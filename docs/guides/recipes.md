# Recipes

## Normalize and audit a record

Use `tap` to inspect a deep copy without changing the value flowing through the pipeline. Use `mut` when a step should intentionally update that value in place.

```python
from pipeline import Pipeline, mut, tap

audit_log = []

def normalize(record):
    result = dict(record)
    result["name"] = result["name"].strip().title()
    return result

def add_status(record):
    record["status"] = "processed"

def record_audit(record_copy):
    audit_log.append(record_copy)

pipeline = Pipeline([
    (normalize,),
    (mut, (add_status,)),
    (tap, (record_audit,)),
])

pipeline.run({"name": "  ada lovelace  "}).wait()

print(pipeline.result)
# {"name": "Ada Lovelace", "status": "processed"}
print(audit_log[0]["status"])  # "processed"
```

The audit callback receives a deep copy; edits it makes do not affect `pipeline.result`.

## Reuse a transformation

Calling a pipeline object runs it synchronously, so the same configured pipeline can process multiple inputs:

```python
from pipeline import Pipeline

normalize = Pipeline([
    (str.strip,),
    (str.casefold,),
])

names = [normalize(name) for name in [" Ada ", "GRACE"]]
print(names)  # ["ada", "grace"]
```

## Continue after a failed operation

When `stop_on_error=False`, the next step receives the last successful value after a failure. An error handler can record the failure while a later step prepares the value for retry:

```python
from pipeline import Pipeline

def send_to_service(record):
    raise ConnectionError("service unavailable")

def queue_for_retry(record):
    return {**record, "status": "queued"}

failures = []
pipeline = Pipeline([
    (send_to_service,),
    (queue_for_retry,),
])

pipeline.run(
    {"id": 12},
    stop_on_error=False,
    error_handler=failures.append,
).wait()

print(pipeline.result)  # {"id": 12, "status": "queued"}
print(type(failures[0].error).__name__)  # "ConnectionError"
```

See [Async pipelines](async-pipelines.md#errors) for the recorded error details and continuation behavior.
