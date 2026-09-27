"""Tests for core pipeline step helpers."""

import pytest

from pipeline.core import execute_step, validate_step


class TestValidateStep:
	"""Test validation of pipeline step tuples."""

	@pytest.mark.parametrize(
		"step",
		[
			(lambda value: value,),
			(lambda value, extra: value + extra, (1,)),
			(lambda value, extra: value + extra, {"extra": 1}),
			(lambda value, extra=0: value + extra, (), {"extra": 1}),
		],
	)
	def test_accepts_valid_step_formats(self, step):
		validate_step(step)

	@pytest.mark.parametrize(
		("step", "error", "message"),
		[
			("not a tuple", TypeError, "Step must be a tuple"),
			((), TypeError, "Step cannot be empty"),
			((42,), TypeError, "Step function must be callable"),
			((lambda value: value, (), {}, None), TypeError, "at most 3 items"),
			((lambda value: value, 1), TypeError, "Step arguments must be a tuple or mapping"),
			((lambda value: value, {}, {}), TypeError, "positional arguments must be a tuple"),
			((lambda value: value, (), []), TypeError, "keyword arguments must be a mapping"),
		],
	)
	def test_rejects_invalid_step_formats(self, step, error, message):
		with pytest.raises(error, match=message):
			validate_step(step)


class TestExecuteStep:
	"""Test invocation of pipeline step tuples."""

	def test_executes_callable_only(self):
		assert execute_step((lambda value: value + 1,), 2) == 3

	def test_executes_with_positional_arguments(self):
		assert execute_step((lambda value, amount: value + amount, (3,)), 2) == 5

	def test_executes_with_keyword_arguments_mapping(self):
		assert execute_step((lambda value, amount: value + amount, {"amount": 3}), 2) == 5

	def test_executes_with_positional_and_keyword_arguments(self):
		step = (lambda value, amount, factor: (value + amount) * factor, (3,), {"factor": 2})
		assert execute_step(step, 2) == 10
