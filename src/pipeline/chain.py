"""Utility for executing callables and pipeline steps sequentially."""
from . import core


def chain(steps, default=None):
	"""Execute callables and pipeline steps sequentially with an initial value.

	Each step receives the result of the previous step as its first positional argument.
	A callable is called with only that value.
	A step tuple may be ``(function,)``, ``(function, args)``, ``(function, kwargs)``, or ``(function, args, kwargs)``.
	When keyword arguments are supplied, positional arguments must be a tuple.

	Args:
		steps: An iterable of callables or pipeline step tuples to execute in order.
		default: Initial value passed to the first step.
			Defaults to ``None``.

	Returns:
		The result produced by the last step, or ``default`` if no steps are configured.

	Raises:
		TypeError: If a non-callable step has an invalid format.
	"""
	steps = tuple(steps)
	for step in steps:
		if not callable(step):
			core.validate_step(step)
	result = default
	for step in steps:
		if not callable(step):
			result = core.execute_step(step, result)
		else:
			result = step(result)
	return result
