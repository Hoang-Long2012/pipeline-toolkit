"""Utility for composing functions sequentially."""

def compose(steps, default=None):
	"""Apply callables sequentially to a value.

	The result of each callable is passed as the first argument to the next callable.

	Args:
		steps: Callables to apply sequentially.
		default: Initial value passed to the first callable.
			Defaults to ``None``.

	Returns:
		The result produced by the last callable, or ``default`` when no callables are provided.

	Raises:
		TypeError: If `steps` is not iterable, or any step is not callable.
	"""
	result = default
	for function in steps:
		if not callable(function):
			raise TypeError("function is not callable.")
		result = function(result)
	return result
