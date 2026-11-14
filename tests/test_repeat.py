"""Tests for the repeat function."""
import inspect

import pytest

from pipeline import compose, flow, repeat


class TestRepeatBasic:
	"""Test basic repeat functionality."""

	def test_repeat_single_time(self):
		"""Test repeat with times=1."""
		def add_one(x):
			return x + 1

		steps = list(repeat(1, add_one))
		assert len(steps) == 1
		assert steps[0](10) == 11

	def test_repeat_multiple_times(self):
		"""Test repeat yields the expected number of callable steps."""
		def multiply_by_two(x):
			return x * 2

		steps = list(repeat(3, multiply_by_two))
		assert len(steps) == 3
		value = 1
		for step in steps:
			value = step(value)
		assert value == 8  # 1 * 2 * 2 * 2

	def test_repeat_with_args_and_kwargs(self):
		"""Test repeat correctly passes positional and keyword arguments."""
		def calculate(value, offset, multiplier=1):
			return (value + offset) * multiplier

		steps = list(repeat(2, calculate, 3, multiplier=2))
		assert len(steps) == 2
		# Step 1: (0 + 3) * 2 = 6
		# Step 2: (6 + 3) * 2 = 18
		val = 0
		for step in steps:
			val = step(val)
		assert val == 18

	def test_repeat_integration_with_compose(self):
		"""Test repeat used directly with compose."""
		def add(value, amount):
			return value + amount

		result = compose(repeat(4, add, 5), default=10)
		assert result == 30  # 10 + 5 * 4

	def test_repeat_integration_with_flow(self):
		"""Test repeat used directly with flow."""
		def double(value):
			return value * 2

		results = list(flow(repeat(3, double), data=2))
		assert results == [4, 8, 16]


class TestRepeatGeneratorBehavior:
	"""Test generator semantics of repeat."""

	def test_repeat_returns_generator(self):
		"""Test repeat returns a generator object."""
		def dummy(x):
			return x

		gen = repeat(1, dummy)
		assert inspect.isgenerator(gen)

	def test_repeat_lazy_validation(self):
		"""Test validation occurs when iteration starts, not when called."""
		gen = repeat("invalid", lambda x: x)
		assert inspect.isgenerator(gen)
		with pytest.raises(TypeError, match="times is not an int."):
			next(gen)

	def test_repeat_yields_callables(self):
		"""Test every item yielded by repeat is callable."""
		def identity(x):
			return x

		for step in repeat(5, identity):
			assert callable(step)


class TestRepeatExceptions:
	"""Test repeat error handling and argument validation."""

	def test_repeat_times_not_int(self):
		"""Test repeat raises TypeError when times is not an integer."""
		def func(x):
			return x

		with pytest.raises(TypeError, match="times is not an int."):
			next(repeat("3", func))

		with pytest.raises(TypeError, match="times is not an int."):
			next(repeat(2.5, func))

		with pytest.raises(TypeError, match="times is not an int."):
			next(repeat(None, func))

	def test_repeat_times_zero_or_negative(self):
		"""Test repeat raises ValueError when times is <= 0."""
		def func(x):
			return x

		with pytest.raises(ValueError, match="times must be positive."):
			next(repeat(0, func))

		with pytest.raises(ValueError, match="times must be positive."):
			next(repeat(-1, func))

		with pytest.raises(ValueError, match="times must be positive."):
			next(repeat(-10, func))

	def test_repeat_function_not_callable(self):
		"""Test repeat raises TypeError when function is not callable."""
		with pytest.raises(TypeError, match="function is not a callable."):
			next(repeat(3, "not_a_callable"))

		with pytest.raises(TypeError, match="function is not a callable."):
			next(repeat(3, None))

		with pytest.raises(TypeError, match="function is not a callable."):
			next(repeat(3, 42))

	def test_repeat_propagates_wrapper_exceptions(self):
		"""Test exceptions raised inside function are propagated upon invocation."""
		def fail(value):
			raise RuntimeError("Execution error")

		steps = list(repeat(2, fail))
		with pytest.raises(RuntimeError, match="Execution error"):
			steps[0](10)
