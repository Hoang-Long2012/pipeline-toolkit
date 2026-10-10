"""Tests for the Checkpoint class."""
import threading

from pipeline import Checkpoint


class TestCheckpointInitialization:
	"""Test Checkpoint initialization."""

	def test_checkpoint_init(self):
		"""Test initializing a checkpoint."""
		checkpoint = Checkpoint()

		assert checkpoint.value is None


class TestCheckpointCall:
	"""Test calling a checkpoint."""

	def test_call_stores_value(self):
		"""Test calling checkpoint stores the supplied value."""
		checkpoint = Checkpoint()
		finished = threading.Event()
		entered = threading.Event()
		result = []

		def run():
			entered.set()
			result.append(checkpoint(42))
			finished.set()

		thread = threading.Thread(target=run)
		thread.start()

		assert entered.wait(timeout=1.0)

		while checkpoint.value is None and not finished.is_set():
			threading.Event().wait(0.001)

		assert checkpoint.value == 42
		assert not finished.is_set()

		checkpoint.next()

		assert finished.wait(timeout=1.0)
		thread.join(timeout=1.0)

		assert result == [42]

	def test_call_returns_original_value(self):
		"""Test checkpoint returns the value supplied to it."""
		checkpoint = Checkpoint()
		finished = threading.Event()
		entered = threading.Event()
		value = object()
		result = []

		def run():
			entered.set()
			result.append(checkpoint(value))
			finished.set()

		thread = threading.Thread(target=run)
		thread.start()

		assert entered.wait(timeout=1.0)

		while checkpoint.value is None and not finished.is_set():
			threading.Event().wait(0.001)

		assert checkpoint.value is value
		assert not finished.is_set()

		checkpoint.next()

		assert finished.wait(timeout=1.0)
		thread.join(timeout=1.0)

		assert result[0] is value

	def test_call_blocks_until_next(self):
		"""Test checkpoint blocks until next is called."""
		checkpoint = Checkpoint()
		started = threading.Event()
		finished = threading.Event()

		def run():
			started.set()
			checkpoint(42)
			finished.set()

		thread = threading.Thread(target=run)
		thread.start()

		assert started.wait(timeout=1.0)

		while checkpoint.value is None:
			threading.Event().wait(0.001)

		assert not finished.is_set()

		checkpoint.next()

		assert finished.wait(timeout=1.0)
		thread.join(timeout=1.0)

	def test_call_can_be_used_repeatedly(self):
		"""Test checkpoint supports multiple activation cycles."""
		checkpoint = Checkpoint()
		first_finished = threading.Event()
		second_finished = threading.Event()
		results = []

		def run():
			results.append(checkpoint(10))
			first_finished.set()

			results.append(checkpoint(20))
			second_finished.set()

		thread = threading.Thread(target=run)
		thread.start()

		while checkpoint.value is None:
			threading.Event().wait(0.001)

		assert checkpoint.value == 10
		assert not first_finished.is_set()

		checkpoint.next()

		assert first_finished.wait(timeout=1.0)

		while checkpoint.value != 20:
			threading.Event().wait(0.001)

		assert checkpoint.value == 20
		assert not second_finished.is_set()

		checkpoint.next()

		assert second_finished.wait(timeout=1.0)
		thread.join(timeout=1.0)

		assert results == [10, 20]


class TestCheckpointWait:
	"""Test waiting for an active checkpoint."""

	def test_wait_blocks_until_active(self):
		"""Test wait blocks until the checkpoint becomes active."""
		checkpoint = Checkpoint()
		waiting = threading.Event()
		finished = threading.Event()

		def wait_for_checkpoint():
			waiting.set()
			checkpoint.wait()
			finished.set()

		waiter = threading.Thread(target=wait_for_checkpoint)
		waiter.start()

		assert waiting.wait(timeout=1.0)
		assert not finished.is_set()

		checkpoint_thread_finished = threading.Event()

		def run():
			checkpoint(42)
			checkpoint_thread_finished.set()

		thread = threading.Thread(target=run)
		thread.start()

		assert finished.wait(timeout=1.0)
		assert checkpoint.is_active
		assert checkpoint.value == 42
		assert not checkpoint_thread_finished.is_set()

		checkpoint.next()

		assert checkpoint_thread_finished.wait(timeout=1.0)

		waiter.join(timeout=1.0)
		thread.join(timeout=1.0)

	def test_wait_returns_immediately_when_active(self):
		"""Test wait returns immediately when the checkpoint is active."""
		checkpoint = Checkpoint()
		finished = threading.Event()

		def run():
			checkpoint(42)
			finished.set()

		thread = threading.Thread(target=run)
		thread.start()

		while not checkpoint.is_active:
			threading.Event().wait(0.001)

		checkpoint.wait()

		assert checkpoint.is_active
		assert not finished.is_set()

		checkpoint.next()

		assert finished.wait(timeout=1.0)
		thread.join(timeout=1.0)


class TestCheckpointNext:
	"""Test releasing checkpoint calls."""

	def test_next_releases_blocked_call(self):
		"""Test next releases a checkpoint waiting for permission."""
		checkpoint = Checkpoint()
		finished = threading.Event()

		def run():
			checkpoint(42)
			finished.set()

		thread = threading.Thread(target=run)
		thread.start()

		while checkpoint.value is None:
			threading.Event().wait(0.001)

		assert not finished.is_set()

		checkpoint.next()

		assert finished.wait(timeout=1.0)
		thread.join(timeout=1.0)

	def test_next_does_not_change_value(self):
		"""Test next does not modify the stored value."""
		checkpoint = Checkpoint()
		finished = threading.Event()

		def run():
			checkpoint(42)
			finished.set()

		thread = threading.Thread(target=run)
		thread.start()

		while checkpoint.value is None:
			threading.Event().wait(0.001)

		assert checkpoint.value == 42

		checkpoint.next()

		assert finished.wait(timeout=1.0)
		assert checkpoint.value == 42

		thread.join(timeout=1.0)


class TestCheckpointValue:
	"""Test the checkpoint value property."""

	def test_value_is_none_before_first_call(self):
		"""Test value is None before the checkpoint is activated."""
		checkpoint = Checkpoint()

		assert checkpoint.value is None

	def test_value_contains_latest_value(self):
		"""Test value contains the most recently published value."""
		checkpoint = Checkpoint()
		finished = threading.Event()

		def run():
			checkpoint(42)
			finished.set()

		thread = threading.Thread(target=run)
		thread.start()

		while checkpoint.value is None:
			threading.Event().wait(0.001)

		assert checkpoint.value == 42

		checkpoint.next()

		assert finished.wait(timeout=1.0)
		thread.join(timeout=1.0)

	def test_value_is_updated_for_each_generation(self):
		"""Test value is updated for every checkpoint activation."""
		checkpoint = Checkpoint()
		finished = threading.Event()

		def run():
			checkpoint("first")
			checkpoint("second")
			finished.set()

		thread = threading.Thread(target=run)
		thread.start()

		while checkpoint.value is None:
			threading.Event().wait(0.001)

		assert checkpoint.value == "first"

		checkpoint.next()

		while checkpoint.value != "second":
			threading.Event().wait(0.001)

		assert checkpoint.value == "second"

		checkpoint.next()

		assert finished.wait(timeout=1.0)
		thread.join(timeout=1.0)


class TestCheckpointIsActive:
	"""Test the checkpoint active state."""

	def test_is_active_is_false_initially(self):
		"""Test checkpoint is inactive before the first call."""
		checkpoint = Checkpoint()

		assert not checkpoint.is_active

	def test_is_active_is_true_while_blocked(self):
		"""Test checkpoint is active while waiting for release."""
		checkpoint = Checkpoint()
		finished = threading.Event()

		def run():
			checkpoint(42)
			finished.set()

		thread = threading.Thread(target=run)
		thread.start()

		while not checkpoint.is_active:
			threading.Event().wait(0.001)

		assert checkpoint.is_active
		assert not finished.is_set()

		checkpoint.next()

		assert finished.wait(timeout=1.0)
		assert not checkpoint.is_active

		thread.join(timeout=1.0)


class TestCheckpointPipeline:
	"""Test using Checkpoint as a pipeline step."""

	def test_checkpoint_preserves_pipeline_value(self):
		"""Test checkpoint passes its value through unchanged."""
		from pipeline import Pipeline

		checkpoint = Checkpoint()
		pipeline = Pipeline([
			(checkpoint,),
		])

		pipeline.run(42)

		while checkpoint.value is None:
			threading.Event().wait(0.001)

		assert checkpoint.value == 42

		checkpoint.next()
		pipeline.wait()

		assert pipeline.result == 42

	def test_checkpoint_pauses_pipeline_until_next(self):
		"""Test checkpoint pauses pipeline execution until released."""
		from pipeline import Pipeline

		checkpoint = Checkpoint()
		step_finished = threading.Event()

		def after(value):
			step_finished.set()
			return value + 1

		pipeline = Pipeline([
			(checkpoint,),
			(after,),
		])

		pipeline.run(42)

		while checkpoint.value is None:
			threading.Event().wait(0.001)

		assert checkpoint.value == 42
		assert not step_finished.is_set()

		checkpoint.next()

		assert step_finished.wait(timeout=1.0)
		pipeline.wait()

		assert pipeline.result == 43

	def test_checkpoint_exposes_pipeline_value(self):
		"""Test checkpoint exposes the value received from the pipeline."""
		from pipeline import Pipeline

		checkpoint = Checkpoint()
		pipeline = Pipeline([
			(lambda value: value * 2,),
			(checkpoint,),
		])

		pipeline.run(21)

		while checkpoint.value is None:
			threading.Event().wait(0.001)

		assert checkpoint.value == 42

		checkpoint.next()
		pipeline.wait()

		assert pipeline.result == 42
