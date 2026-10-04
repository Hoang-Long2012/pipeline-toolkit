"""Utility for executing pipeline steps sequentially."""
from . import core


def chain(steps, default=None):
	"""Execute pipeline steps sequentially with an initial value.

	Each step receives the result of the previous step as its first positional argument.

	Args:
		steps: An iterable of pipeline steps to execute in order.
		default: Initial value passed to the first step.
			Defaults to ``None``.

	Returns:
		The result produced by the last step, or ``default`` if no steps are configured.

	Raises:
		TypeError: If any step has an invalid format.
	"""
	steps = tuple(steps)
	for step in steps:
		core.validate_step(step)
	result = default
	for step in steps:
		result = core.execute_step(step, result)
	return result
