# Changelog

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
