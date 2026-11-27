"""Utility for forwarding a value to a specific positional or keyword argument."""


def forward(value, function, target, *args, **kwargs):
	"""Forward a value to a specific argument of a callable.

	If ``target`` is an integer, ``value`` is inserted as a 1-based positional argument into ``args`` at position ``target``.
	If ``target`` is a string, ``value`` is passed as a keyword argument named ``target`` in ``kwargs``.

	The callable is then invoked with the resulting positional and keyword arguments.

	Args:
		value: The value to forward to ``function``.
		function: The callable to invoke.
		target: The 1-based positional index (int) or keyword parameter name (str) where ``value`` is placed.
		args: Additional positional arguments passed to ``function``.
		kwargs: Additional keyword arguments passed to ``function``.

	Returns:
		The value returned by invoking ``function(*args, **kwargs)``.

	Raises:
		TypeError: If ``function`` is not callable, or ``target`` is not an ``int`` or ``str``.
		ValueError: If ``target`` is an integer less than 1.
		Any exception raised by ``function`` is propagated to the caller.

	Example:
	```python
	def divide(a, b):
		return a / b

	# Pass 2 as the second positional argument (target=2):
	forward(2, divide, 2, 10)  # divide(10, 2) -> 5.0

	# Pass 2 as a keyword argument (target="b"):
	forward(2, divide, "b", 10)  # divide(10, b=2) -> 5.0
	```
	"""
	if not callable(function):
		raise TypeError("function is not a callable.")
	if not isinstance(target, (str, int)):
		raise TypeError("target must be int or str.")
	if isinstance(target, int) and target < 1:
		raise ValueError("target < 1.")
	if isinstance(target, int):
		args = list(args)
		args.insert(target - 1, value)
	if isinstance(target, str):
		kwargs[target] = value
	return function(*args, **kwargs)
