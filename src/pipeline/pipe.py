"""Tools for creating reusable pipeline steps from callables."""
from functools import wraps

from ._compat import _DEFAULT


class step:
	"""Represent a callable with preconfigured arguments.

	The wrapped callable is invoked with a value as its first argument, followed by the stored positional and keyword arguments.

	The ``default`` property provides the initial value used by operations such as ``step * n`` and ``step > file``.

	Args:
		function: The callable to execute.
		*args: Positional arguments passed to ``function``.
		**kwargs: Keyword arguments passed to ``function``.

	Raises:
		TypeError: If ``function`` is not callable.
	"""
	def __init__(self, function, *args, **kwargs):
		if not callable(function):
			raise TypeError("function is not callable.")
		self._function = function
		self._args = args
		self._kwargs = kwargs
		self._default = None
	def export(self):
		"""Export the step in pipeline step format.

		The returned tuple contains the wrapped callable and, when configured, its positional and keyword arguments.

		Returns:
			tuple: One of the following forms:

		```python
		(function,)
		(function, args)
		(function, kwargs)
		(function, args, kwargs)
		```
		"""
		parts = [self._function]
		if self._args:
			parts.append(self._args)
		if self._kwargs:
			parts.append(self._kwargs)
		return tuple(parts)
	def __call__(self, default=_DEFAULT):
		"""Execute the step with an input value.

		If ``default`` is omitted, the step's configured ``default`` value is used.

		Args:
			default: The value passed to the wrapped callable. If omitted, use the
				step's configured default.

		Returns:
			The value returned by the wrapped callable.
		"""
		return self._function(default if default is not _DEFAULT else self.default, *self._args, **self._kwargs)
	def __ror__(self, other):
		"""Execute the step with ``other`` as the input value.

		Returns:
			The value returned by the wrapped callable.
		"""
		return self._function(other, *self._args, **self._kwargs)
	def __mul__(self, other):
		"""Execute the step repeatedly using the previous result as input.

		Args:
			other: The number of times to execute the step.

		Returns:
			The value returned by the final execution.

		Raises:
			ValueError: If ``other`` is less than 1.
		"""
		if not isinstance(other, int):
			return NotImplemented
		if other < 1:
			raise ValueError("other < 1.")
		result = self.default
		for _ in range(other):
			result = self._function(result, *self._args, **self._kwargs)
		return result
	def __lt__(self, other):
		"""Read a value from a file-like object and execute the step with it.

		Args:
			other: An object providing a ``read()`` method.

		Returns:
			The value returned by the wrapped callable.
		"""
		return self._function(other.read(), *self._args, **self._kwargs)
	def __gt__(self, other):
		"""Execute the step and write its result to a file-like object.

		Args:
			other: An object providing a ``write()`` method.

		Returns:
			The value returned by ``other.write()``.
		"""
		return other.write(self._function(self.default, *self._args, **self._kwargs))
	def __iter__(self):
		yield from self.export()
	def __repr__(self):
		name = getattr(self._function, "__name__", type(self._function).__name__)
		parts = [f"{name}"]
		if self._args:
			parts.extend(f"{arg!r}" for arg in self._args)
		if self._kwargs:
			parts.extend(f"{key}={value!r}" for key, value in self._kwargs.items())
		return f"{type(self).__name__}({', '.join(parts)})"
	@property
	def default(self):
		"""The initial value used when a step operation needs one."""
		return self._default
	@default.setter
	def default(self, value):
		"""Set the initial value used when a step operation needs one."""
		self._default = value
def pipe(function):
	"""Wrap a callable as a step factory.

	The wrapped callable is preserved as the underlying operation while its metadata is copied to the wrapper.

	Calling a ``pipe`` object creates a ``step`` containing the supplied arguments.

	Args:
		function: The callable to wrap.

	Raises:
		TypeError: If ``function`` is not callable.
	"""
	if not callable(function):
		raise TypeError("function is not callable.")
	@wraps(function)
	def wrapper(*args, **kwargs):
		return step(function, *args, **kwargs)
	return wrapper
