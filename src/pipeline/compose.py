def compose(*args, default=None):
	"""Apply callables sequentially to a value.

	The result of each callable is passed as the first argument to the next callable.

	Args:
		*args: Callables to apply sequentially.
		default: Initial value passed to the first callable.

	Returns:
		The result produced by the last callable.

	Raises:
		TypeError: If any argument is not callable.
	"""
	result = default
	for function in args:
		if not callable(function):
			raise TypeError("function is not callable.")
		result = function(result)
	return result