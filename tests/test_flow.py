"""Tests for the flow function."""
import inspect

import pytest

from pipeline import flow


class TestFlowBasic:
	"""Test basic flow functionality."""

	def test_flow_empty_steps(self):
		"""Test flow with no steps yields nothing."""
		result = list(flow([]))
		assert result == []

	def test_flow_empty_steps_with_data(self):
		"""Test flow with no steps and data yields nothing."""
		result = list(flow([], data=42))
		assert result == []

	def test_flow_single_step(self):
		"""Test flow with a single callable."""
		def add_five(x):
			return x + 5

		result = list(flow([add_five], data=10))
		assert result == [15]

	def test_flow_multiple_steps(self):
		"""Test flow with multiple callables yielding intermediate results."""
		def add_five(x):
			return x + 5

		def multiply_by_two(x):
			return x * 2

		result = list(flow([add_five, multiply_by_two], data=10))
		assert result == [15, 30]

	def test_flow_default_data_is_none(self):
		"""Test flow passes None to the first callable when data is omitted."""
		def handle_none(x):
			return x is None

		result = list(flow([handle_none]))
		assert result == [True]


class TestFlowGeneratorBehavior:
	"""Test generator semantics of flow."""

	def test_flow_returns_generator(self):
		"""Test flow returns a generator object."""
		gen = flow([])
		assert inspect.isgenerator(gen)

	def test_flow_lazy_execution(self):
		"""Test that steps are executed lazily during iteration."""
		executed = []

		def step_one(x):
			executed.append(1)
			return x + 1

		def step_two(x):
			executed.append(2)
			return x * 2

		gen = flow([step_one, step_two], data=5)
		assert executed == []

		first = next(gen)
		assert first == 6
		assert executed == [1]

		second = next(gen)
		assert second == 12
		assert executed == [1, 2]

		with pytest.raises(StopIteration):
			next(gen)

	def test_flow_accepts_arbitrary_iterable(self):
		"""Test flow accepts any iterable of steps."""
		def add_one(x):
			return x + 1

		steps_generator = (step for step in [add_one, add_one, add_one])
		assert list(flow(steps_generator, data=0)) == [1, 2, 3]


class TestFlowDataPassing:
	"""Test data passing between steps."""

	def test_flow_type_transitions(self):
		"""Test flow passing different types across steps."""
		def to_string(x):
			return str(x)

		def wrap_list(s):
			return [s]

		def append_item(lst):
			return lst + ["done"]

		result = list(flow([to_string, wrap_list, append_item], data=100))
		assert result == ["100", ["100"], ["100", "done"]]


class TestFlowExceptions:
	"""Test flow error handling and step validation."""

	def test_flow_non_iterable_steps(self):
		"""Test flow raises TypeError when steps is not iterable upon iteration."""
		gen = flow(42)
		with pytest.raises(TypeError):
			next(gen)

	def test_flow_validates_all_steps_before_execution(self):
		"""Test that invalid steps are caught before any step executes."""
		executed = []

		def valid_step(x):
			executed.append("run")
			return x

		gen = flow([valid_step, 42], data=10)
		with pytest.raises(TypeError, match="int is not a callable."):
			next(gen)

		assert executed == [], "No step should execute if any step is not callable"

	def test_flow_error_step_with_custom_name(self):
		"""Test error message uses __name__ attribute if present."""
		class NamedObject:
			__name__ = "CustomStep"

		gen = flow([NamedObject()], data=10)
		with pytest.raises(TypeError, match="CustomStep is not a callable."):
			next(gen)

	def test_flow_propagates_execution_errors(self):
		"""Test that exceptions raised by steps are propagated."""
		def step_one(x):
			return x + 1

		def failing_step(x):
			raise ValueError("Step execution failed")

		gen = flow([step_one, failing_step], data=5)
		assert next(gen) == 6

		with pytest.raises(ValueError, match="Step execution failed"):
			next(gen)
