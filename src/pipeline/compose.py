"""Utility for composing functions sequentially."""

def compose(callables):
	"""Apply a sequence of callables to a value.

	Each callable receives the result of the previous callable as its first argument.

	Args:
		callables: An iterable of callables to apply sequentially.

	Returns:
		A wrapper that applies the callables to a value and returns the final result.
		If no callables are provided, the original value is returned unchanged.

	Raises:
		TypeError: If `callables` is not iterable or contains a non-callable item.
	"""
	callables = tuple(callables)
	for function in callables:
		if not callable(function):
			raise TypeError("function is not callable.")
	def wrapper(data=None):
		result = data
		for function in callables:
			result = function(result)
		return result
	return wrapper
