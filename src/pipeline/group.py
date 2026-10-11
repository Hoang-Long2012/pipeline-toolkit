from .pipeline import Pipeline


class Group:
	def __init__(self, iterable=()):
		self._pipelines = []
		for pipeline in iterable:
			if not isinstance(pipeline, (Pipeline, type(self))):
				raise TypeError(f"{pipeline} is not a Pipeline or Group.")
			self._pipelines.append(pipeline)
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
		if not isinstance(pipeline, (Pipeline, type(self))):
			raise TypeError("pipeline is not a Pipeline or Group.")
		self._pipelines.append(pipeline)
	def insert(self, index, pipeline):
		if not isinstance(index, int):
			raise TypeError("index is not a int.")
		if index < 0:
			raise ValueError("index  not be a negative.")
		if index >= len(self._pipelines):
			raise IndexError("index out of range.")
		if not isinstance(pipeline, (Pipeline, type(self))):
			raise TypeError("pipeline is not a Pipeline or Group.")
		self._pipelines.insert(index, pipeline)
