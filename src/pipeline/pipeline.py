from .stack import Stack
from collections.abc import Mapping
import threading
class Pipeline:
	"""A simple asynchronous pipeline for executing callable steps sequentially.

	Each step is represented by a tuple containing a callable and optional positional and keyword arguments:

		(function,)
		(function, args)
		(function, kwargs)
		(function, args, kwargs)

	Where ``args`` must be a tuple or mapping, and ``kwargs`` must be a mapping.
	The pipeline always passes the result of the previous step as the first positional argument to the next step.
	The pipeline is snapshotted when execution starts, so modifications to the pipeline after ``run()`` has started do not affect the current execution.

	Args:
		iterable: An iterable of pipeline steps. Defaults to an empty pipeline.

	Attributes:
		stop_event: Event used to request that the worker stop execution.
		skip_event: Event used to request that the next step be skipped.
		pipeline: List containing the configured pipeline steps.
		thread: The worker thread for the current execution, or ``None`` when no execution is active.
		step: The one-based index of the currently executing step, or ``0`` when the pipeline is not running.
		results: Stack containing the initial value and results produced by executed steps.
		errors: Stack containing exceptions raised by executed steps.

	Example:
		>>> def add(value, amount):
			...     return value + amount

		>>> pipeline = Pipeline([
		...     (add, (5,)),
		...     (add, (10,)),
		... ])
		>>> pipeline.run(0)
		>>> pipeline.wait()
		>>> pipeline.results.get()
		15
	"""
	def __init__(self, iterable=()):
		"""Initialize a pipeline.

		Args:
			iterable: An iterable containing pipeline steps.

		Raises:
			TypeError: If any item in ``iterable`` is not a valid step.
		"""
		iterable = tuple(iterable)
		self.stop_event = threading.Event()
		self.skip_event = threading.Event()
		self.pipeline = []
		self.thread = None
		self.step = 0
		self.results = Stack()
		self.errors = Stack()
		for step in iterable:
			self._validate_step(step)
			self.pipeline.append(step)
	def _validate_step(self, step):
		if not step or not isinstance(step, tuple):
			raise TypeError("Invalid step format.")
		if not callable(step[0]):
			raise TypeError("Invalid step format.")
		if len(step) > 3:
			raise TypeError("Invalid step format.")
		if len(step) >= 2 and not isinstance(step[1], (tuple, Mapping)):
			raise TypeError("Invalid step format.")
		if len(step) == 3 and not isinstance(step[1], tuple):
			raise TypeError("Invalid step format.")
		if len(step) == 3 and not isinstance(step[2], Mapping):
			raise TypeError("Invalid step format.")
	def _execute_step(self, step, default):
		if len(step) == 1:
			return step[0](default)
		if isinstance(step[1], tuple):
			return step[0](default, *step[1], **step[2]) if len(step) > 2 else step[0](default, *step[1])
		return step[0](default, **step[1])
	def run(self, default=None, delay=0, daemon=False, stop_on_error=True):
		"""Run the pipeline asynchronously in a worker thread.

		The supplied ``default`` value is stored as the initial result.
		Each step receives the result of the preceding step as its first positional argument.

		The pipeline is snapshotted when execution starts, so modifications to ``self.pipeline`` do not affect the current execution.
		Execution stops when all steps have completed, ``stop()`` is called, or an exception is raised while ``stop_on_error`` is enabled.

		Args:
			default: Initial value passed to the first step.
				Defaults to ``None``.
			delay: Delay in seconds between steps. Must be a non-negative integer or floating-point number.
				Defaults to ``0``.
			daemon: Whether the worker thread should be a daemon thread.
				Defaults to ``False``.
			stop_on_error: Whether execution should stop after the first exception.
				Defaults to ``True``.

		Returns:
			This pipeline instance.

		Raises:
			TypeError: If ``delay`` is not an integer or floating-point number.
			ValueError: If ``delay`` is negative.
			RuntimeError: If the pipeline is already running.
		"""
		if not isinstance(delay, (int, float)):
			raise TypeError("Delay is not int or float.")
		if delay < 0:
			raise ValueError("Delay cannot be negative.")
		if self.running:
			raise RuntimeError("Pipeline is already running.")
		self.stop_event.clear()
		self.skip_event.clear()
		pipeline = tuple(self.pipeline)
		self.step = 0
		self.results.clear()
		self.results.push(default)
		self.errors.clear()
		def worker():
			for index, step in enumerate(pipeline):
				if self.stop_event.is_set():
					break
				self.step = index + 1
				if self.skip_event.is_set():
					self.skip_event.clear()
					continue
				try:
					self.results.push(self._execute_step(step, self.results.get()))
				except Exception as error:
					self.errors.push(error)
					if stop_on_error:
						break
				if delay:
					self.stop_event.wait(delay)
			if not self.stop_event.is_set():
				self.step = 0
			self.thread = None
		self.thread = threading.Thread(target=worker, daemon=daemon)
		self.thread.start()
		return self
	def run_step(self, step, default):
		"""Execute a single pipeline step synchronously.

		This method does not create or modify the worker thread and does not store the result or exception in the pipeline's ``results`` or ``errors`` stacks.
		Exceptions are allowed to propagate to the caller.

		Args:
			step: One-based index of the pipeline step to execute.
			default: Value passed to the selected step as its first argument.

		Returns:
			The value returned by the selected step.

		Raises:
			TypeError: If ``step`` is not an integer.
			ValueError: If ``step`` is less than ``1``.
			IndexError: If ``step`` is outside the pipeline.
			RuntimeError: If the pipeline is currently running.
		"""
		if not isinstance(step, int):
			raise TypeError("Step is not int.")
		if step < 1:
			raise ValueError("Step < 1.")
		if not 1 <= step <= len(self.pipeline):
			raise IndexError("Step out of pipeline.")
		if self.running:
			raise RuntimeError("Pipeline is already running.")
		step = self.pipeline[step - 1]
		return self._execute_step(step, default)
	def stop(self):
		"""Request the running pipeline to stop and wait for termination.

		Returns:
			The one-based index of the step at which execution was stopped, or ``0`` if the pipeline was not running.
		"""
		if self.thread is not None and self.running:
			self.stop_event.set()
			self.thread.join()
			step = self.step
			self.step = 0
			return step
		return 0
	def skip(self):
		"""Request the currently running pipeline to skip its next step.

		If the worker has not yet checked the skip event, the next step that reaches the worker's skip check will be skipped.

		Returns:
			This pipeline instance.
		"""
		if self.thread is not None and self.running:
			self.skip_event.set()
		return self
	def wait(self):
		"""Wait until the currently running pipeline finishes.

		This method blocks only when the pipeline is running.

		Returns:
			This pipeline instance.
		"""
		if self.thread is not None and self.running:
			self.thread.join()
		return self
	def rerun(self, *args, **kwargs):
		"""Stop the current execution and start the pipeline again.

		All arguments are passed directly to :meth:`run`.

		Returns:
			This pipeline instance.
		"""
		self.stop()
		self.run(*args, **kwargs)
		return self
	@property
	def running(self):
		"""Whether the pipeline currently has a running worker thread."""
		return self.thread is not None and self.thread.is_alive()
	def add(self, step):
		"""Append a validated step to the pipeline.

		Args:
			step: The step to append.

		Raises:
			TypeError: If ``step`` has an invalid format.
		"""
		self._validate_step(step)
		self.pipeline.append(step)
	def insert(self, index, step):
		"""Insert a validated step at the specified index.

		Args:
			index: One-based position at which to insert the step.
			step: The step to insert.

		Raises:
			TypeError: If ``index`` is not an integer or ``step`` is invalid.
			IndexError: If ``index`` is outside the pipeline.
		"""
		if not isinstance(index, int):
			raise TypeError(f"{index} is not int.")
		if not 1 < index <= len(self.pipeline) + 1:
			raise IndexError("Index out of range.")
		self._validate_step(step)
		self.pipeline.insert(index - 1, step)
	def pop(self, index):
		"""Remove and return the step at the specified index.

		Args:
			index: One-based index of the step to remove.

		Returns:
			The removed pipeline step.

		Raises:
			TypeError: If ``index`` is not an integer.
			IndexError: If ``index`` is outside the pipeline.
		"""
		if not isinstance(index, int):
			raise TypeError(f"{index} is not int.")
		if not 1 <= index <= len(self.pipeline):
			raise IndexError("Index out of range.")
		return self.pipeline.pop(index - 1)
	def clear(self):
		"""Remove all steps from the pipeline."""
		self.pipeline.clear()
	def _format_step(self, step):
		func = step[0]
		if len(step) >= 2:
			args = step[1]
		else:
			args = ()
		if isinstance(args, tuple):
			parts = [repr(arg) for arg in args]
			if len(step) == 3:
				parts.extend(f"{key}={value!r}" for key, value in step[2].items())
		else:
			parts = [f"{key}={value!r}" for key, value in args.items()]
		return f"{func.__name__}({', '.join(parts)})"
	def __str__(self):
		"""Return a human-readable representation of the pipeline."""
		return " | ".join(self._format_step(step) for step in self.pipeline)
	def __repr__(self):
		"""Return the developer-oriented representation of the pipeline."""
		return f"{type(self).__name__}(total_steps={len(self.pipeline)}, current_step={self.step}, running={self.running})"
	def __bool__(self):
		"""Return whether the pipeline is currently running."""
		return self.running
	def __call__(self, *args, **kwargs):
		"""Run the pipeline.

		Arguments are passed directly to :meth:`run`.

		Returns:
			This pipeline instance.
		"""
		return self.run(*args, **kwargs)
	def __contains__(self, item):
		"""Return whether a callable exists as a pipeline step.

		Identity comparison is used, so the callable must be the exact same object as the callable stored in the step.

		Args:
			item: Callable to search for.

		Returns:
			``True`` if the callable is present, otherwise ``False``.
		"""
		return any(step[0] is item for step in self.pipeline)
	def __len__(self):
		"""Return the number of configured pipeline steps."""
		return len(self.pipeline)