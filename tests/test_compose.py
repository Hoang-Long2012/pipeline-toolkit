"""Tests for the compose function."""
from functools import partial

import pytest

from pipeline import compose


class TestComposeBasic:
	"""Test basic compose functionality."""

	def test_compose_single_function(self):
		"""Test compose with a single function."""
		def add_five(x):
			return x + 5

		assert compose([add_five])(10) == 15

	def test_compose_multiple_functions(self):
		"""Test compose with multiple functions."""
		def add_five(x):
			return x + 5

		def multiply_by_two(x):
			return x * 2

		assert compose([add_five, multiply_by_two])(10) == 30

	def test_compose_empty(self):
		"""Test compose with no functions."""
		assert compose([])(42) == 42

	def test_compose_with_none(self):
		"""Test compose with None as input."""
		def process(x):
			return x if x is not None else 0

		assert compose([process])() == 0

	def test_compose_without_arguments(self):
		"""Test compose with no input argument."""
		assert compose([])() is None


class TestComposeChaining:
	"""Test compose function chaining."""

	def test_compose_chaining_order(self):
		"""Test that functions are applied in order."""
		results = []

		def track1(x):
			results.append(1)
			return x + 1

		def track2(x):
			results.append(2)
			return x + 1

		def track3(x):
			results.append(3)
			return x + 1

		assert compose([track1, track2, track3])(0) == 3
		assert results == [1, 2, 3]

	def test_compose_data_flow(self):
		"""Test data flows correctly through functions left-to-right."""
		def triple(x):
			return x * 3

		def subtract_two(x):
			return x - 2

		def divide_by_two(x):
			return x / 2

		assert compose([triple, subtract_two, divide_by_two])(10) == 14.0

	def test_compose_calculation_example(self):
		"""Test compose with a specific calculation."""
		result = compose([
			lambda x: x * 2,
			lambda x: x + 5,
			lambda x: x // 2
		])(20)

		assert result == 22


class TestComposeTypes:
	"""Test compose with different types."""

	def test_compose_with_strings(self):
		"""Test compose with string operations."""
		def upper(s):
			return s.upper()

		def reverse(s):
			return s[::-1]

		assert compose([upper, reverse])("hello") == "OLLEH"

	def test_compose_with_lists(self):
		"""Test compose with list operations."""
		def append_item(lst):
			result = lst.copy()
			result.append(4)
			return result

		def extend_list(lst):
			result = lst.copy()
			result.extend([5, 6])
			return result

		assert compose([append_item, extend_list])([1, 2, 3]) == [
			1, 2, 3, 4, 5, 6
		]

	def test_compose_with_dicts(self):
		"""Test compose with dictionary operations."""
		def add_key(d):
			d = d.copy()
			d["new_key"] = "value"
			return d

		def update_key(d):
			d = d.copy()
			d["existing"] = "updated"
			return d

		assert compose([add_key, update_key])({"existing": "original"}) == {
			"existing": "updated",
			"new_key": "value"
		}


class TestComposeExceptions:
	"""Test compose error handling."""

	def test_compose_non_iterable(self):
		"""Test compose raises an error when input is not iterable."""
		with pytest.raises(TypeError):
			compose(42)

	def test_compose_non_callable(self):
		"""Test compose raises an error for non-callable items."""
		with pytest.raises(TypeError, match="function is not callable"):
			compose(["not_callable"])

	def test_compose_propagates_exceptions(self):
		"""Test that exceptions from functions are propagated."""
		def raise_error(x):
			raise ValueError("Custom error")

		with pytest.raises(ValueError, match="Custom error"):
			compose([raise_error])(10)

	def test_compose_non_callable_in_chain(self):
		"""Test compose rejects non-callable items before execution."""
		results = []

		def valid(x):
			results.append(x)
			return x + 1

		with pytest.raises(TypeError, match="function is not callable"):
			compose([valid, 42, valid])

		assert results == []


class TestComposeComplexScenarios:
	"""Test compose with complex scenarios."""

	def test_compose_with_lambdas(self):
		"""Test compose with lambda functions."""
		result = compose([
			lambda x: x * 2,
			lambda x: x + 5,
			lambda x: x // 2
		])(20)

		assert result == 22

	def test_compose_with_partial_functions(self):
		"""Test compose with partial functions."""
		def add(a, b):
			return a + b

		add_five = partial(add, 5)

		assert compose([add_five])(10) == 15

	def test_compose_with_methods(self):
		"""Test compose with methods."""
		class Calculator:
			def __init__(self, value):
				self.value = value

			def add(self, x):
				self.value += x
				return self.value

			def multiply(self, x):
				self.value *= x
				return self.value

		calc = Calculator(10)

		result = compose([
			lambda x: calc.add(5),
			lambda x: calc.multiply(2)
		])(None)

		assert result == 30

	def test_compose_with_generator(self):
		"""Test compose with a generator of functions."""
		def add_one(x):
			return x + 1

		steps = (step for step in [add_one, add_one])

		assert compose(steps)(0) == 2

	def test_compose_reusable(self):
		"""Test that the returned wrapper can be reused."""
		def add_one(x):
			return x + 1

		function = compose([add_one])

		assert function(0) == 1
		assert function(10) == 11

	def test_compose_validates_generator(self):
		"""Test that invalid items in a generator are detected."""
		steps = (step for step in [lambda x: x + 1, 42])

		with pytest.raises(TypeError, match="function is not callable"):
			compose(steps)
