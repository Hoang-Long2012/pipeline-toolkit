# Changelog

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
