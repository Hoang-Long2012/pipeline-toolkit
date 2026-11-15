"""Utility for composing functions sequentially."""

def compose(callables):
	"""Apply callables sequentially to a value.

	The result of each callable is passed as the first argument to the next callable.

	Args:
		callables: Callables to apply sequentially.

	Returns:
		The result produced by the last callable, or ``default`` when no callables are provided.

	Raises:
		TypeError: If `steps` is not iterable, or any step is not callable.
	"""
	def wrapper(data=None):
		for function in callables:
			if not callable(function):
				raise TypeError("function is not callable.")
		result = data
		for function in callables:
			result = function(result)
		return result
	return wrapper
