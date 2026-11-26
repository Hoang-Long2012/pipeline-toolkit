"""Utility for executing callables with a context manager."""


def context_executor(value, manager, *args, **kwargs):
	"""Execute a context manager with a value and return its result.

	The context manager factory ``manager`` is called with ``value`` and any additional positional and keyword arguments.
	The context manager is entered, and the resulting value bound to the context is returned upon completion.

	Args:
		value: Value passed as the first argument to ``manager``.
		manager: A callable that accepts ``value`` and returns a context manager.
		args: Additional positional arguments passed to ``manager``.
		kwargs: Additional keyword arguments passed to ``manager``.

	Returns:
		The value yielded or returned by entering the context manager.

	Raises:
		TypeError: If ``manager`` is not callable or does not return a context manager.
		Any exception raised by ``manager`` or within the context manager is propagated to the caller.

	Example:
	```python
	from contextlib import contextmanager

	@contextmanager
	def managed(value, prefix=""):
		yield f"{prefix}{value}"

	result = context_executor("example", managed, prefix="test_")
	# result is 'test_example'
	```
	"""
	if not callable(manager):
		raise TypeError("manager is not a callable.")
	with manager(value, *args, **kwargs) as result:
		return result
