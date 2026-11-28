# Async pipelines

## Worker-thread execution

`Pipeline.run()` starts execution in a worker thread and returns immediately. It is not an `async`/`await` API. Call `wait()` to block until the pipeline finishes:

```python
from pipeline import Pipeline

pipeline = Pipeline([
    (lambda value: value + 1,),
    (lambda value: value * 2,),
])

pipeline.run(20)
pipeline.wait()

print(pipeline.result)  # 42
```

`wait(timeout=...)` returns the pipeline even if the timeout expires; the worker continues running. `result` raises `RuntimeError` while execution is active.

## Pipeline context manager

Entering a pipeline context starts it if it is not already running. Exiting the context calls `stop()`, which requests a stop and waits for the worker to terminate. An active step is not forcibly interrupted.

```python
from pipeline import Pipeline

pipeline = Pipeline([(lambda value: value + 1,)], default=0)

with pipeline:
    pipeline.wait()

print(pipeline.result)  # 1
```

The context manager does not suppress exceptions raised in the `with` body.

## Checkpoints

Use `Checkpoint` as a step to publish the current value and pause the worker until `next()` is called. `wait()` blocks until a checkpoint is active, and `value` exposes the most recently published value.

```python
from pipeline import Checkpoint, Pipeline

checkpoint = Checkpoint()
pipeline = Pipeline([
    (checkpoint,),
    (lambda value: value + 1,),
])

pipeline.run(41)
checkpoint.wait()
print(checkpoint.value)  # 41

checkpoint.next()
pipeline.wait()
print(pipeline.result)  # 42
```

`Checkpoint` passes the same value through after it is released. See the [Checkpoint API](../api/Checkpoint.md) for its state properties.

## Errors

By default, a step exception derived from `Exception` is recorded and stops the run. `pipeline.errors` contains caught step exceptions. `pipeline.error(reraise=False)` returns the most recent one; `pipeline.error()` raises it.

With `stop_on_error=False`, execution continues after a failed step. The failed step does not add a result, so the next step receives the last successful value. An optional `error_handler` receives an `ErrorContext` with the failed step's one-based index, step tuple, exception, and input value.

```python
from pipeline import Pipeline

def fail(value):
    raise ValueError("invalid record")

def continue_processing(value):
    return {"value": value, "status": "needs review"}

errors = []
pipeline = Pipeline([(fail,), (continue_processing,)])

pipeline.run(
    {"id": 7},
    stop_on_error=False,
    error_handler=errors.append,
).wait()

print(pipeline.result)  # {"value": {"id": 7}, "status": "needs review"}
print(errors[0].index)  # 1
```

Exceptions raised by the error handler are not caught by the pipeline.
