"""Tests for the chain function."""
import pytest

from pipeline.chain import chain


class TestChainContract:
	"""Test the semantic contract of the chain function."""

	def test_chain_no_steps_returns_default(self):
		"""Test chain with empty steps returns the default value."""
		result = chain([], default=42)
		assert result == 42

	def test_chain_no_steps_no_default_returns_none(self):
		"""Test chain with no steps and no default returns None."""
		result = chain([])
		assert result is None

	def test_chain_executes_steps_sequentially(self):
		"""Test chain passes output of each step as input to the next."""
		def add_one(x):
			return x + 1

		def multiply_two(x):
			return x * 2

		result = chain([(add_one,), (multiply_two,)], default=5)
		assert result == 12  # (5 + 1) * 2

	def test_chain_passes_default_to_first_step(self):
		"""Test that default is passed as input to the first step."""
		def identity(x):
			return x

		result = chain([(identity,)], default="expected_value")
		assert result == "expected_value"

	def test_chain_validates_all_steps_before_execution(self):
		"""Test that all steps are validated before any step is executed."""
		executed = []

		def record_step(x):
			executed.append("executed")
			return x

		def invalid_step():
			pass

		# Second step is invalid but should be caught during validation
		# before the first step ever executes
		with pytest.raises(TypeError):
			chain([record_step, (invalid_step, (), {}, "extra")], default=10)

		assert executed == [], "No steps should execute if validation fails"

	def test_chain_accepts_iterable_of_steps(self):
		"""Test chain materializes any iterable of steps."""

		def add_one(x):
			return x + 1

		def add_two(x):
			return x + 2

		steps_iter = iter([(add_one,), (add_two,)])
		result = chain(steps_iter, default=10)
		assert result == 13  # 10 + 1 + 2

	def test_chain_propagates_execution_errors(self):
		"""Test that exceptions from step execution are propagated."""
		def raise_error(x):
			raise ValueError("Step failed")

		with pytest.raises(ValueError, match="Step failed"):
			chain([(raise_error,)], default=10)
