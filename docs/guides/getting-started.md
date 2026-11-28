# Getting started

`pipeline-toolkit` builds sequential pipelines from ordinary Python callables. A pipeline runs its steps in a worker thread and passes each result to the next step.

## Install

Install the package with pip:

```bash
python -m pip install pipeline-toolkit
```

The package requires Python 3.8 or later and has no runtime dependencies.

## Create and run a pipeline

Each step is a tuple containing a callable and, optionally, its configured arguments:

```python
from pipeline import Pipeline

def add(value, amount):
    return value + amount

def multiply(value, factor):
    return value * factor

pipeline = Pipeline([
    (add, (5,)),
    (multiply, (2,)),
])
```

Start the pipeline with an initial value, wait for the worker to finish, then read the final result:

```python
pipeline.run(10)
pipeline.wait()

print(pipeline.result)  # 30
```

`run()` returns the pipeline, so these calls can also be chained:

```python
pipeline.run(10).wait()
```

The first step receives `10`; the next receives the first step's return value. `result` is the latest successful value, and it cannot be read while the pipeline is running. If `run()` is called without an initial value, the pipeline uses its `default`, which is `None` unless configured.

## Run synchronously

Call the pipeline object when the caller should wait for execution and receive the result directly:

```python
result = pipeline(10)
print(result)  # 30
```

This synchronous form reraises the most recent step exception, if one was recorded.

## Continue learning

- [Core concepts](core-concepts.md) explains step arguments, mutation, editing, and composition.
- [Async pipelines](async-pipelines.md) covers worker-thread execution, checkpoints, and errors.
- [Recipes](recipes.md) provides practical examples.
- The [API reference](../api/Pipeline.md) lists the public pipeline methods and properties.
