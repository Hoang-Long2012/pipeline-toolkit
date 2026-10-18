"""A container for managing and executing a collection of pipelines or sub-groups."""
import copy

from .pipeline import Pipeline


class Group:
	"""A container for managing and executing a collection of pipelines or sub-groups.

	``Group`` allows multiple ``Pipeline`` instances or nested ``Group`` instances to be organized, executed, and controlled together as a single unit.

	Pipelines and sub-groups in a group can be started, stopped, or waited on collectively.
	The group also supports common sequence operations such as indexing, iteration, and length inspection.

	Example:
	``````python
	from pipeline import Group, Pipeline

	p1 = Pipeline([(lambda x: x + 1,)])
	p2 = Pipeline([(lambda x: x * 2,)])

	group = Group([p1, p2])
	group.run(5).wait()
	``````
	"""
	def __init__(self, iterable=()):
		"""Initialize a group of pipelines.

		Args:
			iterable: An iterable containing ``Pipeline`` or ``Group`` instances.
				Defaults to an empty group.

		Raises:
			TypeError: If ``iterable`` is not iterable, or if any item is not a ``Pipeline`` or ``Group``.
		"""
		self._pipelines = []
		for pipeline in iterable:
			if not isinstance(pipeline, (Pipeline, type(self))):
				raise TypeError(f"{pipeline} is not a Pipeline or Group.")
			self._pipelines.append(pipeline)
	def _validate(self, pipeline):
		if not isinstance(pipeline, (Pipeline, type(self))):
			raise TypeError("pipeline is not a Pipeline or Group.")
	def run(self, *args, **kwargs):
		"""Start all pipelines in the group.

		Passes all positional and keyword arguments to each pipeline's ``run()`` method.

		Args:
			args: Positional arguments forwarded to each pipeline's ``run()`` method.
			kwargs: Keyword arguments forwarded to each pipeline's ``run()`` method.

		Returns:
			This group instance.
		"""
		for pipeline in self._pipelines:
			pipeline.run(*args, **kwargs)
		return self
	def stop(self):
		"""Stop execution of all pipelines in the group.

		Returns:
			This group instance.
		"""
		for pipeline in self._pipelines:
			pipeline.stop()
		return self
	def wait(self, timeout=None):
		"""Wait for all pipelines in the group to complete execution.

		Args:
			timeout: Maximum time in seconds to wait for each pipeline.
				Defaults to ``None`` (wait indefinitely).

		Returns:
			This group instance.
		"""
		for pipeline in self._pipelines:
			pipeline.wait(timeout)
		return self
	def add(self, pipeline):
		"""Append a pipeline or sub-group to the end of the group.

		Args:
			pipeline: A ``Pipeline`` or ``Group`` instance to add.

		Returns:
			This group instance.

		Raises:
			TypeError: If ``pipeline`` is not a ``Pipeline`` or ``Group``.
		"""
		self._validate(pipeline)
		self._pipelines.append(pipeline)
		return self
	def insert(self, index, pipeline):
		"""Insert a pipeline or sub-group at the given zero-based index.

		Args:
			index: The zero-based integer position at which to insert.
			pipeline: A ``Pipeline`` or ``Group`` instance to insert.

		Returns:
			This group instance.

		Raises:
			TypeError: If ``index`` is not an integer, or if ``pipeline`` is not a ``Pipeline`` or ``Group``.
			ValueError: If ``index`` is negative.
		"""
		if not isinstance(index, int):
			raise TypeError("index is not a int.")
		if index < 0:
			raise ValueError("index  not be a negative.")
		self._validate(pipeline)
		self._pipelines.insert(index, pipeline)
		return self
	def extend(self, iterable):
		"""Extend the group by appending pipelines and sub-groups from an iterable.

		Args:
			iterable: An iterable containing ``Pipeline`` or ``Group`` instances.

		Returns:
			This group instance.

		Raises:
			TypeError: If ``iterable`` is not iterable, or if any item is not a ``Pipeline`` or ``Group``.
		"""
		iterable = tuple(iterable)
		for pipeline in iterable:
			self._validate(pipeline)
		self._pipelines.extend(iterable)
		return self
	def remove(self, pipeline):
		"""Remove the first occurrence of a pipeline or sub-group from the group.

		Args:
			pipeline: The ``Pipeline`` or ``Group`` instance to remove.

		Returns:
			This group instance.

		Raises:
			TypeError: If ``pipeline`` is not a ``Pipeline`` or ``Group``.
			ValueError: If ``pipeline`` is not found in the group.
		"""
		self._validate(pipeline)
		self._pipelines.remove(pipeline)
		return self
	def pop(self, index):
		"""Remove and return the pipeline or sub-group at the given zero-based index.

		Args:
			index: The zero-based integer index of the item to remove.

		Returns:
			The removed ``Pipeline`` or ``Group`` instance.

		Raises:
			TypeError: If ``index`` is not an integer.
			ValueError: If ``index`` is negative.
			IndexError: If ``index`` is out of range.
		"""
		if not isinstance(index, int):
			raise TypeError("index is not a int.")
		if index < 0:
			raise ValueError("index  not be a negative.")
		if index >= len(self._pipelines):
			raise IndexError("index out of range.")
		return self._pipelines.pop(index)

	def clear(self):
		"""Remove all pipelines and sub-groups from the group.

		Returns:
			This group instance.
		"""
		self._pipelines.clear()
	def reverse(self):
		"""Reverse the order of pipelines and sub-groups in the group in place.

		Returns:
			This group instance.
		"""
		self._pipelines.reverse()
	def index(self, pipeline):
		"""Return the zero-based index of the first occurrence of a pipeline or sub-group.

		Args:
			pipeline: The ``Pipeline`` or ``Group`` instance to search for.

		Returns:
			The zero-based index of the matching pipeline or sub-group.

		Raises:
			TypeError: If ``pipeline`` is not a ``Pipeline`` or ``Group``.
			ValueError: If ``pipeline`` is not found in the group.
		"""
		self._validate(pipeline)
		for index, candidate in enumerate(self._pipelines):
			if pipeline == candidate:
				return index
		raise ValueError(f"{'pipeline' if isinstance(pipeline, Pipeline) else 'sub-group'} not found in group.")
	def count(self, pipeline):
		"""Return the number of occurrences of a pipeline or sub-group in the group.

		Args:
			pipeline: The ``Pipeline`` or ``Group`` instance to count.

		Returns:
			The number of times ``pipeline`` occurs in the group.

		Raises:
			TypeError: If ``pipeline`` is not a ``Pipeline`` or ``Group``.
		"""
		self._validate(pipeline)
		return sum(pipeline == candidate for candidate in self._pipelines)
	def copy(self):
		"""Return a shallow copy of the group.

		Returns:
			A new ``Group`` instance containing references to the same pipelines and sub-groups.
		"""
		return copy.copy(self)
	def __call__(self, *args, **kwargs):
		"""Start all pipelines in the group.

		Equivalent to calling ``run(*args, **kwargs)``.

		Args:
			args: Positional arguments forwarded to ``run()``.
			kwargs: Keyword arguments forwarded to ``run()``.

		Returns:
			This group instance.
		"""
		return self.run(*args, **kwargs)
	def __len__(self):
		"""Return the number of pipelines and sub-groups in the group."""
		return len(self._pipelines)
	def __bool__(self):
		"""Return whether the group contains at least one pipeline or sub-group.

		Returns:
			````True```` if the group is non-empty, otherwise ````False````.
		"""
		return bool(self._pipelines)
	def __contains__(self, pipeline):
		"""Return whether a pipeline or sub-group exists in the group.

		Args:
			pipeline: The ``Pipeline`` or ``Group`` instance to search for.

		Returns:
			````True```` if ``pipeline`` is found in the group, otherwise ````False````.

		Raises:
			TypeError: If ``pipeline`` is not a ``Pipeline`` or ``Group``.
		"""
		self._validate(pipeline)
		for candidate in self._pipelines:
			if pipeline == candidate:
				return True
		return False
	def __getitem__(self, index):
		"""Return the pipeline or sub-group at the given zero-based index.

		Args:
			index: Zero-based integer index of the item to retrieve.

		Returns:
			The ``Pipeline`` or ``Group`` at the specified index.

		Raises:
			TypeError: If ``index`` is not an integer.
			ValueError: If ``index`` is negative.
			IndexError: If ``index`` is out of range.
		"""
		if not isinstance(index, int):
			raise TypeError("index is not a int.")
		if index < 0:
			raise ValueError("index  not be a negative.")
		if index >= len(self._pipelines):
			raise IndexError("index out of range.")
		return self._pipelines[index]
	def __setitem__(self, index, pipeline):
		"""Set the pipeline or sub-group at the given zero-based index.

		Args:
			index: Zero-based integer index of the item to replace.
			pipeline: A ``Pipeline`` or ``Group`` instance to assign.

		Raises:
			TypeError: If ``index`` is not an integer, or if ``pipeline`` is not a ``Pipeline`` or ``Group``.
			ValueError: If ``index`` is negative.
			IndexError: If ``index`` is out of range.
		"""
		if not isinstance(index, int):
			raise TypeError("index is not a int.")
		if index < 0:
			raise ValueError("index  not be a negative.")
		if index >= len(self._pipelines):
			raise IndexError("index out of range.")
		self._validate(pipeline)
		self._pipelines[index] = pipeline
	def __delitem__(self, index):
		"""Delete the pipeline or sub-group at the given zero-based index.

		Args:
			index: Zero-based integer index of the item to delete.

		Raises:
			TypeError: If ``index`` is not an integer.
			ValueError: If ``index`` is negative.
			IndexError: If ``index`` is out of range.
		"""
		if not isinstance(index, int):
			raise TypeError("index is not a int.")
		if index < 0:
			raise ValueError("index  not be a negative.")
		if index >= len(self._pipelines):
			raise IndexError("index out of range.")
		del self._pipelines[index]
	def __iter__(self):
		"""Iterate over the pipelines and sub-groups in the group.

		Yields:
			Each ``Pipeline`` or ``Group`` in the group in order.
		"""
		yield from self._pipelines
	def __reversed__(self):
		"""Return an iterator that yields pipelines and sub-groups in reverse order.

		Returns:
			A reverse iterator over the pipelines and sub-groups in the group.
		"""
		yield from reversed(self._pipelines)
	def __repr__(self):
		"""Return a string representation of the group."""
		return f"{type(self).__name__}(pipeline={sum(isinstance(pipeline, Pipeline) for pipeline in self._pipelines)}, sub-group={sum(isinstance(pipeline, type(self)) for pipeline in self._pipelines)})"
	def __eq__(self, other):
		"""Return whether this group is equal to another group.

		Args:
			other: The object to compare with.

		Returns:
			``True`` if ``other`` contains the same pipelines and sub-groups in the same order, otherwise ``False``.
		"""
		if not isinstance(other, type(self)):
			return NotImplemented
		return self._pipelines == other._pipelines
	def __copy__(self):
		"""Return a shallow copy of the group."""
		return type(self)(self._pipelines)
