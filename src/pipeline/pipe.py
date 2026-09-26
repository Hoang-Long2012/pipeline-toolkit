"""Tools for creating reusable pipeline steps from callables."""
from functools import update_wrapper

from ._compat import _DEFAULT


class step:
	"""Represent a callable with preconfigured arguments.

	The wrapped callable is invoked with a value as its first argument, followed by the stored positional and keyword arguments.

	The ``default`` attribute provides the initial value used by operations such as ``step * n`` and ``step > file``.

	Attributes:
		function: The callable to execute.
		args: Positional arguments passed to ``function``.
		kwargs: Keyword arguments passed to ``function``.
		default: The initial value used by operations that require one.
			Defaults to ``None``.

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
		self.function = function
		self.args = args
		self.kwargs = kwargs
		self._default = None
	def export(self):
		"""Export the step in pipeline step format.

		The returned tuple contains the wrapped callable and, when configured, its positional and keyword arguments.

		Returns:
			tuple: One of the following forms:

				(function,)
				(function, args)
				(function, kwargs)
				(function, args, kwargs)
		"""
		parts = [self.function]
		if self.args:
			parts.append(self.args)
		if self.kwargs:
			parts.append(self.kwargs)
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
		return self.function(default if default is not _DEFAULT else self.default, *self.args, **self.kwargs)
	def __ror__(self, other):
		return self.function(other, *self.args, **self.kwargs)
	def __mul__(self, other):
		if not isinstance(other, int):
			return NotImplemented
		if other < 1:
			raise ValueError("other < 1.")
		result = self.default
		for _ in range(other):
			result = self.function(result, *self.args, **self.kwargs)
		return result
	def __lt__(self, other):
		return self.function(other.read(), *self.args, **self.kwargs)
	def __gt__(self, other):
		return other.write(self.function(self.default, *self.args, **self.kwargs))
	def __iter__(self):
		yield from self.export()
	def __repr__(self):
		name = getattr(self.function, "__name__", type(self.function).__name__)
		parts = [f"{name}"]
		if self.args:
			parts.extend(f"{arg!r}" for arg in self.args)
		if self.kwargs:
			parts.extend(f"{key}={value!r}" for key, value in self.kwargs.items())
		return f"{type(self).__name__}({', '.join(parts)})"
	@property
	def default(self):
		"""The initial value used when a step operation needs one."""
		return self._default
	@default.setter
	def default(self, value):
		"""Set the initial value used when a step operation needs one."""
		self._default = value
class pipe:
	"""Wrap a callable as a step factory.

	The wrapped callable is preserved as the underlying operation while its metadata is copied to the wrapper.

	Calling a ``pipe`` object creates a ``step`` containing the supplied arguments.

	Args:
		function: The callable to wrap.

	Raises:
		TypeError: If ``function`` is not callable.
	"""
	def __init__(self, function):
		if not callable(function):
			raise TypeError("function is not callable.")
		self.function = function
		update_wrapper(self, self.function)
	def __call__(self, *args, **kwargs):
		return step(self.function, *args, **kwargs)
	def __repr__(self):
		name = getattr(self.function, "__name__", type(self.function).__name__)
		return f"{type(self).__name__}({name})"
