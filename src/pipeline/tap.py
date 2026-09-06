import copy


def tap(value, function, *args, **kwargs):
	"""Apply a function to a deep copy of a value and return the original value.

	The function is called for its side effect.
	A deep copy of ``value`` is passed to the function, so modifications made by the function do not affect the original value.

	The return value of ``function`` is ignored.
	This makes ``tap`` useful for inspecting, logging, debugging, or otherwise processing a value without interrupting a chain of operations.

	Args:
		value: Value to pass to ``function`` and return unchanged.
		function: Callable to invoke with a deep copy of ``value``.
		*args: Additional positional arguments passed to ``function``.
		**kwargs: Additional keyword arguments passed to ``function``.

	Returns:
		The original ``value`` object.

	Raises:
		TypeError: If ``function`` is not callable.
		Any exception raised by ``copy.deepcopy`` or ``function`` is propagated to the caller.

	Example:
		>>> data = {"items": [1, 2, 3]}
		>>> tap(data, print)
		{'items': [1, 2, 3]}

		A function can modify its argument without modifying the original:

		>>> def inspect(data):
			...     data["items"].append(4)
		>>> original = {"items": [1, 2, 3]}
		>>> result = tap(original, inspect)
		>>> result is original
		True
		>>> original
		{'items': [1, 2, 3]}
	"""
	if not callable(function):
		raise TypeError("function is not callable.")
	function(copy.deepcopy(value), *args, **kwargs)
	return value