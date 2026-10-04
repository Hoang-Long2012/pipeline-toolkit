"""Utility for applying side effects to a value in place."""


def mut(value, function, *args, **kwargs):
	"""Apply a function to a value in place and return the value.

	The function is called for its side effect.
	The original ``value`` is passed directly to the function, so modifications made by the function affect the value.

	The return value of ``function`` is ignored.
	This makes ``mut`` useful for modifying a value within a chain of operations without replacing the value with the function's return value.

	Args:
		value: Value to pass to ``function`` and return after mutation.
		function: Callable to invoke with ``value``.
		*args: Additional positional arguments passed to ``function``.
		**kwargs: Additional keyword arguments passed to ``function``.

	Returns:
		The original ``value`` object, potentially modified by ``function``.

	Raises:
		TypeError: If ``function`` is not callable.
		Any exception raised by ``function`` is propagated to the caller.

	Example:
	```python
	data = {"items": [1, 2, 3]}
	mut(data, dict.update, {"name": "example"})

	data
	# {'items': [1, 2, 3], 'name': 'example'}
	```

	A function can modify the value directly:

	```python
	def append_item(data):
	    data["items"].append(4)

	original = {"items": [1, 2, 3]}

	result = mut(original, append_item)

	result is original  # True

	original
	# {'items': [1, 2, 3, 4]}
	```
	"""
	if not callable(function):
		raise TypeError("function is not callable.")
	function(value, *args, **kwargs)
	return value
