"""Tests for the compose function."""
import pytest

from pipeline import compose


class TestComposeBasic:
	"""Test basic compose functionality."""

	def test_compose_single_function(self):
		"""Test compose with a single function."""
		def add_five(x):
			return x + 5
		result = compose(add_five, default=10)
		assert result == 15

	def test_compose_multiple_functions(self):
		"""Test compose with multiple functions."""
		def add_five(x):
			return x + 5
		def multiply_by_two(x):
			return x * 2
		result = compose(add_five, multiply_by_two, default=10)
		assert result == 30	 # 10 + 5 = 15, then 15 * 2 = 30

	def test_compose_empty(self):
		"""Test compose with no functions returns default."""
		result = compose(default=42)
		assert result == 42

	def test_compose_with_none_default(self):
		"""Test compose with None as default."""
		def process(x):
			return x if x is not None else 0
		result = compose(process, default=None)
		assert result == 0


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
		compose(track1, track2, track3, default=0)
		assert results == [1, 2, 3]

	def test_compose_data_flow(self):
		"""Test data flows correctly through functions left-to-right."""
		def triple(x):
			return x * 3
		def subtract_two(x):
			return x - 2
		def divide_by_two(x):
			return x / 2
		result = compose(triple, subtract_two, divide_by_two, default=10)
		# 10 * 3 = 30, then 30 - 2 = 28, then 28 / 2 = 14.0
		assert result == 14.0

	def test_compose_calculation_example(self):
		"""Test compose with specific calculation."""
		result = compose(
			lambda x: x * 2,
			lambda x: x + 5,
			lambda x: x // 2,
			default=20
		)
		# 20 * 2 = 40, then 40 + 5 = 45, then 45 // 2 = 22
		assert result == 22


class TestComposeTypes:
	"""Test compose with different types."""

	def test_compose_with_strings(self):
		"""Test compose with string operations."""
		def upper(s):
			return s.upper()
		def reverse(s):
			return s[::-1]
		result = compose(upper, reverse, default="hello")
		assert result == "OLLEH"

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
		result = compose(append_item, extend_list, default=[1, 2, 3])
		assert result == [1, 2, 3, 4, 5, 6]

	def test_compose_with_dicts(self):
		"""Test compose with dictionary operations."""
		def add_key(d):
			d = d.copy()
			d['new_key'] = 'value'
			return d
		def update_key(d):
			d = d.copy()
			d['existing'] = 'updated'
			return d
		result = compose(add_key, update_key, default={'existing': 'original'})
		assert result == {'existing': 'updated', 'new_key': 'value'}


class TestComposeExceptions:
	"""Test compose error handling."""

	def test_compose_non_callable(self):
		"""Test compose raises error for non-callable."""
		with pytest.raises(TypeError, match="function is not callable"):
			compose("not_callable", default=10)

	def test_compose_propagates_exceptions(self):
		"""Test that exceptions from functions are propagated."""
		def raise_error(x):
			raise ValueError("Custom error")
		with pytest.raises(ValueError, match="Custom error"):
			compose(raise_error, default=10)

	def test_compose_non_callable_in_chain(self):
		"""Test compose raises error for non-callable in middle."""
		def valid(x):
			return x + 1
		with pytest.raises(TypeError, match="function is not callable"):
			compose(valid, 42, valid, default=10)


class TestComposeComplexScenarios:
	"""Test compose with complex scenarios."""

	def test_compose_with_lambdas(self):
		"""Test compose with lambda functions."""
		result = compose(
			lambda x: x * 2,
			lambda x: x + 5,
			lambda x: x // 2,
			default=20
		)
		# 20 * 2 = 40, then 40 + 5 = 45, then 45 // 2 = 22
		assert result == 22

	def test_compose_with_partial_functions(self):
		"""Test compose with partial functions."""
		from functools import partial
		def add(a, b):
			return a + b
		add_five = partial(add, 5)
		result = compose(add_five, default=10)
		assert result == 15

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
		result = compose(
			lambda x: calc.add(5),
			lambda x: calc.multiply(2),
			default=None
		)
		assert result == 30	 # (10 + 5) * 2
