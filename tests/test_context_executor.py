"""Tests for the context_executor function."""
from contextlib import contextmanager

import pytest

from pipeline import Pipeline, context_executor


class CustomContext:
	"""Helper context manager to track execution lifecycle."""

	def __init__(self, value, *args, **kwargs):
		self.value = value
		self.args = args
		self.kwargs = kwargs
		self.entered = False
		self.exited = False

	def __enter__(self):
		self.entered = True
		return f"entered:{self.value}"

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.exited = True
		return False


class TestContextExecutor:
	"""Test context_executor behavior and semantics."""

	def test_returns_context_result(self):
		"""Test context_executor returns the value yielded by the context manager."""
		@contextmanager
		def sample_manager(value):
			yield value * 2

		result = context_executor(21, sample_manager)
		assert result == 42

	def test_enters_and_exits_context_manager(self):
		"""Test context_executor properly enters and exits the context manager."""
		tracker = []

		class TrackerContext:
			def __enter__(self):
				tracker.append("enter")
				return "active"

			def __exit__(self, exc_type, exc_val, exc_tb):
				tracker.append("exit")
				return False

		def factory(value):
			tracker.append(f"factory:{value}")
			return TrackerContext()

		result = context_executor("test", factory)
		assert result == "active"
		assert tracker == ["factory:test", "enter", "exit"]

	def test_forwards_positional_arguments(self):
		"""Test context_executor forwards extra positional arguments to the manager."""
		context_instance = None

		def factory(value, *args):
			nonlocal context_instance
			context_instance = CustomContext(value, *args)
			return context_instance

		result = context_executor("val", factory, 1, 2, 3)
		assert result == "entered:val"
		assert context_instance.args == (1, 2, 3)
		assert context_instance.entered is True
		assert context_instance.exited is True

	def test_forwards_keyword_arguments(self):
		"""Test context_executor forwards keyword arguments to the manager."""
		context_instance = None

		def factory(value, **kwargs):
			nonlocal context_instance
			context_instance = CustomContext(value, **kwargs)
			return context_instance

		result = context_executor("val", factory, option="custom", flag=True)
		assert result == "entered:val"
		assert context_instance.kwargs == {"option": "custom", "flag": True}
		assert context_instance.entered is True
		assert context_instance.exited is True

	def test_forwards_mixed_arguments(self):
		"""Test context_executor forwards both positional and keyword arguments."""
		@contextmanager
		def mixed_manager(value, prefix, suffix="", repeat=1):
			yield (prefix + str(value) + suffix) * repeat

		result = context_executor(5, mixed_manager, "[", suffix="]", repeat=2)
		assert result == "[5][5]"

	def test_rejects_non_callable_manager(self):
		"""Test context_executor raises TypeError when manager is not callable."""
		with pytest.raises(TypeError, match="manager is not a callable"):
			context_executor(42, "not_callable")

	def test_propagates_exception_from_manager(self):
		"""Test context_executor propagates exceptions raised when calling manager."""
		def failing_manager(value):
			raise ValueError("Factory failed")

		with pytest.raises(ValueError, match="Factory failed"):
			context_executor(42, failing_manager)

	def test_propagates_exception_from_enter(self):
		"""Test context_executor propagates exceptions raised inside __enter__."""
		class FailingEnterContext:
			def __enter__(self):
				raise RuntimeError("Enter failed")

			def __exit__(self, exc_type, exc_val, exc_tb):
				return False

		with pytest.raises(RuntimeError, match="Enter failed"):
			context_executor(42, lambda v: FailingEnterContext())

	def test_propagates_exception_from_exit(self):
		"""Test context_executor propagates exceptions raised inside __exit__."""
		class FailingExitContext:
			def __enter__(self):
				return "ok"

			def __exit__(self, exc_type, exc_val, exc_tb):
				raise RuntimeError("Exit failed")

		with pytest.raises(RuntimeError, match="Exit failed"):
			context_executor(42, lambda v: FailingExitContext())

	def test_works_as_pipeline_step(self):
		"""Test context_executor can be used as a step in a Pipeline."""
		@contextmanager
		def multiply_context(value, factor):
			yield value * factor

		pipeline = Pipeline([
			(context_executor, (multiply_context, 3)),
		])
		result = pipeline(10)
		assert result == 30
