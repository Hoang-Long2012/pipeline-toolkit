"""Integration scenarios testing coordination between pipeline-toolkit components."""
import threading

import pytest

from pipeline import (
	Checkpoint,
	Group,
	Pipeline,
	chain,
	compose,
	flow,
	mut,
	pipe,
	repeat,
	step,
	tap,
)
from pipeline.error import ErrorContext
from pipeline.stack import Stack, StackOverflowError, StackUnderflowError


class TestETLDataIngestionScenario:
	"""Scenario 1: Async ETL pipeline coordinating Pipeline, pipe, step, tap, mut, and Stack."""

	def test_etl_data_ingestion_and_side_effects(self):
		"""Test an ETL pipeline where tap audits, mut enriches, and Stack collects results."""
		audit_records = []
		destination_storage = Stack(maxsize=10)

		# 1. Component: pipe decorator for creating parameterized processing step
		@pipe
		def normalize_text(record, uppercase=False):
			cleaned = dict(record)
			cleaned["name"] = cleaned["name"].strip()
			if uppercase:
				cleaned["name"] = cleaned["name"].upper()
			return cleaned

		# 2. Component: tap ensures audit logging receives an isolated copy
		def audit_sink(record_copy):
			# Attempting mutation in tap must not affect the original data flowing through
			record_copy["audited"] = True
			audit_records.append(record_copy)

		# 3. Component: mut performs explicit, intended in-place mutation
		def enrich_metadata(record, batch_id):
			record["batch_id"] = batch_id
			record["status"] = "PROCESSED"

		# 4. Final step: load into a Stack
		def load_to_stack(record):
			destination_storage.push(record)
			return record["id"]

		pipeline = Pipeline([
			# Normalization step using @pipe factory
			(normalize_text(uppercase=True),),
			# Tap step for telemetry/auditing without mutating pipeline state
			(tap, (audit_sink,)),
			# In-place enrichment with mut
			(mut, (enrich_metadata, "BATCH-2026"), {}),
			# Storage load step
			(load_to_stack,),
		])

		raw_input = {
			"id": 101,
			"name": "   john doe   ",
			"score": 85,
		}

		pipeline.run(raw_input).wait()

		# Verify pipeline outcome
		assert pipeline.result == 101
		assert not pipeline.running
		assert len(pipeline.results) == 5  # default + 4 steps
		assert len(pipeline.errors) == 0

		# Verify Stack received the processed item
		assert len(destination_storage) == 1
		stored = destination_storage.peek()
		assert stored["id"] == 101
		assert stored["name"] == "JOHN DOE"
		assert stored["batch_id"] == "BATCH-2026"
		assert stored["status"] == "PROCESSED"
		# tap did not leak its mutation to stored data
		assert "audited" not in stored

		# Verify tap received its isolated deep copy
		assert len(audit_records) == 1
		assert audit_records[0]["audited"] is True


class TestMultiPipelineCoordinationScenario:
	"""Scenario 2: Multi-stage pipeline coordination using Checkpoint and Group."""

	def test_checkpoint_synchronization_between_pipelines(self):
		"""Test producer and consumer pipelines synchronizing at a Checkpoint."""
		checkpoint = Checkpoint()
		producer_finished = threading.Event()
		consumer_finished = threading.Event()
		execution_order = []

		def producer_fetch(initial):
			execution_order.append("producer_start")
			return {"batch": initial, "raw_data": [10, 20, 30]}

		def producer_cleanse(data):
			execution_order.append("producer_cleanse")
			data["cleaned"] = [x * 2 for x in data["raw_data"]]
			return data

		def producer_finalize(data):
			execution_order.append("producer_finalize")
			producer_finished.set()
			return "producer_complete"

		def consumer_process(checkpoint_val):
			execution_order.append("consumer_process")
			# Consumer aggregates the intermediate data released by checkpoint
			total = sum(checkpoint_val["cleaned"])
			consumer_finished.set()
			return {"total": total}

		# Producer pipeline halts at the Checkpoint
		producer = Pipeline([
			(producer_fetch,),
			(producer_cleanse,),
			(checkpoint,),  # Halts here until checkpoint.next() is invoked
			(producer_finalize,),
		])

		consumer = Pipeline([
			(consumer_process,),
		])

		# Run producer asynchronously
		producer.run(1)

		# Wait until checkpoint is active
		checkpoint.wait()
		assert checkpoint.is_active
		assert "producer_cleanse" in execution_order
		assert "producer_finalize" not in execution_order

		# Extract the published checkpoint value and trigger consumer
		intermediate_value = checkpoint.value
		assert intermediate_value["cleaned"] == [20, 40, 60]

		consumer.run(intermediate_value)
		assert consumer_finished.wait(timeout=2.0)
		consumer.wait()
		assert consumer.result == {"total": 120}

		# Now release the producer to finish its remaining steps
		checkpoint.next()
		assert producer_finished.wait(timeout=2.0)
		producer.wait()

		assert producer.result == "producer_complete"
		assert execution_order == [
			"producer_start",
			"producer_cleanse",
			"consumer_process",
			"producer_finalize",
		]

	def test_group_concurrent_execution_with_checkpoint(self):
		"""Test a Group of pipelines coordinating concurrently via a shared Checkpoint."""
		checkpoint = Checkpoint()
		sync_record = []

		def stage1_work(val):
			return val + 10

		def stage2_work(val):
			sync_record.append(f"sync_val_{val}")
			return val * 3

		p1 = Pipeline([
			(stage1_work,),
			(checkpoint,),
			(stage2_work,),
		])

		p2 = Pipeline([
			(lambda x: x + 100,),
		])

		group = Group([p1, p2])
		group.run(5)

		# p2 runs to completion while p1 pauses at checkpoint
		checkpoint.wait()
		assert checkpoint.value == 15
		assert p1.running
		p2.wait()
		assert p2.result == 105

		# Release checkpoint
		checkpoint.next()
		group.wait()

		assert not p1.running
		assert not p2.running
		assert p1.result == 45
		assert sync_record == ["sync_val_15"]


class TestResilientProcessingScenario:
	"""Scenario 3: Resilient batch processing with error handling, dead-letter Stack, and mut."""

	def test_fault_tolerant_pipeline_with_error_handler_and_recovery(self):
		"""Test resilient processing where failed steps are recorded in dead-letter stack while flow recovers."""
		dead_letter_stack = Stack(maxsize=5)

		def record_failure_in_dead_letter(context: ErrorContext):
			dead_letter_stack.push({
				"step_index": context.index,
				"error_message": str(context.error),
				"failed_step": context.step,
				"payload": dict(context.previous_result),
			})

		def validate_transaction(tx):
			if tx["amount"] <= 0:
				raise ValueError("Amount must be positive")
			return tx

		def risky_payment_gateway(tx):
			# Transient error occurs during external gateway call
			raise ConnectionError("Gateway timeout: 504")

		def fallback_and_compensate(tx):
			# When previous step fails and stop_on_error=False,
			# previous valid result is passed to the next step
			def mark_pending(data):
				data["status"] = "QUEUED_FOR_RETRY"
				data["retry_count"] = data.get("retry_count", 0) + 1

			return mut(tx, mark_pending)

		def audit_notification(tx):
			tx["notified"] = True
			return tx

		pipeline = Pipeline([
			(validate_transaction,),
			(risky_payment_gateway,),
			(fallback_and_compensate,),
			(audit_notification,),
		])

		transaction = {"tx_id": "TX-999", "amount": 250, "status": "INIT"}

		# Run with stop_on_error=False and custom error handler
		pipeline.run(
			transaction,
			stop_on_error=False,
			error_handler=record_failure_in_dead_letter,
		).wait()

		# Verify pipeline did not crash and processed the fallback
		assert pipeline.result is not None
		assert pipeline.result["status"] == "QUEUED_FOR_RETRY"
		assert pipeline.result["retry_count"] == 1
		assert pipeline.result["notified"] is True

		# Verify error was tracked on the pipeline
		assert len(pipeline.errors) == 1
		assert isinstance(pipeline.error(reraise=False), ConnectionError)
		with pytest.raises(ConnectionError, match="Gateway timeout: 504"):
			pipeline.error()

		# Verify dead letter stack captured the ErrorContext details
		assert len(dead_letter_stack) == 1
		failed_context = dead_letter_stack.pop()
		assert failed_context["step_index"] == 2
		assert "Gateway timeout: 504" in failed_context["error_message"]
		assert failed_context["payload"]["tx_id"] == "TX-999"


class TestDynamicAdaptivePipelineScenario:
	"""Scenario 4: Adaptive pipeline modification and rerun reflecting mutable and editable design."""

	def test_adaptive_pipeline_inspection_mutation_and_rerun(self):
		"""Test inspecting intermediate results, dynamically injecting steps, and rerunning."""
		def base_compress(payload):
			# Compresses data by 50%
			payload["size"] = payload["size"] * 0.5
			return payload

		def extra_optimization_pass(payload, factor):
			payload["size"] = payload["size"] * factor
			return payload

		pipeline = Pipeline([
			(base_compress,),
		])

		data = {"filename": "document.pdf", "size": 1000}
		pipeline.run(data).wait()

		assert pipeline.result["size"] == 500

		# Condition: if result size > target (300), edit pipeline by inserting additional passes
		if pipeline.result["size"] > 300:
			# Use repeat to generate multiple optimization steps and insert into the existing pipeline
			extra_steps = list(repeat(2, extra_optimization_pass, 0.7))
			for idx, extra in enumerate(extra_steps):
				# Pipeline step is a tuple of (function, args)
				pipeline.insert(1 + idx, (extra, ()))

		assert len(pipeline) == 3

		# Rerun pipeline from scratch with original data
		fresh_data = {"filename": "document.pdf", "size": 1000}
		pipeline.rerun(fresh_data).wait()

		# Size: 1000 * 0.5 = 500; 500 * 0.7 = 350; 350 * 0.7 = 245
		assert pytest.approx(pipeline.result["size"]) == 245

	def test_dynamic_step_skipping_in_flight(self):
		"""Test skipping an expensive or unnecessary step while pipeline is in-flight."""
		step1_started = threading.Event()
		step1_proceed = threading.Event()
		step2_executed = []

		def step1(x):
			step1_started.set()
			step1_proceed.wait(timeout=2.0)
			return x + 10

		def expensive_step2(x):
			step2_executed.append(True)
			return x * 100

		def step3(x):
			return x + 5

		pipeline = Pipeline([
			(step1,),
			(expensive_step2,),
			(step3,),
		])

		pipeline.run(10)
		assert step1_started.wait(timeout=2.0)

		# While step 1 is executing, trigger skip for step 2
		pipeline.skip()
		step1_proceed.set()

		pipeline.wait()

		# step2 was skipped! Value is: 10 + 10 = 20, step2 skipped (still 20), step3 adds 5 -> 25
		assert pipeline.result == 25
		assert step2_executed == []


class TestScatterGatherAggregationScenario:
	"""Scenario 5: Concurrent scatter-gather and hierarchical Group execution with chain and flow."""

	def test_scatter_gather_with_group_chain_and_flow(self):
		"""Test scattering data to a Group of worker pipelines using chain and flow, then aggregating."""
		# Sub-transformation helper using flow
		def filter_and_scale_stream(numbers):
			def is_even(n):
				return n % 2 == 0

			def square(n):
				return n * n

			# Chain filters and transformations on each item
			stream_transforms = [
				lambda nums: [n for n in nums if is_even(n)],
				lambda evens: [square(n) for n in evens],
			]
			# Use flow to yield intermediate stages and take the final stage
			stages = list(flow(stream_transforms, data=numbers))
			return stages[-1]

		def summarize_batch(scaled_numbers):
			return {
				"count": len(scaled_numbers),
				"sum": sum(scaled_numbers),
			}

		# Master dataset
		shards = [
			[1, 2, 3, 4, 5, 6],
			[7, 8, 9, 10, 11, 12],
			[13, 14, 15, 16, 17, 18],
		]

		# Create a pipeline worker for each shard
		workers = []
		for shard in shards:
			worker = Pipeline(
				[
					# Step using chain to integrate callable sequences
					(lambda s: chain([(filter_and_scale_stream,)], default=s),),
					(summarize_batch,),
				],
				default=shard,
			)
			workers.append(worker)

		# Group coordinates concurrent execution across all worker pipelines
		worker_group = Group(workers)
		assert len(worker_group) == 3

		# Run all workers in parallel
		worker_group.run().wait()

		# Gather and aggregate results
		total_count = sum(p.result["count"] for p in worker_group)
		total_sum = sum(p.result["sum"] for p in worker_group)

		# Shard 1 evens: [2, 4, 6] -> squares: [4, 16, 36] -> sum: 56, count: 3
		# Shard 2 evens: [8, 10, 12] -> squares: [64, 100, 144] -> sum: 308, count: 3
		# Shard 3 evens: [14, 16, 18] -> squares: [196, 256, 324] -> sum: 776, count: 3
		assert total_count == 9
		assert total_sum == 56 + 308 + 776

	def test_nested_group_hierarchical_execution(self):
		"""Test nested Group hierarchy execution and control."""
		def increment(x):
			return x + 1

		subgroup_a = Group([
			Pipeline([(increment,)]),
			Pipeline([(increment,)]),
		])
		subgroup_b = Group([
			Pipeline([(increment,)]),
			Pipeline([(increment,)]),
		])

		master_group = Group([subgroup_a, subgroup_b])
		assert len(master_group) == 2

		# Run entire hierarchy with default value 10
		master_group.run(10).wait()

		# Verify all leaf pipelines completed
		for subgroup in master_group:
			for pipeline in subgroup:
				assert pipeline.result == 11
				assert not pipeline.running


class TestFunctionalCompositionScenario:
	"""Scenario 6: Functional composition mixing pipe, step, compose, repeat, and Pipeline."""

	def test_functional_pipeline_composition(self):
		"""Test integrating pipe, step operators (* and |), compose, and repeat inside a Pipeline."""
		@pipe
		def add(value, amount):
			return value + amount

		@pipe
		def multiply(value, factor):
			return value * factor

		# Component: step default and multiplication operator for repeated evaluation
		inc = add(1)
		inc.default = 10
		assert (inc * 3) == 13

		# Component: step exponentiation creates multiple step instances
		multipliers = multiply(2) ** 2
		assert len(multipliers) == 2

		# Component: functional composition using compose
		# Composes (+ 3) with (* 2)
		composed_operation = compose([
			add(3),
			multiply(2),
		])

		# Component: step instance creation directly with arguments
		subtract_step = step(lambda val, sub: val - sub, 4)
		assert subtract_step(14) == 10

		# Component: pipe operator (|) works directly on values
		test_piped_val = 5 | multiply(3)
		assert test_piped_val == 15

		# Put composed operations, exponentiated steps, and step objects inside an asynchronous Pipeline
		pipeline = Pipeline([
			(composed_operation,),
			# Repeated step instances created via step ** 2
			*((m,) for m in multipliers),
			(subtract_step,),
		])

		# Flow:
		# Initial: 10
		# composed_operation: (10 + 3) * 2 = 26
		# multipliers step 1: 26 * 2 = 52
		# multipliers step 2: 52 * 2 = 104
		# subtract_step: 104 - 4 = 100
		pipeline.run(10).wait()

		assert pipeline.result == 100
		assert len(pipeline) == 4


class TestStackPipelineIntegrationScenario:
	"""Scenario 7: Stack as bounded queue and state synchronizer with Pipeline."""

	def test_stack_as_bounded_buffer_between_pipeline_invocations(self):
		"""Test using Stack with maxsize for bounded result storage and underflow/overflow handling."""
		buffer = Stack(maxsize=2)

		pipeline = Pipeline([
			(lambda x: x * 10,),
			(lambda x: buffer.push(x),),
		])

		# Run 1: buffer has 1 item
		pipeline.run(1).wait()
		assert len(buffer) == 1
		assert buffer.peek() == 10

		# Run 2: buffer has 2 items (full)
		pipeline.run(2).wait()
		assert len(buffer) == 2
		assert buffer.full()
		assert buffer.peek() == 20

		# Run 3: buffer overflow caught by the pipeline
		pipeline.run(3).wait()
		assert len(pipeline.errors) == 1
		assert isinstance(pipeline.error(reraise=False), StackOverflowError)
		with pytest.raises(StackOverflowError):
			pipeline.error()

		# Drain buffer LIFO
		assert buffer.pop() == 20
		assert buffer.pop() == 10
		assert buffer.empty()

		with pytest.raises(StackUnderflowError):
			buffer.pop()
