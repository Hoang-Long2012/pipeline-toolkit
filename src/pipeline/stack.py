class StackOverflowError(Exception):
	"""Raised when attempting to push an item onto a full stack."""
class StackUnderflowError(Exception):
	"""Raised when attempting to access or remove an item from an empty stack."""
class Stack:
	"""A simple LIFO stack container with optional maximum capacity.

	The stack follows the Last-In, First-Out (LIFO) principle. The most recently pushed item is returned by :meth:`get` or removed by :meth:`pop`.

	A maximum size can optionally be specified.
	A ``maxsize`` of ``0`` means that the stack has no size limit.

	Args:
		maxsize: Maximum number of items allowed in the stack.
			Defaults to ``0``, meaning unlimited capacity.

	Raises:
		TypeError: If ``maxsize`` is not an integer.
		ValueError: If ``maxsize`` is negative.

	Example:
		>>> stack = Stack(3)
		>>> stack.push("first")
		>>> stack.push("second")
		>>> stack.get()
		'second'
		>>> stack.pop()
		'second'
		>>> len(stack)
		1
	"""
	def __init__(self, maxsize=0):
		"""Initialize an empty stack.

		Args:
			maxsize: Maximum number of items allowed in the stack.
				``0`` means unlimited capacity.

		Raises:
			TypeError: If ``maxsize`` is not an integer.
			ValueError: If ``maxsize`` is negative.
		"""
		if not isinstance(maxsize, int):
			raise TypeError("maxsize is not int.")
		if maxsize < 0:
			raise ValueError("maxsize < 0.")
		self._maxsize = maxsize
		self._stack = []
	def push(self, value):
		"""Push an item onto the top of the stack.

		Args:
			value: Value to push onto the stack.

		Raises:
			StackOverflowError: If the stack has reached its maximum capacity.
		"""
		if self._maxsize and len(self._stack) >= self._maxsize:
			raise StackOverflowError("stack overflow")
		self._stack.append(value)
	def get(self):
		"""Return the item at the top of the stack without removing it.

		Returns:
			The most recently pushed item.

		Raises:
			StackUnderflowError: If the stack is empty.
		"""
		if not self._stack:
			raise StackUnderflowError("stack underflow")
		return self._stack[-1]
	def pop(self):
		"""Remove and return the item at the top of the stack.

		Returns:
			The most recently pushed item.

		Raises:
			StackUnderflowError: If the stack is empty.
		"""
		if not self._stack:
			raise StackUnderflowError("stack underflow")
		return self._stack.pop()
	def clear(self):
		"""Remove all items from the stack."""
		self._stack.clear()
	def empty(self):
		"""Return whether the stack is empty.

		Returns:
			``True`` if the stack contains no items, otherwise ``False``.
		"""
		return len(self._stack) == 0
	def full(self):
		"""Return whether the stack has reached its maximum capacity.

		An unlimited stack is never considered full.

		Returns:
			``True`` if the stack is full, otherwise ``False``.
		"""
		return bool(self._maxsize and len(self._stack) >= self._maxsize)
	def __len__(self):
		"""Return the number of items currently in the stack."""
		return len(self._stack)
	def __bool__(self):
		"""Return whether the stack contains at least one item."""
		return bool(self._stack)
	def __contains__(self, value):
		"""Return whether a value exists in the stack.

		Args:
			value: Value to search for.

		Returns:
			``True`` if ``value`` is present, otherwise ``False``.
		"""
		return value in self._stack
	def __iter__(self):
		"""Iterate over the items in the stack from bottom to top.

		Returns:
			An iterator over the stack's items.
		"""
		yield from self._stack
	def __repr__(self):
		"""Return the developer-oriented representation of the stack."""
		return f"{type(self).__name__}({self._stack!r}, maxsize={self._maxsize})"