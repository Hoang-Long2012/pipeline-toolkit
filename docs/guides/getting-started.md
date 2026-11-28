# Getting Started

Install `pipeline-toolkit` with pip:

```bash
python -m pip install pipeline-toolkit
```

The package requires Python 3.8 or later and has no runtime dependencies.

## Create a Pipeline

Each pipeline step is a tuple containing a callable and optional arguments. The pipeline passes the current value as the callable's first argument and uses the returned value for the next step.

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

## Run and Read the Result

`run()` starts execution in a worker thread and returns the pipeline. Call `wait()` before reading `result`:

```python
pipeline.run(10).wait()
print(pipeline.result)  # 30
```

If `run()` is called without an initial value, it uses the pipeline's `default`, which is `None` unless configured. `result` is the initial value followed by the last successful step result, and it cannot be read while the pipeline is running.

Calling the pipeline object runs synchronously and returns the result:

```python
result = pipeline(10)
print(result)  # 30
```

With the default `stop_on_error=True`, this synchronous form reraises a step exception. If called with `stop_on_error=False`, it continues after caught step exceptions and returns the final result instead.

## Next Guides

- [Building and editing pipelines](building-and-editing-pipelines.md) covers step formats and mutable pipeline configuration.
- [Functional composition and steps](functional-composition.md) covers reusable functions and configured callables.
- [Side effects and state](side-effects-and-state.md) explains mutation, observation, and execution results.
- [Concurrency and coordination](concurrency-and-coordination.md) covers worker threads, groups, and checkpoints.
- [Error handling](error-handling.md) covers failures and continuation behavior.
- See the [API reference](../api/Pipeline.md) for all public pipeline methods and properties.
