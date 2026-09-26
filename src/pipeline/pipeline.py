"""Asynchronous pipeline for sequentially executing callable steps."""
import copy
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

	Where ``args`` may be a tuple or mapping when used alone, but must be a tuple when ``kwargs`` is provided.
	The pipeline always passes the result of the previous step as the first positional argument to the next step.
	The pipeline is snapshotted when execution starts, so modifications to the pipeline after ``run()`` has started do not affect the current execution.

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
	def __init__(self, iterable=(), default=None, name=None, *, run_now=False, run_args=(), run_kwargs=None):
		"""Initialize a pipeline.

		Args:
			iterable: An iterable containing pipeline steps.
				Defaults to an empty pipeline.
			default: The value used for the first step when `run()` is called without an explicit `default`.
				Defaults to ``None``.
			name: The name assigned to the worker thread and pipeline.
				Must be a non-empty string or ``None``.
				Defaults to ``None``.
			run_now: Whether to start the pipeline immediately after initialization.
				Defaults to ``False``.
			run_args: A tuple of positional arguments passed to `run()` when `run_now` is enabled.
				Defaults to ``()``.
			run_kwargs: A mapping of keyword arguments passed to `run()` when `run_now` is enabled.
				Defaults to ``None``.

		Raises:
			TypeError: If any item in `iterable` is not a valid step, if ``name`` is not a string or ``None``, if ``run_args`` is not a tuple, or if ``run_kwargs`` is not a mapping.
			ValueError: If ``name`` is an empty string.
		"""
		iterable = tuple(iterable)
		self._stop_event = threading.Event()
		self._skip_event = threading.Event()
		self._steps = []
		self._thread = None
		self._step = 0
		self.results = Stack()
		self.errors = Stack()
		self._default = default
		if name is not None and not isinstance(name, str):
			raise TypeError("name is not a str.")
		if name is not None and not name:
			raise ValueError("name cannot be an empty string.")
		self._name = name
		for step in iterable:
			self._validate_step(step)
			self._steps.append(step)
		if run_now:
			if not isinstance(run_args, tuple):
				raise TypeError("run_args is not a tuple.")
			if run_kwargs is None:
				run_kwargs = {}
			elif not isinstance(run_kwargs, Mapping):
				raise TypeError("run_kwargs is not a Mapping.")
			self.run(*run_args, **run_kwargs)
	def _validate_step(self, step):
		if not isinstance(step, tuple):
			raise TypeError(f"Step must be a tuple, not {type(step).__name__}.")
		if not step:
			raise TypeError("Step cannot be empty.")
		if not callable(step[0]):
			raise TypeError(f"Step function must be callable, not {type(step[0]).__name__}.")
		if len(step) > 3:
			raise TypeError(f"Step must contain at most 3 items, got {len(step)}.")
		if len(step) >= 2:
			if not isinstance(step[1], (tuple, Mapping)):
				raise TypeError(f"Step arguments must be a tuple or mapping, not {type(step[1]).__name__}.")
		if len(step) == 3:
			if not isinstance(step[1], tuple):
				raise TypeError("Step positional arguments must be a tuple when keyword arguments are provided.")
		if len(step) == 3 and not isinstance(step[2], Mapping):
			raise TypeError(f"Step keyword arguments must be a mapping, not {type(step[2]).__name__}.")
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

		The pipeline is snapshotted when execution starts, so modifications to the configured steps do not affect the current execution.
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
		self._stop_event.clear()
		self._skip_event.clear()
		steps = tuple(self._steps)
		self._step = 0
		self.results.clear()
		self.results.push(default if default is not _DEFAULT else self._default)
		self.errors.clear()
		def worker():
			if not steps:
				return None
			if delay:
				self._stop_event.wait(delay)
			for index, step in enumerate(steps):
				if self._stop_event.is_set():
					break
				self._step = index + 1
				if self._skip_event.is_set():
					self._skip_event.clear()
					continue
				try:
					self.results.push(self._execute_step(step, self.results.get()))
				except Exception as error:
					self.errors.push(error)
					if stop_on_error:
						break
				if delay and index < len(steps) - 1:
					self._stop_event.wait(delay)
			if not self._stop_event.is_set():
				self._step = 0
			self._thread = None
		self._thread = threading.Thread(target=worker, name=self._name, daemon=daemon)
		self._thread.start()
		return self
	def run_step(self, index, default=None):
		"""Execute a single pipeline step synchronously.

		This method does not create or modify the worker thread and does not store the result or exception in the pipeline's ``results`` or ``errors`` stacks.
		Exceptions are allowed to propagate to the caller.

		Args:
			index: One-based index of the pipeline step to execute.
			default: Value passed to the selected step as its first argument.
				Defaults to ``None``.

		Returns:
			The value returned by the selected step.

		Raises:
			TypeError: If ``index`` is not an integer.
			ValueError: If ``index`` is less than ``1``.
			IndexError: If ``index`` is outside the pipeline.
			RuntimeError: If the pipeline is currently running.
		"""
		if not isinstance(index, int):
			raise TypeError("index is not int.")
		if index < 1:
			raise ValueError("index < 1.")
		if not 1 <= index <= len(self._steps):
			raise IndexError("index out of pipeline.")
		if self.running:
			raise RuntimeError("Pipeline is already running.")
		step = self._steps[index - 1]
		return self._execute_step(step, default)
	def execute(self, step, default=None):
		"""Execute a pipeline step synchronously.

		This method validates and executes the specified step directly.
		It does not create or modify the worker thread and does not store the result or exception in the pipeline's ``results`` or ``errors`` stacks.
		Exceptions are allowed to propagate to the caller.

		Args:
			step: The pipeline step to execute.
			default: Value passed to the step as its first argument.
				Defaults to ``None``.

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
		if self._thread is not None and self.running:
			self._stop_event.set()
			self._thread.join()
			step = self._step
			self._step = 0
			return step
		return 0
	def skip(self):
		"""Request the currently running pipeline to skip its next step.

		If the worker has not yet checked the skip event, the next step that reaches the worker's skip check will be skipped.

		Returns:
			This pipeline instance.
		"""
		if self._thread is not None and self.running:
			self._skip_event.set()
		return self
	def wait(self):
		"""Wait until the currently running pipeline finishes.

		This method blocks only while the pipeline is running.

		Returns:
			This pipeline instance.
		"""
		if self._thread is not None and self.running:
			self._thread.join()
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
		return self._thread is not None and self._thread.is_alive()
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
	def error(self, reraise=True):
		"""Return or raise the most recent exception raised by the pipeline.

		By default, the exception is raised.
		If ``reraise`` is ``False``, the exception is returned instead.

		Args:
			reraise: Whether to raise the most recent exception.
				Defaults to ``True``.

		Returns:
			The most recent exception if ``reraise`` is ``False``.
			``None`` if no exception was raised.

		Raises:
			RuntimeError: If the pipeline is currently running.
			Exception: The most recent exception raised by a pipeline step when ``reraise`` is ``True``.
		"""
		if self.running:
			raise RuntimeError("Pipeline is already running.")
		if self.errors:
			if reraise:
				raise self.errors.get()
			return self.errors.get()
	def add(self, step):
		"""Append a validated step to the pipeline.

		Args:
			step: The step to append.

		Raises:
			TypeError: If ``step`` has an invalid format.
		"""
		self._validate_step(step)
		self._steps.append(step)
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
		if not 1 <= index <= len(self._steps) + 1:
			raise IndexError("Index out of range.")
		self._validate_step(step)
		self._steps.insert(index - 1, step)
	def update(self, iterable):
		"""Append multiple validated steps to the pipeline.

		All steps are validated before being added, so the pipeline is left unchanged if any step is invalid.

		Args:
			iterable: An iterable of pipeline steps.

		Raises:
			TypeError: If any item in ``iterable`` has an invalid step format.
		"""
		steps = tuple(iterable)
		for step in steps:
			self._validate_step(step)
		self._steps.extend(steps)
	def remove(self, step):
		"""Remove the first matching step from the pipeline.

		Args:
			step: The pipeline step to remove.

		Raises:
			TypeError: If ``step`` has an invalid format.
			ValueError: If ``step`` is not found in the pipeline.
		"""
		self._validate_step(step)
		for index, pipeline_step in enumerate(self._steps):
			if pipeline_step == step:
				del self._steps[index]
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
		if not 1 <= index <= len(self._steps):
			raise IndexError("Index out of range.")
		return self._steps.pop(index - 1)
	def clear(self):
		"""Remove all steps from the pipeline."""
		self._steps.clear()
	def reverse(self):
		"""Reverse the order of pipeline steps in place."""
		self._steps.reverse()
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
		if not 1 <= index <= len(self._steps):
			raise IndexError("Index out of range.")
		return self._steps[index - 1]
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
		if not 1 <= index <= len(self._steps):
			raise IndexError("Index out of range.")
		self._validate_step(step)
		self._steps[index - 1] = step
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
		if not 1 <= index <= len(self._steps):
			raise IndexError("Index out of range.")
		del self._steps[index - 1]
	def copy(self):
		"""Return a shallow copy of the pipeline.

		The pipeline configuration, default value, and name are shallow-copied.
		Execution state, including results, errors, the current step, and the worker thread, is not copied.

		Returns:
			A new pipeline instance with a shallow copy of the configuration.

		Raises:
			RuntimeError: If the pipeline is currently running.
		"""
		return self.__copy__()
	def index(self, step):
		"""Return the one-based index of the first matching pipeline step.

		Args:
			step: The pipeline step to search for.

		Returns:
			The one-based index of the first matching step.

		Raises:
			TypeError: If ``step`` has an invalid format.
			ValueError: If ``step`` is not found in the pipeline.
		"""
		self._validate_step(step)
		for index, pipeline_step in enumerate(self._steps):
			if pipeline_step == step:
				return index + 1
		raise ValueError("Step not found in pipeline.")
	def count(self, step):
		"""Return the number of occurrences of a pipeline step.

		Args:
			step: The pipeline step to count.

		Returns:
			The number of times ``step`` occurs in the pipeline.

		Raises:
			TypeError: If ``step`` has an invalid format.
		"""
		self._validate_step(step)
		total = 0
		for pipeline_step in self._steps:
			if pipeline_step == step:
				total += 1
		return total
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
		name = getattr(func, "__name__", type(func).__name__)
		return f"{name}({', '.join(parts)})"
	def __str__(self):
		"""Return a human-readable representation of the pipeline."""
		pipeline = [f"{self.default!r}"]
		pipeline.extend(self._format_step(step) for step in self._steps)
		if self._name:
			return f"{self._name}: {' | '.join(pipeline)}"
		return " | ".join(pipeline)
	def __repr__(self):
		"""Return the developer-oriented representation of the pipeline."""
		return f"{type(self).__name__}(name={self._name!r}, default={self.default!r}, total_steps={len(self._steps)}, current_step={self.step}, running={self.running})"
	def __bool__(self):
		"""Return whether the pipeline contains any configured steps.

		Returns:
			``True`` if the pipeline contains at least one step, otherwise ``False``.
		"""
		return bool(self._steps)
	def __call__(self, *args, **kwargs):
		"""Run the pipeline.

		Arguments are passed directly to :meth:`run`.

		Returns:
			This pipeline instance.
		"""
		return self.run(*args, **kwargs)
	def __contains__(self, item):
		"""Return whether a callable or step configuration exists in the pipeline.

		Callable items are matched by identity.
		Tuple items must be valid step configurations and are matched against the full configuration.

		Args:
			item: A callable or a step tuple to search for.

		Returns:
			``True`` if the callable or valid step configuration is present in the pipeline, otherwise ``False``.

		Raises:
			TypeError: If ``item`` is not callable or a tuple, or if a tuple is not a valid step.
		"""
		if callable(item):
			return any(step[0] is item for step in self._steps)
		if isinstance(item, tuple):
			self._validate_step(item)
			return any(step == item for step in self._steps)
		raise TypeError("item is not a callable or step.")
	def __len__(self):
		"""Return the number of configured pipeline steps."""
		return len(self._steps)
	def __iter__(self):
		"""Iterate over the configured pipeline steps.

		Yields:
			Each pipeline step in its configured order.
		"""
		yield from self._steps
	def __reversed__(self):
		"""Return an iterator that yields pipeline steps in reverse order.

		Returns:
			An iterator over the pipeline steps in reverse order.
		"""
		return reversed(self._steps)
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
	def __copy__(self):
		"""Create a shallow copy of the pipeline.

		Only the pipeline configuration, default value, and name are copied.
		Execution state, including results, errors, the current step, and the worker thread, is reset in the new pipeline.

		Returns:
			A new pipeline instance with a shallow copy of the configuration.

		Raises:
			RuntimeError: If the pipeline is currently running.
		"""
		if self.running:
			raise RuntimeError("Pipeline is already running.")
		pipeline = copy.copy(self._steps)
		default = copy.copy(self.default)
		name = copy.copy(self._name)
		return type(self)(pipeline, default, name)
	def __deepcopy__(self, memo):
		"""Create a deep copy of the pipeline.

		The pipeline configuration, default value, and name are deep-copied.
		Execution state, including results, errors, the current step, and the worker thread, is reset in the new pipeline.

		Returns:
			A new pipeline instance with a deep copy of the configuration.

		Raises:
			RuntimeError: If the pipeline is currently running.
		"""
		if self.running:
			raise RuntimeError("Pipeline is already running.")
		pipeline = copy.deepcopy(self._steps, memo)
		default = copy.deepcopy(self.default, memo)
		name = copy.deepcopy(self._name, memo)
		return type(self)(pipeline, default, name)
	def __iadd__(self, step):
		"""Append a pipeline step in place.

		This is equivalent to calling :meth:`add` with the specified step.

		Args:
			step: The pipeline step to append.

		Returns:
			This pipeline instance.

		Raises:
			TypeError: If ``step`` has an invalid format.
		"""
		self.add(step)
		return self
	def __add__(self, other):
		"""Return a new pipeline by concatenating pipeline steps.

		The original pipeline and the iterable are not modified.

		Args:
			other: An iterable containing pipeline steps to append.

		Returns:
			A new pipeline containing the steps from this pipeline followed by the steps from ``other``.

		Raises:
			TypeError: If any item in ``other`` has an invalid step format.
		"""
		other = tuple(other)
		return type(self)([*self, *other], self.default, self._name)
	def __radd__(self, other):
		"""Return a new pipeline by prepending iterable steps.

		The original pipeline and the iterable are not modified.

		Args:
			other: An iterable containing pipeline steps to prepend.

		Returns:
			A new pipeline containing the steps from ``other`` followed by the steps from this pipeline.

		Raises:
			TypeError: If any item in ``other`` has an invalid step format.
		"""
		other = tuple(other)
		return type(self)([*other, *self], self.default, self._name)
	def __eq__(self, other):
		"""Return whether two pipelines have equal configurations.

		Two pipelines are considered equal when they have the same pipeline steps, default value, and name.
		Execution state is not considered.

		Args:
			other: The object to compare with.

		Returns:
			``True`` if ``other`` is a pipeline with the same steps, default value, and name, otherwise ``False``.
		"""
		if not isinstance(other, type(self)):
			return NotImplemented
		return isinstance(other, type(self)) and self._steps == other._steps and self.default == other.default and self._name == other._name
	def __mul__(self, count):
		"""Return a new pipeline with its steps repeated.

		The original pipeline is not modified.

		Args:
			count: Number of times to repeat the pipeline steps.
				Must be a positive integer. Non-integer values are unsupported.

		Returns:
			A new pipeline containing the repeated steps.

		Raises:
			ValueError: If ``count`` is less than one.
		"""
		if not isinstance(count, int):
			return NotImplemented
		if count < 1:
			raise ValueError("Count < 1.")
		return type(self)(self._steps * count, self.default, self._name)
	@property
	def name(self):
		"""Return the name of the worker thread and pipeline."""
		return self._name
	@name.setter
	def name(self, name):
		"""Set the name of the worker thread and pipeline.

		Args:
			name: The name to assign to the worker thread and pipeline.
				Must be a non-empty string or ``None``.
				``None`` clears the name.

		Raises:
			TypeError: If ``name`` is not a string or ``None``.
			ValueError: If ``name`` is an empty string.
		"""
		if name is not None and not isinstance(name, str):
			raise TypeError("name is not a str.")
		if name is not None and not name:
			raise ValueError("name cannot be an empty string.")
		self._name = name
	@property
	def step(self):
		"""Return the one-based index of the step currently running, or ``0`` when idle."""
		return self._step
	@property
	def default(self):
		"""Return the default value used when :meth:`run` receives no initial value."""
		return self._default
	@default.setter
	def default(self, value):
		"""Set the default value used when :meth:`run` receives no initial value.

		Args:
			value: The default initial value for pipeline execution.
		"""
		self._default = value
