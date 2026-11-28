# Concurrency & Coordination

## Run in a Worker Thread

`Pipeline.run()` starts a worker thread and returns immediately. `wait()` blocks until completion. A timeout only limits how long the caller waits; it does not stop the worker.

```python
from pipeline import Pipeline

pipeline = Pipeline([(lambda value: value + 1,)])
pipeline.run(10)
pipeline.wait()
print(pipeline.result)  # 11
```

`stop()` requests a stop and waits for the current step to finish; it does not interrupt a running callable. `skip()` requests that the next step reaching the worker's skip check be skipped.

## Coordinate a Group

`Group` starts each contained pipeline and forwards the same arguments to each `run()` call. Each pipeline runs in its own worker thread; values are not passed from one group member to another.

```python
from pipeline import Group, Pipeline

double = Pipeline([(lambda value: value * 2,)])
increment = Pipeline([(lambda value: value + 1,)])

group = Group([double, increment])
group.run(10).wait()

print(double.result)  # 20
print(increment.result)  # 11
```

A group can also contain nested groups. Its `wait()` and `stop()` methods apply to every contained pipeline and sub-group.

## Pause at a Checkpoint

Use `Checkpoint` as a step when another part of the program needs to inspect an intermediate value before the pipeline continues. The checkpoint stores the value and blocks the worker until `next()` releases it.

```python
from pipeline import Checkpoint, Pipeline

checkpoint = Checkpoint()
pipeline = Pipeline([
    (lambda value: value * 2,),
    (checkpoint,),
    (lambda value: value + 1,),
])

pipeline.run(10)
checkpoint.wait()
print(checkpoint.value)  # 20

checkpoint.next()
pipeline.wait()
print(pipeline.result)  # 21
```

`Checkpoint.wait()` blocks until a checkpoint is active. `next()` releases the current pause; the checkpoint then returns the published value to the next pipeline step.

## Use a Context Manager

Entering a `Pipeline` context starts it if it is not already running. Exiting calls `stop()`. This is a regular synchronous context manager, not an `async with` interface.

```python
pipeline = Pipeline([(lambda value: value + 1,)], default=0)

with pipeline:
    pipeline.wait()

print(pipeline.result)  # 1
```

See the [Group API](../api/Group.md) and [Checkpoint API](../api/Checkpoint.md).
