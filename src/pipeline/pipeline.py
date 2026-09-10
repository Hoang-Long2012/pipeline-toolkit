import threading
from collections.abc import Mapping

from ._compat import _DEFAULT
from .stack import Stack


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
		default: The value used for the first step when ``run()`` is called without an explicit ``default``.

	Attributes:
		step: The one-based index of the currently executing step, or ``0`` when the pipeline is not running.
		default: The value used for the first step when ``run()`` is called without an explicit ``default``.
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
	def __init__(self, iterable=(), default=None, run_now=False, run_args=()):
		"""Initialize a pipeline.

		Args:
			iterable: An iterable containing pipeline steps.
				Defaults to an empty pipeline.
			default: The value used for the first step when ``run()`` is called without an explicit ``default``.
				Default to ``None``.
			run_now: Whether to start the pipeline immediately after initialization.
				Defaults to ``False``.
			run_args: A tuple of positional arguments passed to ``run()`` when ``run_now`` is enabled.
				Defaults to ``()``.

		Raises:
			TypeError: If any item in ``iterable`` is not a valid step, or if ``run_args`` is not a tuple.
		"""
		iterable = tuple(iterable)
		self.stop_event = threading.Event()
		self.skip_event = threading.Event()
		self.pipeline = []
		self.thread = None
		self.step = 0
		self.results = Stack()
		self.errors = Stack()
		self.default = default
		for step in iterable:
			self._validate_step(step)
			self.pipeline.append(step)
		if run_now:
			if not isinstance(run_args, tuple):
				raise TypeError("run_args is not a tuple.")
			self.run(*run_args)
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
	def run(self, default=_DEFAULT, delay=0, daemon=False, stop_on_error=True):
		"""Run the pipeline asynchronously in a worker thread.

		The supplied ``default`` value is stored as the initial result.
		Each step receives the result of the preceding step as its first positional argument.

		The pipeline is snapshotted when execution starts, so modifications to ``self.pipeline`` do not affect the current execution.
		Execution stops when all steps have completed, ``stop()`` is called, or an exception is raised while ``stop_on_error`` is enabled.

		Args:
			default: The initial value passed to the first step.
				If omitted, the pipeline's ``default`` value is used.
				``None`` may be passed explicitly.
			delay: Delay in seconds before the first step and between subsequent steps.
				Must be a non-negative integer or floating-point number.
				Defaults to ``0``.
			daemon: Whether the worker thread should be a daemon thread.
				Defaults to ``False``.
			stop_on_error: Whether execution should stop after the first exception.
				When disabled, the failed step's result is not added to ``results``, and execution continues with the previous result.
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
		self.results.push(default if default is not _DEFAULT else self.default)
		self.errors.clear()
		def worker():
			if delay:
				self.stop_event.wait(delay)
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
				if delay and index < len(pipeline) - 1:
					self.stop_event.wait(delay)
			if not self.stop_event.is_set():
				self.step = 0
			self.thread = None
		self.thread = threading.Thread(target=worker, daemon=daemon)
		self.thread.start()
		return self
	def run_step(self, step, default=None):
		"""Execute a single pipeline step synchronously.

		This method does not create or modify the worker thread and does not store the result or exception in the pipeline's ``results`` or ``errors`` stacks.
		Exceptions are allowed to propagate to the caller.

		Args:
			step: One-based index of the pipeline step to execute.
			default: Value passed to the selected step as its first argument.
				Default to ``None``.

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
	def execute(self, step, default=None):
		"""Execute a pipeline step synchronously.

		This method validates and executes the specified step directly.
		It does not create or modify the worker thread and does not store the result or exception in the pipeline's ``results`` or ``errors`` stacks.
		Exceptions are allowed to propagate to the caller.

		Args:
			step: The pipeline step to execute.
			default: Value passed to the step as its first argument.
				Default to ``None``.

		Returns:
			The value returned by the step.

		Raises:
			TypeError: If ``step`` has an invalid format.
			RuntimeError: If the pipeline is currently running.
		"""
		self._validate_step(step)
		if self.running:
			raise RuntimeError("Pipeline is already running.")
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

		This method blocks only while the pipeline is running.

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
	@property
	def result(self):
		"""Return the most recent result of the pipeline.

		The initial value is considered the result when no pipeline step has successfully completed.

		Returns:
			The initial value or the result produced by the last successfully executed step.
			``None`` if the pipeline has not been run yet.

		Raises:
			RuntimeError: If the pipeline is currently running.
		"""
		if self.running:
			raise RuntimeError("Pipeline is already running.")
		if self.results:
			return self.results.get()
	@property
	def error(self):
		"""Raise the most recent exception raised by the pipeline, if any.

		Returns:
			``None`` if no exception was raised by the pipeline.

		Raises:
			RuntimeError: If the pipeline is currently running.
			Exception: The most recent exception raised by a pipeline step.
		"""
		if self.running:
			raise RuntimeError("Pipeline is already running.")
		if self.errors:
			raise self.errors.get()
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
		if not 1 <= index <= len(self.pipeline) + 1:
			raise IndexError("Index out of range.")
		self._validate_step(step)
		self.pipeline.insert(index - 1, step)
	def remove(self, step):
		"""Remove the first matching step from the pipeline.

		Args:
			step: The pipeline step to remove.

		Raises:
			TypeError: If ``step`` has an invalid format.
			ValueError: If ``step`` is not found in the pipeline.
		"""
		self._validate_step(step)
		for index, pipeline_step in enumerate(self.pipeline):
			if pipeline_step == step:
				del self.pipeline[index]
				return None
		raise ValueError("Step not found in pipeline.")
	def discard(self, step):
		"""Remove the first matching step from the pipeline if present.

		If the step is not found, the pipeline is left unchanged.

		Args:
			step: The pipeline step to remove.

		Raises:
			TypeError: If ``step`` has an invalid format.
		"""
		try:
			self.remove(step)
		except ValueError:
			pass
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
	def __getitem__(self, index):
		"""Return the pipeline step at the specified index.

		Args:
			index: One-based index of the pipeline step to retrieve.

		Returns:
			The pipeline step at the specified index.

		Raises:
			TypeError: If ``index`` is not an integer.
			IndexError: If ``index`` is outside the pipeline.
		"""
		if not isinstance(index, int):
			raise TypeError(f"{index} is not int.")
		if not 1 <= index <= len(self.pipeline):
			raise IndexError("Index out of range.")
		return self.pipeline[index - 1]
	def __setitem__(self, index, step):
		"""Replace the pipeline step at the specified index.

		Args:
			index: One-based index of the pipeline step to replace.
			step: The new pipeline step.

		Raises:
			TypeError: If ``index`` is not an integer or ``step`` is invalid.
			IndexError: If ``index`` is outside the pipeline.
		"""
		if not isinstance(index, int):
			raise TypeError(f"{index} is not int.")
		if not 1 <= index <= len(self.pipeline):
			raise IndexError("Index out of range.")
		self._validate_step(step)
		self.pipeline[index - 1] = step
	def __delitem__(self, index):
		"""Remove the pipeline step at the specified index.

		Args:
			index: One-based index of the pipeline step to remove.

		Raises:
			TypeError: If ``index`` is not an integer.
			IndexError: If ``index`` is outside the pipeline.
		"""
		if not isinstance(index, int):
			raise TypeError(f"{index} is not int.")
		if not 1 <= index <= len(self.pipeline):
			raise IndexError("Index out of range.")
		del self.pipeline[index - 1]
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
	def __iter__(self):
		"""Iterate over the configured pipeline steps.

		Yields:
			Each pipeline step in its configured order.
		"""
		yield from self.pipeline
	def __enter__(self):
		"""Enter the context manager and start the pipeline if it is not running.

		Returns:
			This pipeline instance.
		"""
		if not self.running:
			self.run()
		return self
	def __exit__(self, exc_type, exc_value, traceback):
		"""Exit the context manager and stop the pipeline."""
		self.stop()