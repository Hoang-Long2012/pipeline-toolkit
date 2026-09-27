"""Core helpers for validating and executing pipeline steps.

A pipeline step is a tuple containing a callable and, optionally, positional arguments, keyword arguments, or both.
These helpers keep step validation and invocation behavior shared by :class:`pipeline.Pipeline` and other callers.
"""
from collections.abc import Mapping


def validate_step(step):
	"""Validate the structure of a pipeline step.

	A step may be ``(function,)``, ``(function, args)``, ``(function, kwargs)``, or ``(function, args, kwargs)``.
	When keyword arguments are supplied, positional arguments must be a tuple.

	Args:
		step: The step tuple to validate.

	Raises:
		TypeError: If the step or any of its arguments has an invalid format.
	"""
	if not isinstance(step, tuple):
		raise TypeError(f"Step must be a tuple, not {type(step).__name__}.")
	if not step:
		raise TypeError("Step cannot be empty.")
	if not callable(step[0]):
		raise TypeError(f"Step function must be callable, not {type(step[0]).__name__}.")
	if len(step) > 3:
		raise TypeError(f"Step must contain at most 3 items, got {len(step)}.")
	if len(step) >= 2:
		if not isinstance(step[1], (tuple, Mapping)):
			raise TypeError(f"Step arguments must be a tuple or mapping, not {type(step[1]).__name__}.")
	if len(step) == 3:
		if not isinstance(step[1], tuple):
			raise TypeError("Step positional arguments must be a tuple when keyword arguments are provided.")
	if len(step) == 3 and not isinstance(step[2], Mapping):
		raise TypeError(f"Step keyword arguments must be a mapping, not {type(step[2]).__name__}.")
def execute_step(step, default):
	"""Execute a validated pipeline step with its input value.

	The ``default`` value is passed as the callable's first positional argument, followed by any configured arguments.

	Args:
		step: A valid pipeline step tuple.
		default: The value passed as the callable's first argument.

	Returns:
		The value returned by the step callable.
	"""
	if len(step) == 1:
		return step[0](default)
	if isinstance(step[1], tuple):
		return step[0](default, *step[1], **step[2]) if len(step) > 2 else step[0](default, *step[1])
	return step[0](default, **step[1])