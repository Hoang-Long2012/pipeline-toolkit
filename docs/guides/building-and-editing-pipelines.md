# Building & Editing Pipelines

## Step Structure

A step is a tuple containing a callable and optional configured arguments. The current pipeline value is always passed as the callable's first positional argument.

```python
def format_price(value, currency="$", precision=2):
    return f"{currency}{value:.{precision}f}"

steps = [
    (format_price,),
    (format_price, ("$",)),
    (format_price, {"currency": "$", "precision": 0}),
    (format_price, ("$",), {"precision": 0}),
]
```

The second item is either a tuple of positional arguments or a mapping of keyword arguments. When both are provided, the second item must be a tuple and the third must be a mapping.

## Edit the Configuration

Pipelines are mutable. Use `add`, `insert`, and `update` to append or insert steps; use `remove`, `discard`, `pop`, `clear`, or item assignment to remove or replace them.

```python
from pipeline import Pipeline

def add(value, amount):
    return value + amount

pipeline = Pipeline([(add, (1,))])
pipeline.add((add, (2,)))
pipeline.insert(1, (add, (10,)))
pipeline[2] = (add, (5,))

pipeline.run(0).wait()
print(pipeline.result)  # 17
```

Pipeline indexes are one-based: `pipeline[1]` is the first step. The `steps` property returns a deep copy; changing that returned list does not edit the pipeline.

## Reuse and Derive Pipelines

A pipeline can run again with a new initial value. Each call to `run()` clears the previous run's `results`, `calls`, and `errors`.

Use `pipeline + steps` to create a new pipeline with additional steps without changing the original:

```python
extended = pipeline + [(add, (3,))]
```

## Execution Snapshot

When `run()` starts, the pipeline captures a shallow copy of its step list. Adding, removing, or replacing steps afterward does not change the sequence for that run. The step tuples and their contents are not deep-copied; mutable objects stored in positional or keyword arguments are shared with the active run.

See the [Pipeline API](../api/Pipeline.md) for the complete editing interface.
