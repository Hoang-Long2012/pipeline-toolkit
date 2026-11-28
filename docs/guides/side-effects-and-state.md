# Side Effects & State

## Mutate a Value Intentionally

`mut(value, function, ...)` passes the original value to a function for in-place changes. It ignores the function's return value and returns the original value, so the value continues through the pipeline:

```python
from pipeline import Pipeline, mut

def add_status(record):
    record["status"] = "processed"

pipeline = Pipeline([(mut, (add_status,))])
pipeline.run({"id": 12}).wait()
print(pipeline.result)  # {"id": 12, "status": "processed"}
```

## Observe Without Changing the Pipeline Value

`tap(value, function, ...)` passes a deep copy to the function and returns the original value. Mutations made by the callback do not change the value flowing through the pipeline.

```python
from pipeline import Pipeline, tap

audit_log = []
pipeline = Pipeline([(tap, (audit_log.append,))])
record = {"id": 12}

pipeline.run(record).wait()
print(pipeline.result is record)  # True
print(audit_log[0] is record)  # False
```

Both helpers propagate exceptions raised by their callback.

## Inspect Execution State

After a run completes:

- `pipeline.result` returns the latest successful result, or the initial value if no step succeeded.
- `pipeline.results` is a LIFO `Stack` containing the initial value and successful step results. Iteration yields the newest value first.
- `pipeline.calls` contains the successfully executed steps, newest first.
- `pipeline.errors` contains caught step exceptions, newest first.

Starting another run clears these execution stacks. Read `result` only after execution has stopped; it raises `RuntimeError` while the pipeline is running.

See the [`mut`](../api/mut.md), [`tap`](../api/tap.md), and [Stack API](../api/Stack.md) references for details.
