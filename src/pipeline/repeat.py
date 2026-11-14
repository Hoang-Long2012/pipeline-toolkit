"""Utility for yielding repeated callable steps."""


def repeat(times, function, *args, **kwargs):
	"""Yield a callable step repeated a specified number of times.

	Each yielded step is a function that accepts a value as its first argument
	and passes it to ``function`` alongside any preconfigured positional and
	keyword arguments.

	Args:
		times: The number of times to repeat the callable. Must be a positive integer.
		function: The callable to be repeated.
		args: Additional positional arguments to pass to ``function``.
		kwargs: Additional keyword arguments to pass to ``function``.

	Yields:
		A callable wrapper that invokes ``function(value, *args, **kwargs)``.

	Raises:
		TypeError: If ``times`` is not an integer, or ``function`` is not callable.
		ValueError: If ``times`` is less than or equal to 0.

	Example:
	```python
	def add(x, amount):
		return x + amount

	steps = list(repeat(3, add, 2))
	# steps contains 3 wrapper functions, each adding 2

	value = 0
	for step in steps:
		value = step(value)
	# value is 6
	```
	"""
	if not isinstance(times, int):
		raise TypeError("times is not an int.")
	if times <= 0:
		raise ValueError("times must be positive.")
	if not callable(function):
		raise TypeError("function is not a callable.")
	def wrapper(value):
		return function(value, *args, **kwargs)
	for _ in range(times):
		yield wrapper
