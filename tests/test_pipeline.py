"""Tests for the Pipeline class."""

import copy
import threading
import time

import pytest

from pipeline import Pipeline


class TestPipelineInitialization:
	"""Test Pipeline initialization."""

	def test_pipeline_init_empty(self):
		"""Test initializing empty pipeline."""
		pipeline = Pipeline()
		assert len(pipeline) == 0
		assert pipeline.default is None
		assert pipeline.step == 0
		assert not pipeline.running

	def test_pipeline_init_with_steps(self):
		"""Test initializing pipeline with steps."""

		def add(x, y):
			return x + y

		pipeline = Pipeline([
			(add, (5,)),
			(add, (10,)),
		])
		assert len(pipeline) == 2
		assert pipeline.step == 0

	def test_pipeline_init_with_default(self):
		"""Test initializing pipeline with default value."""
		pipeline = Pipeline(default=42)
		assert pipeline.default == 42

	def test_pipeline_init_with_run_now(self):
		"""Test initializing and immediately running the pipeline."""

		def add(x, y):
			return x + y

		pipeline = Pipeline(
			[(add, (5,))],
			run_now=True,
			run_args=(10,),
		)
		pipeline.wait()

		assert pipeline.result == 15

	def test_pipeline_init_run_now_uses_default(self):
		"""Test run_now uses the pipeline default when run_args is empty."""

		def add(x, y):
			return x + y

		pipeline = Pipeline(
			[(add, (5,))],
			default=10,
			run_now=True,
		)
		pipeline.wait()

		assert pipeline.result == 15

	def test_pipeline_init_run_now_invalid_run_args(self):
		"""Test run_now with non-tuple run_args raises TypeError."""

		with pytest.raises(TypeError, match="run_args is not a tuple"):
			Pipeline(run_now=True, run_args=[10])

	def test_pipeline_init_invalid_step(self):
		"""Test initializing pipeline with invalid step raises TypeError."""
		with pytest.raises(TypeError, match="Invalid step format"):
			Pipeline(["not_a_tuple"])

	def test_pipeline_init_non_callable_step(self):
		"""Test initializing pipeline with non-callable step raises TypeError."""
		with pytest.raises(TypeError, match="Invalid step format"):
			Pipeline([("not_callable",)])


class TestPipelineStepFormats:
	"""Test different step formats."""

	def test_step_callable_only(self):
		"""Test step with callable only."""
		pipeline = Pipeline([(str.upper,)])
		pipeline.run("hello").wait()
		assert pipeline.results.get() == "HELLO"

	def test_step_with_positional_args(self):
		"""Test step with positional arguments."""

		def add(x, y):
			return x + y

		pipeline = Pipeline([(add, (5,))])
		pipeline.run(10).wait()
		assert pipeline.results.get() == 15

	def test_step_with_keyword_args(self):
		"""Test step with keyword arguments."""

		def power(x, exp=2):
			return x**exp

		pipeline = Pipeline([(power, {"exp": 3})])
		pipeline.run(2).wait()
		assert pipeline.results.get() == 8

	def test_step_with_args_and_kwargs(self):
		"""Test step with both positional and keyword arguments."""

		def func(x, a, b=10):
			return x + a + b

		pipeline = Pipeline([(func, (5,), {"b": 20})])
		pipeline.run(10).wait()
		assert pipeline.results.get() == 35

	def test_invalid_three_part_step_with_mapping_args(self):
		"""Test three-part step requires tuple positional arguments."""

		def func(x):
			return x

		pipeline = Pipeline()

		with pytest.raises(TypeError, match="Invalid step format"):
			pipeline.execute((func, {"x": 1}, {"y": 2}), 10)


class TestPipelineExecution:
	"""Test pipeline execution."""

	def test_run_basic(self):
		"""Test basic pipeline run."""

		def add(x, y):
			return x + y

		pipeline = Pipeline([(add, (5,))])
		pipeline.run(10)
		pipeline.wait()
		assert pipeline.results.get() == 15

	def test_run_returns_pipeline(self):
		"""Test that run returns the pipeline instance."""
		pipeline = Pipeline()
		result = pipeline.run()
		assert result is pipeline

	def test_run_multiple_steps(self):
		"""Test running pipeline with multiple steps."""

		def add(x, y):
			return x + y

		def multiply(x, y):
			return x * y

		pipeline = Pipeline([
			(add, (5,)),
			(multiply, (2,)),
		])
		pipeline.run(10).wait()
		assert pipeline.results.get() == 30

	def test_wait_returns_pipeline(self):
		"""Test that wait returns the pipeline instance."""
		pipeline = Pipeline()
		pipeline.run()
		result = pipeline.wait()
		assert result is pipeline

	def test_running_property(self):
		"""Test running property during and after execution."""

		def quick_func(x):
			return x

		pipeline = Pipeline([(quick_func,)])
		assert not pipeline.running
		pipeline.run(10)
		pipeline.wait()
		assert not pipeline.running


class TestPipelineStop:
	"""Test pipeline stop functionality."""

	def test_stop_when_not_running(self):
		"""Test stop when pipeline is not running returns 0."""
		pipeline = Pipeline()
		result = pipeline.stop()
		assert result == 0

	def test_stop_during_delay_cancellation_window(self):
		"""Test stopping during initial delay returns 0."""

		def func(x):
			return x

		pipeline = Pipeline([(func,)])
		pipeline.run(10, delay=1.0)
		stopped_step = pipeline.stop()
		assert stopped_step == 0

	def test_stop_after_execution_completes(self):
		"""Test stop after pipeline has finished returns 0."""

		def func(x):
			return x

		pipeline = Pipeline([(func,)])
		pipeline.run(10).wait()
		result = pipeline.stop()
		assert result == 0


class TestPipelineSkip:
	"""Test pipeline skip functionality."""

	def test_skip_returns_pipeline(self):
		"""Test that skip returns the pipeline instance."""
		pipeline = Pipeline()
		result = pipeline.skip()
		assert result is pipeline

	def test_skip_execution(self):
		"""Test that skip actually skips a step during execution."""
		ready_to_skip = threading.Event()
		proceed_from_skip = threading.Event()

		def step1_func(x):
			ready_to_skip.set()
			proceed_from_skip.wait()
			return x + 1

		def step2_func(x):
			return x + 10

		def step3_func(x):
			return x + 100

		pipeline = Pipeline([
			(step1_func,),
			(step2_func,),
			(step3_func,),
		])
		pipeline.run(0)

		assert ready_to_skip.wait(timeout=1.0), (
			"Step 1 never reached sync point"
		)

		pipeline.skip()
		proceed_from_skip.set()

		pipeline.wait()

		assert pipeline.results.get() == 101


class TestPipelineRerun:
	"""Test pipeline rerun functionality."""

	def test_rerun_after_completion_with_new_value(self):
		"""Test rerun after pipeline has completed restarts with new value."""

		def add(x, y):
			return x + y

		pipeline = Pipeline([(add, (5,))])
		pipeline.run(10).wait()

		first_result = pipeline.results.get()
		assert first_result == 15

		pipeline.rerun(20).wait()
		assert pipeline.results.get() == 25

	def test_rerun_while_running(self):
		"""Test rerun stops and restarts while first run is executing."""
		first_run_started = threading.Event()

		pipeline = None

		def slow_func(x):
			first_run_started.set()

			if x == 10:
				pipeline.stop_event.wait()

			return x + 5

		pipeline = Pipeline([(slow_func,)])

		pipeline.run(10)

		assert first_run_started.wait(timeout=1.0), (
			"First run never started"
		)

		pipeline.rerun(20).wait()

		assert pipeline.results.get() == 25

	def test_rerun_returns_pipeline(self):
		"""Test that rerun returns the pipeline instance."""
		pipeline = Pipeline()
		pipeline.run()
		result = pipeline.rerun(10)
		assert result is pipeline
		pipeline.wait()


class TestPipelineResults:
	"""Test pipeline results stack and result property."""

	def test_results_contains_initial_value(self):
		"""Test that results contains initial value."""
		pipeline = Pipeline()
		pipeline.run(42)
		pipeline.wait()
		assert pipeline.results.get() == 42

	def test_results_contains_step_results(self):
		"""Test that results contains all intermediate results."""

		def add(x, y):
			return x + y

		pipeline = Pipeline([
			(add, (5,)),
			(add, (10,)),
		])
		pipeline.run(10).wait()

		results = list(pipeline.results)
		assert results == [25, 15, 10]

	def test_results_stack_lifo(self):
		"""Test results follow LIFO order."""

		def add(x, y):
			return x + y

		pipeline = Pipeline([
			(add, (5,)),
			(add, (10,)),
		])
		pipeline.run(10).wait()

		assert pipeline.results.get() == 25
		assert pipeline.results.pop() == 25
		assert pipeline.results.get() == 15

	def test_result_returns_latest_result(self):
		"""Test result property returns the latest result."""

		def add(x, y):
			return x + y

		pipeline = Pipeline([(add, (5,))])
		pipeline.run(10).wait()

		assert pipeline.result == 15

	def test_result_returns_initial_value_without_successful_step(self):
		"""Test result returns initial value when no step succeeds."""

		def raise_error(x):
			raise ValueError("Error")

		pipeline = Pipeline([(raise_error,)])
		pipeline.run(42).wait()

		assert pipeline.result == 42

	def test_result_is_none_before_first_run(self):
		"""Test result is None before the pipeline has run."""
		pipeline = Pipeline()
		assert pipeline.result is None

	def test_result_raises_while_running(self):
		"""Test result raises RuntimeError while pipeline is running."""
		step_started = threading.Event()
		step_should_exit = threading.Event()

		def slow_func(x):
			step_started.set()
			step_should_exit.wait(timeout=1.0)
			return x

		pipeline = Pipeline([(slow_func,)])
		pipeline.run(10)

		assert step_started.wait(timeout=1.0)

		with pytest.raises(RuntimeError, match="Pipeline is already running"):
			_ = pipeline.result

		step_should_exit.set()
		pipeline.wait()


class TestPipelineErrors:
	"""Test pipeline error handling."""

	def test_errors_stack_on_exception(self):
		"""Test errors are stored in errors stack."""

		def raise_error(x):
			raise ValueError("Test error")

		pipeline = Pipeline([(raise_error,)])
		pipeline.run(10).wait()

		assert len(pipeline.errors) == 1
		assert isinstance(pipeline.errors.get(), ValueError)

	def test_stop_on_error_true(self):
		"""Test that pipeline stops on first error when stop_on_error=True."""

		def raise_error(x):
			raise ValueError("Error")

		def add(x, y):
			return x + y

		pipeline = Pipeline([
			(raise_error,),
			(add, (5,)),
		])
		pipeline.run(10, stop_on_error=True).wait()

		assert len(pipeline.errors) == 1
		assert pipeline.step == 0

	def test_stop_on_error_false(self):
		"""Test that pipeline continues on error when stop_on_error=False."""

		def raise_error(x):
			raise ValueError("Error")

		def add(x, y):
			return x + y

		pipeline = Pipeline([
			(raise_error,),
			(add, (5,)),
		])
		pipeline.run(10, stop_on_error=False).wait()

		assert len(pipeline.errors) == 1
		assert pipeline.results.get() == 15

	def test_error_raises_latest_exception(self):
		"""Test error property raises the latest pipeline exception."""

		def raise_error(x):
			raise ValueError("Test error")

		pipeline = Pipeline([(raise_error,)])
		pipeline.run(10).wait()

		with pytest.raises(ValueError, match="Test error"):
			_ = pipeline.error

	def test_error_returns_none_without_exception(self):
		"""Test error property returns None when no exception occurred."""

		def func(x):
			return x

		pipeline = Pipeline([(func,)])
		pipeline.run(10).wait()

		assert pipeline.error is None

	def test_error_raises_while_running(self):
		"""Test error raises RuntimeError while pipeline is running."""
		step_started = threading.Event()
		step_should_exit = threading.Event()

		def slow_func(x):
			step_started.set()
			step_should_exit.wait(timeout=1.0)
			return x

		pipeline = Pipeline([(slow_func,)])
		pipeline.run(10)

		assert step_started.wait(timeout=1.0)

		with pytest.raises(RuntimeError, match="Pipeline is already running"):
			_ = pipeline.error

		step_should_exit.set()
		pipeline.wait()


class TestPipelineManualSteps:
	"""Test manual step execution."""

	def test_run_step_basic(self):
		"""Test running a single step manually."""

		def add(x, y):
			return x + y

		pipeline = Pipeline([(add, (5,))])
		result = pipeline.run_step(1, 10)
		assert result == 15

	def test_run_step_default_is_none(self):
		"""Test run_step uses None as its default value."""
		pipeline = Pipeline([(lambda x: x,)])

		assert pipeline.run_step(1) is None

	def test_run_step_does_not_affect_state(self):
		"""Test run_step doesn't affect pipeline results or errors."""

		def add(x, y):
			return x + y

		pipeline = Pipeline([
			(add, (5,)),
			(add, (10,)),
		])
		result = pipeline.run_step(1, 10)

		assert result == 15
		assert len(pipeline.results) == 0
		assert len(pipeline.errors) == 0

	def test_run_step_invalid_index_type(self):
		"""Test run_step with non-integer index."""
		pipeline = Pipeline()

		with pytest.raises(TypeError, match="Step is not int"):
			pipeline.run_step("1", 10)

	def test_run_step_invalid_index_out_of_range(self):
		"""Test run_step with index beyond pipeline."""
		pipeline = Pipeline()

		with pytest.raises(IndexError, match="Step out of pipeline"):
			pipeline.run_step(1, 10)

	def test_run_step_invalid_index_zero(self):
		"""Test run_step with zero index."""

		def func(x):
			return x

		pipeline = Pipeline([(func,)])

		with pytest.raises(ValueError, match="Step < 1"):
			pipeline.run_step(0, 10)

	def test_run_step_while_running(self):
		"""Test run_step raises error while pipeline is running."""
		step_started = threading.Event()
		step_should_exit = threading.Event()

		def slow_func(x):
			step_started.set()
			step_should_exit.wait(timeout=1.0)
			return x

		pipeline = Pipeline([(slow_func,)])
		pipeline.run(10)

		assert step_started.wait(timeout=1.0), "Pipeline never started"

		with pytest.raises(RuntimeError, match="Pipeline is already running"):
			pipeline.run_step(1, 10)

		step_should_exit.set()
		pipeline.wait()


class TestPipelineExecute:
	"""Test direct synchronous step execution."""

	def test_execute_basic(self):
		"""Test executing a standalone step."""

		def add(x, y):
			return x + y

		pipeline = Pipeline()
		result = pipeline.execute((add, (5,)), 10)

		assert result == 15

	def test_execute_callable_only(self):
		"""Test executing a callable-only step."""

		def identity(x):
			return x

		pipeline = Pipeline()
		assert pipeline.execute((identity,), 42) == 42

	def test_execute_with_keyword_args(self):
		"""Test executing a step with keyword arguments."""

		def power(x, exp=2):
			return x**exp

		pipeline = Pipeline()
		assert pipeline.execute((power, {"exp": 3}), 2) == 8

	def test_execute_with_args_and_kwargs(self):
		"""Test executing a step with positional and keyword arguments."""

		def func(x, a, b=10):
			return x + a + b

		pipeline = Pipeline()
		assert pipeline.execute((func, (5,), {"b": 20}), 10) == 35

	def test_execute_does_not_affect_state(self):
		"""Test execute doesn't affect pipeline results or errors."""

		def add(x, y):
			return x + y

		pipeline = Pipeline([(add, (5,))])
		result = pipeline.execute((add, (10,)), 5)

		assert result == 15
		assert len(pipeline.results) == 0
		assert len(pipeline.errors) == 0

	def test_execute_invalid_step(self):
		"""Test execute validates the supplied step."""

		pipeline = Pipeline()

		with pytest.raises(TypeError, match="Invalid step format"):
			pipeline.execute(("not_callable",), 10)

	def test_execute_while_running(self):
		"""Test execute raises error while pipeline is running."""
		step_started = threading.Event()
		step_should_exit = threading.Event()

		def slow_func(x):
			step_started.set()
			step_should_exit.wait(timeout=1.0)
			return x

		pipeline = Pipeline([(slow_func,)])
		pipeline.run(10)

		assert step_started.wait(timeout=1.0)

		with pytest.raises(RuntimeError, match="Pipeline is already running"):
			pipeline.execute((slow_func,), 10)

		step_should_exit.set()
		pipeline.wait()

	def test_execute_propagates_exception(self):
		"""Test execute propagates exceptions to the caller."""

		def raise_error(x):
			raise ValueError("Test error")

		pipeline = Pipeline()

		with pytest.raises(ValueError, match="Test error"):
			pipeline.execute((raise_error,), 10)


class TestPipelineModification:
	"""Test pipeline step modification."""

	def test_add_step(self):
		"""Test adding a step."""

		def add(x, y):
			return x + y

		pipeline = Pipeline()
		result = pipeline.add((add, (5,)))

		assert result is None
		assert len(pipeline) == 1

	def test_insert_step(self):
		"""Test inserting a step at a position."""

		def add(x, y):
			return x + y

		def multiply(x, y):
			return x * y

		pipeline = Pipeline([
			(add, (5,)),
			(add, (10,)),
		])
		pipeline.insert(2, (multiply, (2,)))

		assert len(pipeline) == 3

	def test_pop_step(self):
		"""Test popping a step."""

		def add(x, y):
			return x + y

		pipeline = Pipeline([
			(add, (5,)),
			(add, (10,)),
		])
		step_tuple = pipeline.pop(1)

		assert step_tuple == (add, (5,))
		assert len(pipeline) == 1

	def test_clear_steps(self):
		"""Test clearing all steps."""

		def add(x, y):
			return x + y

		pipeline = Pipeline([
			(add, (5,)),
			(add, (10,)),
		])
		pipeline.clear()

		assert len(pipeline) == 0

	def test_remove_step(self):
		"""Test removing a matching step."""

		def add(x, y):
			return x + y

		def multiply(x, y):
			return x * y

		step = (add, (5,))
		pipeline = Pipeline([
			step,
			(multiply, (2,)),
		])

		result = pipeline.remove(step)

		assert result is None
		assert len(pipeline) == 1
		assert pipeline[1] == (multiply, (2,))

	def test_remove_missing_step(self):
		"""Test removing a missing step raises ValueError."""

		def add(x, y):
			return x + y

		pipeline = Pipeline()

		with pytest.raises(ValueError, match="Step not found in pipeline"):
			pipeline.remove((add, (5,)))

	def test_discard_existing_step(self):
		"""Test discard removes an existing step."""

		def add(x, y):
			return x + y

		step = (add, (5,))
		pipeline = Pipeline([step])

		result = pipeline.discard(step)

		assert result is None
		assert len(pipeline) == 0

	def test_discard_missing_step(self):
		"""Test discard ignores a missing step."""

		def add(x, y):
			return x + y

		pipeline = Pipeline()

		assert pipeline.discard((add, (5,))) is None
		assert len(pipeline) == 0


class TestPipelineItemAccess:
	"""Test item access and modification."""

	def test_getitem(self):
		"""Test retrieving a step by one-based index."""

		def add(x, y):
			return x + y

		step = (add, (5,))
		pipeline = Pipeline([step])

		assert pipeline[1] == step

	def test_getitem_invalid_index_type(self):
		"""Test getting a step with a non-integer index."""

		pipeline = Pipeline()

		with pytest.raises(TypeError, match="is not int"):
			pipeline["1"]

	def test_getitem_index_out_of_range(self):
		"""Test getting a step with an invalid index."""

		pipeline = Pipeline()

		with pytest.raises(IndexError, match="Index out of range"):
			pipeline[1]

	def test_setitem(self):
		"""Test replacing a step by one-based index."""

		def add(x, y):
			return x + y

		def multiply(x, y):
			return x * y

		pipeline = Pipeline([(add, (5,))])
		new_step = (multiply, (2,))

		result = pipeline.__setitem__(1, new_step)

		assert result is None
		assert pipeline[1] == new_step

	def test_setitem_invalid_index_type(self):
		"""Test setting a step with a non-integer index."""

		pipeline = Pipeline()

		with pytest.raises(TypeError, match="is not int"):
			pipeline["1"] = (str,)

	def test_setitem_index_out_of_range(self):
		"""Test setting a step with an invalid index."""

		pipeline = Pipeline()

		with pytest.raises(IndexError, match="Index out of range"):
			pipeline[1] = (str,)

	def test_setitem_invalid_step(self):
		"""Test setting an invalid step."""

		pipeline = Pipeline([(str,)])

		with pytest.raises(TypeError, match="Invalid step format"):
			pipeline[1] = ("not_callable",)

	def test_delitem(self):
		"""Test deleting a step by one-based index."""

		def add(x, y):
			return x + y

		def multiply(x, y):
			return x * y

		pipeline = Pipeline([
			(add, (5,)),
			(multiply, (2,)),
		])

		del pipeline[1]

		assert len(pipeline) == 1
		assert pipeline[1] == (multiply, (2,))

	def test_delitem_invalid_index_type(self):
		"""Test deleting a step with a non-integer index."""

		pipeline = Pipeline()

		with pytest.raises(TypeError, match="is not int"):
			del pipeline["1"]

	def test_delitem_index_out_of_range(self):
		"""Test deleting a step with an invalid index."""

		pipeline = Pipeline()

		with pytest.raises(IndexError, match="Index out of range"):
			del pipeline[1]


class TestPipelineContextManager:
	"""Test pipeline context manager."""

	def test_context_manager_starts_pipeline_if_not_running(self):
		"""Test entering context starts pipeline if not already running."""
		step_executed = threading.Event()

		def mark_executed(x):
			step_executed.set()
			return x

		pipeline = Pipeline([(mark_executed,)], default=42)
		assert not pipeline.running

		with pipeline:
			assert step_executed.wait(timeout=1.0), (
				"Pipeline never executed"
			)

		assert not pipeline.running
		assert pipeline.results.get() == 42

	def test_context_manager_does_not_restart_already_running(self):
		"""Test context manager doesn't restart an already-running pipeline."""
		step_started = threading.Event()

		pipeline = None

		def slow_func(x):
			step_started.set()
			pipeline.stop_event.wait()
			return x + 5

		pipeline = Pipeline([(slow_func,)])

		pipeline.run(10)

		assert step_started.wait(timeout=1.0), "Pipeline never started"

		with pipeline:
			assert pipeline.running

		assert not pipeline.running

	def test_context_manager_exit_calls_stop(self):
		"""Test that exiting context calls stop()."""
		step_started = threading.Event()
		step_should_exit = threading.Event()

		def slow_func(x):
			step_started.set()
			step_should_exit.wait(timeout=1.0)
			return x

		pipeline = Pipeline([(slow_func,)], default=10)

		with pipeline:
			assert step_started.wait(timeout=1.0), (
				"Pipeline never started"
			)

		assert not pipeline.running

		step_should_exit.set()


class TestPipelineCopy:
	"""Test pipeline copying behavior."""

	def test_copy_returns_pipeline(self):
		"""Test copy returns a new pipeline instance."""

		def add(x, y):
			return x + y

		pipeline = Pipeline([(add, (5,))], default=10)
		copied = pipeline.copy()

		assert isinstance(copied, Pipeline)
		assert copied is not pipeline

	def test_copy_copies_configuration_shallowly(self):
		"""Test copy creates a shallow copy of the pipeline configuration."""

		def add(x, y):
			return x + y

		args = ([5],)
		pipeline = Pipeline([(add, args)], default={"value": 10})
		copied = pipeline.copy()

		assert copied.pipeline is not pipeline.pipeline
		assert copied.pipeline == pipeline.pipeline
		assert copied.pipeline[0] is pipeline.pipeline[0]
		assert copied.pipeline[0][1] is args
		assert copied.default is not pipeline.default
		assert copied.default == pipeline.default

	def test_copy_resets_execution_state(self):
		"""Test copy does not copy execution state."""

		def add(x, y):
			return x + y

		pipeline = Pipeline([(add, (5,))])
		pipeline.run(10).wait()

		copied = pipeline.copy()

		assert copied.step == 0
		assert not copied.running
		assert len(copied.results) == 0
		assert len(copied.errors) == 0
		assert copied.thread is None

	def test_copy_method_matches_copy_protocol(self):
		"""Test copy method returns the same result as copy.copy."""

		def add(x, y):
			return x + y

		pipeline = Pipeline([(add, (5,))], default=10)

		copied = pipeline.copy()
		protocol_copy = copy.copy(pipeline)

		assert copied.pipeline == protocol_copy.pipeline
		assert copied.default == protocol_copy.default
		assert copied is not protocol_copy

	def test_copy_while_running_raises(self):
		"""Test copying a running pipeline raises RuntimeError."""
		step_started = threading.Event()
		step_should_exit = threading.Event()

		def slow_func(x):
			step_started.set()
			step_should_exit.wait(timeout=1.0)
			return x

		pipeline = Pipeline([(slow_func,)])
		pipeline.run(10)

		assert step_started.wait(timeout=1.0)

		with pytest.raises(RuntimeError, match="Pipeline is already running"):
			pipeline.copy()

		with pytest.raises(RuntimeError, match="Pipeline is already running"):
			copy.copy(pipeline)

		step_should_exit.set()
		pipeline.wait()

	def test_deepcopy_returns_pipeline(self):
		"""Test deepcopy returns a new pipeline instance."""

		def add(x, y):
			return x + y

		pipeline = Pipeline([(add, (5,))], default={"value": 10})
		copied = copy.deepcopy(pipeline)

		assert isinstance(copied, Pipeline)
		assert copied is not pipeline

	def test_deepcopy_copies_configuration_deeply(self):
		"""Test deepcopy creates an independent copy of the configuration."""

		def add(x, values):
			values.append(x)
			return values

		args = ([5],)
		default = {"values": [10]}
		pipeline = Pipeline([(add, args)], default=default)

		copied = copy.deepcopy(pipeline)

		assert copied.pipeline is not pipeline.pipeline
		assert copied.pipeline[0] is not pipeline.pipeline[0]
		assert copied.pipeline[0][1] is not pipeline.pipeline[0][1]
		assert copied.pipeline[0][1][0] is not pipeline.pipeline[0][1][0]
		assert copied.default is not pipeline.default
		assert copied.default["values"] is not pipeline.default["values"]

	def test_deepcopy_resets_execution_state(self):
		"""Test deepcopy does not copy execution state."""

		def add(x, y):
			return x + y

		pipeline = Pipeline([(add, (5,))])
		pipeline.run(10).wait()

		copied = copy.deepcopy(pipeline)

		assert copied.step == 0
		assert not copied.running
		assert len(copied.results) == 0
		assert len(copied.errors) == 0
		assert copied.thread is None

	def test_deepcopy_is_independent(self):
		"""Test modifying a deep copy does not affect the original pipeline."""

		def add(x, y):
			return x + y

		args = ([5],)
		default = {"value": [10]}
		pipeline = Pipeline([(add, args)], default=default)
		copied = copy.deepcopy(pipeline)

		copied.pipeline[0][1][0].append(15)
		copied.default["value"].append(20)

		assert pipeline.pipeline[0][1] == ([5],)
		assert pipeline.default == {"value": [10]}

	def test_deepcopy_while_running_raises(self):
		"""Test deep copying a running pipeline raises RuntimeError."""
		step_started = threading.Event()
		step_should_exit = threading.Event()

		def slow_func(x):
			step_started.set()
			step_should_exit.wait(timeout=1.0)
			return x

		pipeline = Pipeline([(slow_func,)])
		pipeline.run(10)

		assert step_started.wait(timeout=1.0)

		with pytest.raises(RuntimeError, match="Pipeline is already running"):
			copy.deepcopy(pipeline)

		step_should_exit.set()
		pipeline.wait()


class TestPipelineCallable:
	"""Test pipeline callable interface."""

	def test_pipeline_call_equivalent_to_run(self):
		"""Test calling pipeline is equivalent to calling run."""

		def add(x, y):
			return x + y

		pipeline = Pipeline([(add, (5,))])
		pipeline(10)
		pipeline.wait()

		assert pipeline.results.get() == 15

	def test_pipeline_bool_reflects_running_state(self):
		"""Test pipeline bool reflects running state."""
		pipeline = Pipeline()
		assert not bool(pipeline)

		pipeline.run(10)
		pipeline.wait()

		assert not bool(pipeline)

	def test_pipeline_contains_callable(self):
		"""Test checking if callable is in pipeline."""

		def add(x, y):
			return x + y

		def multiply(x, y):
			return x * y

		pipeline = Pipeline([(add, (5,))])

		assert add in pipeline
		assert multiply not in pipeline

	def test_pipeline_len(self):
		"""Test pipeline length."""

		def add(x, y):
			return x + y

		pipeline = Pipeline([
			(add, (5,)),
			(add, (10,)),
		])

		assert len(pipeline) == 2

	def test_pipeline_iter(self):
		"""Test iterating over pipeline steps."""

		def add(x, y):
			return x + y

		def multiply(x, y):
			return x * y

		steps = [
			(add, (5,)),
			(multiply, (2,)),
		]
		pipeline = Pipeline(steps)

		assert list(pipeline) == steps

	def test_pipeline_str_representation(self):
		"""Test pipeline string representation."""

		def add(x, y):
			return x + y

		pipeline = Pipeline([(add, (5,))])

		assert str(pipeline) == "add(5)"

	def test_pipeline_str_multiple_steps(self):
		"""Test pipeline string with multiple steps."""

		def add(x, y):
			return x + y

		def multiply(x, y):
			return x * y

		pipeline = Pipeline([
			(add, (5,)),
			(multiply, (2,)),
		])

		assert str(pipeline) == "add(5) | multiply(2)"

	def test_pipeline_repr(self):
		"""Test pipeline repr."""
		pipeline = Pipeline()
		repr_str = repr(pipeline)

		assert "Pipeline" in repr_str
		assert "total_steps=0" in repr_str


class TestPipelineDelay:
	"""Test pipeline execution delays."""

	def test_run_with_delay_waits_before_execution(self):
		"""Test that delay parameter adds wait time."""

		def func(x):
			return x

		pipeline = Pipeline([(func,)])
		start = time.monotonic()

		pipeline.run(10, delay=0.1).wait()

		elapsed = time.monotonic() - start
		assert elapsed >= 0.09

	def test_run_delay_cancellation_before_first_step(self):
		"""Test delay provides cancellation window before first step."""

		def func(x):
			return x

		pipeline = Pipeline([(func,)])
		pipeline.run(10, delay=0.5)

		stopped_step = pipeline.stop()

		assert stopped_step == 0


class TestPipelineThreading:
	"""Test pipeline threading behavior."""

	def test_daemon_thread_parameter(self):
		"""Test daemon parameter sets thread daemon flag correctly."""
		step_started = threading.Event()
		step_should_exit = threading.Event()

		def slow_func(x):
			step_started.set()
			step_should_exit.wait(timeout=1.0)
			return x

		pipeline = Pipeline([(slow_func,)])
		pipeline.run(10, daemon=True)

		assert step_started.wait(timeout=1.0), "Thread never started"
		assert pipeline.thread is not None
		assert pipeline.thread.daemon is True

		step_should_exit.set()
		pipeline.wait()

	def test_multiple_runs_not_allowed(self):
		"""Test that multiple concurrent runs are not allowed."""
		step_started = threading.Event()
		step_should_exit = threading.Event()

		def slow_func(x):
			step_started.set()
			step_should_exit.wait(timeout=1.0)
			return x

		pipeline = Pipeline([(slow_func,)])
		pipeline.run(10)

		assert step_started.wait(timeout=1.0), "First run never started"

		with pytest.raises(RuntimeError, match="Pipeline is already running"):
			pipeline.run(20)

		step_should_exit.set()
		pipeline.wait()


class TestPipelineEdgeCases:
	"""Test pipeline edge cases."""

	def test_none_as_explicit_default(self):
		"""Test passing None explicitly as default overrides pipeline default."""

		def func(x):
			return x if x is not None else 0

		pipeline = Pipeline([(func,)], default=42)
		pipeline.run(None).wait()

		assert pipeline.results.get() == 0

	def test_empty_pipeline_execution(self):
		"""Test executing empty pipeline."""
		pipeline = Pipeline()
		pipeline.run(42).wait()

		assert pipeline.results.get() == 42
		assert pipeline.step == 0

	def test_pipeline_snapshot_at_run_time(self):
		"""Test that pipeline is snapshotted when run() is called."""

		def add(x, y):
			return x + y

		pipeline = Pipeline([(add, (5,))])
		pipeline.run(10)

		pipeline.clear()
		pipeline.wait()

		assert pipeline.results.get() == 15


class TestPipelineInvalidParameters:
	"""Test pipeline with invalid parameters."""

	def test_run_invalid_delay_type(self):
		"""Test run with non-numeric delay."""
		pipeline = Pipeline()

		with pytest.raises(TypeError, match="Delay is not int or float"):
			pipeline.run(10, delay="1")

	def test_run_negative_delay(self):
		"""Test run with negative delay."""
		pipeline = Pipeline()

		with pytest.raises(ValueError, match="Delay cannot be negative"):
			pipeline.run(10, delay=-1)

	def test_insert_invalid_index_type(self):
		"""Test insert with non-integer index."""

		def func(x):
			return x

		pipeline = Pipeline()

		with pytest.raises(TypeError, match="is not int"):
			pipeline.insert("1", (func,))

	def test_insert_index_out_of_range(self):
		"""Test insert with index out of range."""

		def func(x):
			return x

		pipeline = Pipeline([(func,)])

		with pytest.raises(IndexError, match="Index out of range"):
			pipeline.insert(3, (func,))

	def test_pop_invalid_index_type(self):
		"""Test pop with non-integer index."""

		def func(x):
			return x

		pipeline = Pipeline([(func,)])

		with pytest.raises(TypeError, match="is not int"):
			pipeline.pop("1")

	def test_pop_index_out_of_range(self):
		"""Test pop with index out of range."""

		def func(x):
			return x

		pipeline = Pipeline([(func,)])

		with pytest.raises(IndexError, match="Index out of range"):
			pipeline.pop(2)
