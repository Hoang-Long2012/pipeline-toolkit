from functools import update_wrapper


class step:
	"""Represent a callable with preconfigured arguments.

	The wrapped callable is invoked with a value as its first argument,
	followed by the stored positional and keyword arguments.

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
	def __call__(self, default=None):
		return self.function(default, *self.args, **self.kwargs)
	def __ror__(self, other):
		return self.function(other, *self.args, **self.kwargs)
	def __mul__(self, other):
		if not isinstance(other, int):
			return NotImplemented
		if other < 1:
			raise ValueError("other < 1.")
		result = None
		for _ in range(other):
			result = self.function(result, *self.args, **self.kwargs)
		return result
	def __lt__(self, other):
		return self.function(other.read(), *self.args, **self.kwargs)
	def __gt__(self, other):
		return other.write(self.function(None, *self.args, **self.kwargs))
	def __repr__(self):
		parts = [f"{self.function!r}"]
		if self.args:
			parts.extend(f"{arg!r}" for arg in self.args)
		if self.kwargs:
			parts.extend(f"{key}={value!r}" for key, value in self.kwargs.items())
		return f"{type(self).__name__}({', '.join(parts)})"
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
		return f"{type(self).__name__}({self.__qualname__})"