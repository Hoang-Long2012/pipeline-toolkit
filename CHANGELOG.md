# Changelog

## 0.5.1
- Added `Pipeline.index()` to return the one-based index of the first matching pipeline step.
- Added `Pipeline.count()` to return the number of occurrences of a pipeline step.
- Improved `Pipeline.__str__()` to include the pipeline's `name` and `default` value at the beginning of the representation.
- Fixed `Pipeline.__str__()` raising an `AttributeError` when the pipeline contains a callable object without a `__name__` attribute.
- Fixed `Pipeline.name` accepting empty strings. The `name` parameter and setter now raise `ValueError` when given an empty string.

## 0.5.0
- Changed `Pipeline.error` from a property to a method. Call `error()` to re-raise the latest exception, or `error(reraise=False)` to retrieve it without re-raising.
- Renamed the `run_step()` parameter from `step` to `index` to clarify that it refers to the one-based position of the pipeline step.

## 0.4.1
- Added `Pipeline.__init__()` parameter `run_kwargs` for passing keyword arguments to `run()` when `run_now` is enabled.
- Added `name` parameter to `Pipeline` for assigning a name to worker threads.
- Added `step.default` for configuring the default value used by `step.__mul__()` and `step.__gt__()`.
- Improved `Pipeline.__repr__()` to include the pipeline name and default value.

## 0.4.0
- Changed `Pipeline.__bool__()` to return whether the pipeline contains configured steps instead of whether it is currently running.
- Changed `Pipeline.init()` parameters `run_now` and `run_args` to be keyword-only.
- Added `Stack.put()` and `Stack.peek()` as compatibility aliases for `Stack.push()` and `Stack.get()`.
- Added a `maxsize` property to `Stack` for getting and setting the maximum stack capacity.
- Added support for `reversed(Stack)`, iterating from bottom to top.
- Added `Pipeline.reverse()` for in-place reversal of pipeline steps.
- Added `reversed(Pipeline)` support for iterating over pipeline steps in reverse order.
- Added `Pipeline.update()` for adding multiple pipeline steps at once with full validation before insertion.
- Added support for appending a single step with the `+=` operator.
- Added support creating a new pipeline by concatenating steps with the `+` operator.
- Added support prepending pipeline steps with the `+` operator.
- Added support comparing pipeline configurations with the `==` operator.
- Added support repeating pipeline steps with the `*` operator.
- Added module-level docstrings describing the purpose of each module.
- Improved error messages for invalid pipeline steps to provide more specific validation details.

## 0.3.2
- Changed `Stack` iteration order to iterate from top to bottom, yielding the most recently pushed item first.
- Added `Pipeline.copy()`, `__copy__()`, and `__deepcopy__()` to support shallow and deep copying of pipeline configuration without copying execution state.
- First stable API release.

## 0.3.1
- Documentation-only release: Edited features list in readme.

## 0.3.0
- Removed `Pipeline.wait(reraise_exception)` and exception re-raising from `Pipeline.wait()`.
- Added iteration support to `Pipeline`, allowing pipeline steps to be iterated in their configured order.
- Added `Pipeline.result` property to retrieve the most recent pipeline result.
- Added Pipeline.error property to raise the most recent exception raised by a pipeline step when accessed.
- Added `run_now` and `run_args` parameters to `Pipeline` to support automatically starting the pipeline with custom `run()` arguments during initialization.
- Added one-based indexed access, replacement, and removal of pipeline steps through `Pipeline.__getitem__()`, `Pipeline.__setitem__()`, and `Pipeline.__delitem__()`.
- Added `Pipeline.remove()` to remove the first matching step.
- Added `Pipeline.discard()` to remove the first matching step without raising `ValueError` when absent.
- Added `Pipeline.execute()` for synchronously executing an individual pipeline step without starting the worker thread or modifying execution results and errors.
- Changed `Pipeline.run_step()` signature to make the `default` argument optional, defaulting to `None`.

## 0.2.4
- Documentation-only release: Fix heading level in README.

## 0.2.3
- Added context manager support to `Pipeline` for automatically starting and stopping pipeline execution.
- Added `step.export()` for converting a `step` object to the standard pipeline step format.
- Added support for unpacking `step` objects into pipeline step tuples.

## 0.2.2
- Improved `Pipeline.run()` default handling with an internal sentinel, allowing `None` to be passed explicitly.
- Added `reraise_exception` support to `Pipeline.wait()` for propagating worker exceptions to the calling thread.
- Improved `Pipeline` documentation for delay, error handling, and default values.
- Added an initial cancellation window before the first pipeline step when `delay` is enabled.

## 0.2.1
- Code cleanup.

## 0.2.0
- Added `compose()` for sequential callable composition.
- Added `pipe` as a callable step factory.
- Added `step` for wrapping callables with preconfigured arguments.
- Added configurable pipeline defaults.
- Fixed `Pipeline.insert()` index validation for inserting at the end of the pipeline.

## 0.1.0
- First release version.
