"""Tests for the mut function."""
import pytest

from pipeline.mut import mut


class TestMut:
	"""Test in-place mutation and return behavior."""

	def test_returns_original_value(self):
		"""Test mut returns the original value object."""
		value = 42
		result = mut(value, lambda value: None)
		assert result is value

	def test_allows_in_place_mutation(self):
		"""Test mut allows the function to modify the value in place."""
		value = {"key": "original"}

		def modify(data):
			data["key"] = "modified"

		result = mut(value, modify)
		assert result is value
		assert value["key"] == "modified"

	def test_ignores_function_return_value(self):
		"""Test mut ignores the return value of the function."""
		value = [1, 2, 3]

		def modify(data):
			data.append(4)
			return "ignored"

		result = mut(value, modify)
		assert result is value
		assert result == [1, 2, 3, 4]

	def test_forwards_arguments(self):
		"""Test mut forwards additional positional and keyword arguments."""
		value = []

		def append_values(data, first, second=0):
			data.extend((first, second))

		result = mut(value, append_values, 1, second=2)
		assert result is value
		assert value == [1, 2]

	def test_rejects_non_callable(self):
		"""Test mut raises TypeError for a non-callable function."""
		with pytest.raises(TypeError, match="function is not callable"):
			mut(42, "not_callable")

	def test_propagates_function_errors(self):
		"""Test mut propagates exceptions raised by the function."""
		def raise_error(value):
			raise ValueError("Function error")

		with pytest.raises(ValueError, match="Function error"):
			mut(42, raise_error)
