import copy
from .pipeline import Pipeline


class Group:
	def __init__(self, iterable=()):
		self._pipelines = []
		for pipeline in iterable:
			if not isinstance(pipeline, (Pipeline, type(self))):
				raise TypeError(f"{pipeline} is not a Pipeline or Group.")
			self._pipelines.append(pipeline)
	def _validate(self, pipeline):
		if not isinstance(pipeline, (Pipeline, type(self))):
			raise TypeError("pipeline is not a Pipeline or Group.")
	def run(self, *args, **kwargs):
		for pipeline in self._pipelines:
			pipeline.run(*args, **kwargs)
		return self
	def stop(self):
		for pipeline in self._pipelines:
			pipeline.stop()
		return self
	def wait(self, timeout=None):
		for pipeline in self._pipelines:
			pipeline.wait(timeout)
		return self
	def add(self, pipeline):
		self._validate(pipeline)
		self._pipelines.append(pipeline)
	def insert(self, index, pipeline):
		if not isinstance(index, int):
			raise TypeError("index is not a int.")
		if index < 0:
			raise ValueError("index  not be a negative.")
		self._validate(pipeline)
		self._pipelines.insert(index, pipeline)
	def extend(self, iterable):
		iterable = tuple(iterable)
		for pipeline in iterable:
			self._validate(pipeline)
		for pipeline in iterable:
			self.add(pipeline)
	def remove(self, pipeline):
		self._validate(pipeline)
		self._pipelines.remove(pipeline)
	def pop(self, index):
		if not isinstance(index, int):
			raise TypeError("index is not a int.")
		if index < 0:
			raise ValueError("index  not be a negative.")
		if index >= len(self._pipelines):
			raise IndexError("index out of range.")
		return self._pipelines.pop(index)
	def clear(self):
		self._pipelines.clear()
	def reverse(self):
		self._pipelines.reverse()
	def index(self, pipeline):
		self._validate(pipeline)
		for index, candidate in enumerate(self._pipelines):
			if pipeline == candidate:
				return index
		raise ValueError(f"{'pipeline' if isinstance(pipeline, Pipeline) else 'subgroup'} not found in group.")
	def count(self, pipeline):
		self._validate(pipeline)
		return sum(pipeline == candidate for candidate in self._pipelines)
	def copy(self):
		return copy.copy(self)
	def __call__(self, *args, **kwargs):
		return self.run(*args, **kwargs)
	def __len__(self):
		return len(self._pipelines)
	def __bool__(self):
		return bool(self._pipelines)
	def __contains__(self, pipeline):
		self._validate(pipeline)
		for candidate in self._pipelines:
			if pipeline == candidate:
				return True
		return False
	def __getitem__(self, index):
		if not isinstance(index, int):
			raise TypeError("index is not a int.")
		if index < 0:
			raise ValueError("index  not be a negative.")
		if index >= len(self._pipelines):
			raise IndexError("index out of range.")
		return self._pipelines[index]
	def __setitem__(self, index, pipeline):
		if not isinstance(index, int):
			raise TypeError("index is not a int.")
		if index < 0:
			raise ValueError("index  not be a negative.")
		if index >= len(self._pipelines):
			raise IndexError("index out of range.")
		self._validate(pipeline)
		self._pipelines[index] = pipeline
	def __delitem__(self, index):
		if not isinstance(index, int):
			raise TypeError("index is not a int.")
		if index < 0:
			raise ValueError("index  not be a negative.")
		if index >= len(self._pipelines):
			raise IndexError("index out of range.")
		del self._pipelines[index]
	def __iter__(self):
		yield from self._pipelines		
	def __reversed__(self):
		yield from reversed(self._pipelines)
	def __repr__(self):
		return f"{type(self).__name__}(pipeline={sum(isinstance(pipeline, Pipeline) for pipeline in self._pipelines)}, subgroup={sum(isinstance(pipeline, type(self)) for pipeline in self._pipelines)})"
	def __eq__(self, other):
		if not isinstance(other, type(self)):
			return NotImplemented
		return self._pipelines == other._pipelines
