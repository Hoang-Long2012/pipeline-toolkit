# Error Handling

## Default Behavior

The default `stop_on_error=True` stops execution after the first step raises an exception derived from `Exception`. The pipeline records that exception in `errors`; the current step's result is not added to `results`.

After the run completes, `pipeline.error()` raises the most recent recorded exception. Use `pipeline.error(reraise=False)` to return it instead; this returns `None` if no step exception was recorded.

## Continue After a Failure

Set `stop_on_error=False` to continue with the next step after a failure. The failed step does not produce a result, so the next step receives the last successful value:

```python
from pipeline import Pipeline

def send_to_service(record):
    raise ConnectionError("service unavailable")

def queue_for_retry(record):
    return {**record, "status": "queued"}

pipeline = Pipeline([
    (send_to_service,),
    (queue_for_retry,),
])

pipeline.run({"id": 12}, stop_on_error=False).wait()
print(pipeline.result)  # {"id": 12, "status": "queued"}
```

## Record Failure Details

Pass an `error_handler` to `run()` to receive an `ErrorContext` for each caught step exception. It contains the one-based step index, the failed step tuple, the exception, and the value passed to the failed step.

```python
from pipeline import Pipeline

failures = []

def record_failure(context):
    failures.append({
        "index": context.index,
        "error": context.error,
        "value": context.previous_result,
    })

def validate(value):
    raise ValueError("invalid input")

pipeline = Pipeline([(validate,)])
pipeline.run("sample", error_handler=record_failure).wait()

print(failures[0]["index"])  # 1
print(type(failures[0]["error"]).__name__)  # "ValueError"
```

An exception raised by the error handler is not caught by the pipeline. Exceptions derived from `BaseException` but not `Exception` are also not caught as step errors.

See the [Pipeline API](../api/Pipeline.md) for `run()`, `errors`, and `error()` details.
