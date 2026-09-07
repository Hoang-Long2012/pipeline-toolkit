# Pipeline Toolkit

A small functional pipeline toolkit for Python.

`pipeline-toolkit` provides a simple way to build sequential pipelines from ordinary Python callables.

It also provides small utilities for composing functions, configuring callable steps, applying side effects, and managing pipeline state.

## Features

- Sequential functional pipeline execution.
- Asynchronous execution using a worker thread.
- Positional and keyword arguments for pipeline steps.
- Configurable pipeline defaults.
- Stop, skip, wait, and rerun execution.
- Context manager support for automatic pipeline execution and cleanup.
- Manual synchronous step execution.
- Optional execution delays.
- Initial cancellation window before the first step when a delay is enabled.
- Configurable daemon worker threads.
- Optional stop-on-error behavior.
- Optional exception re-raising from worker threads.
- Result and error history using a stack.
- Pipeline modification with `add()`, `insert()`, `pop()`, and `clear()`.
- Sequential callable composition with `compose()`.
- Configurable callable steps with `pipe` and `step`.
- Step export and unpacking support.
- Side-effect operations with `tap()`.

## Installation

Install from PyPI:

```bash
pip install pipeline-toolkit
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/Hoang-Long2012/pipeline-toolkit.git
```

## Quick Start

A pipeline is created from an iterable of steps.

Each step is a tuple whose first item is a callable.

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

pipeline.run(10).wait()

print(pipeline.results.get())
```

The execution flow is:

```text
10
 ↓
add(10, 5)
 ↓
15
 ↓
multiply(15, 2)
 ↓
30
```

The final result is `30`.

## Pipeline Steps

Each step can use one of four supported forms.

### Callable only

```python
(function,)
```

The callable receives the previous result:

```python
pipeline = Pipeline([
	(str.upper,),
])

pipeline.run("hello").wait()
```

The step is executed as:

```python
str.upper(previous_result)
```

### Positional arguments

```python
(function, args)
```

where `args` is a tuple:

```python
pipeline = Pipeline([
	(add, (5,)),
	(multiply, (2,)),
])
```

A step such as:

```python
(add, (5,))
```

is executed as:

```python
add(previous_result, 5)
```

### Keyword arguments

```python
(function, kwargs)
```

where `kwargs` is a mapping:

```python
pipeline = Pipeline([
	(pow, {"exp": 2}),
])
```

The step is executed as:

```python
pow(previous_result, exp=2)
```

### Positional and keyword arguments

```python
(function, args, kwargs)
```

For example:

```python
pipeline = Pipeline([
	(my_function, (1, 2), {"option": True}),
])
```

The callable receives the previous result followed by the supplied positional and keyword arguments.

## Execution

### `run()`

Start the pipeline asynchronously.

```python
pipeline.run(default, delay=0, daemon=False, stop_on_error=True)
```

The initial result is determined by the supplied `default` value.

If `default` is omitted, the value configured when creating the pipeline is used.

`None` can be passed explicitly as the initial value:

```python
pipeline = Pipeline([
	(add, (5,)),
], default=10)

pipeline.run(None).wait()
```

In this example, the first step receives `None`, not `10`.

`delay` specifies the delay in seconds before the first step and between subsequent steps.

When `delay` is enabled, the initial delay provides an opportunity to cancel the pipeline before the first step begins.

```python
pipeline.run(10, delay=1)

pipeline.stop()
```

`daemon` controls whether the worker thread is a daemon thread.

`stop_on_error` controls whether execution stops after the first exception.

When disabled, exceptions are stored in `errors` and execution continues with the previous result.

`run()` returns the pipeline instance, allowing calls such as:

```python
pipeline.run(10).wait()
```

The pipeline is snapshotted when execution starts. Changes made to `pipeline.pipeline` after `run()` begins do not affect the current execution.

### `wait()`

Wait for the current execution to finish.

```python
pipeline.wait()
```

It returns the pipeline instance.

By default, exceptions raised by pipeline steps are stored in `errors` and are not raised by `wait()`.

To re-raise the most recent worker exception in the calling thread, use `reraise_exception=True`:

```python
try:
	pipeline.wait(reraise_exception=True)
except Exception as error:
	print(error)
```

This allows an exception raised by a worker step to be re-raised in the thread waiting for the pipeline.

### `stop()`

Request the running pipeline to stop and wait for its worker thread to terminate.

```python
step = pipeline.stop()
```

The return value is the current one-based step index when execution is stopped, or `0` if the pipeline was not running.

If the pipeline is stopped before the first step begins, the return value is `0`.

### `skip()`

Request the worker to skip the next step that reaches its skip check.

```python
pipeline.skip()
```

The method returns the pipeline instance.

### `rerun()`

Stop the current execution and start the pipeline again.

```python
pipeline.rerun(10)
```

Arguments are passed directly to `run()`.

### Context Manager

`Pipeline` can be used as a context manager.

Entering the context automatically starts the pipeline if it is not already running. Exiting the context requests the pipeline to stop and waits for the worker thread to terminate.

```python
with Pipeline([
	(add, (5,)),
	(multiply, (2,)),
]) as pipeline:
	print("Pipeline started")

pipeline.results.get()
```

This is useful when the lifetime of the pipeline should be tied to a `with` block.

The context manager does not start the pipeline again if it is already running:

```python
pipeline.run(10)

with pipeline:
	# The existing execution continues.
	pass
```

When leaving the context, `stop()` is called regardless of whether the block exits normally or because of an exception.

## Manual Step Execution

`run_step()` executes one configured step synchronously.

```python
result = pipeline.run_step(2, 10)
```

Unlike `run()`, this method:

- Does not create a worker thread.
- Does not modify the pipeline's worker-thread state.
- Does not store the result in `results`.
- Does not store exceptions in `errors`.
- Allows exceptions to propagate to the caller.

This makes it useful when a single pipeline step needs to be executed manually.

## Results and Errors

The pipeline provides two `Stack` instances:

```python
pipeline.results
pipeline.errors
```

`results` contains the initial value and the results produced by successfully executed steps.

For example:

```python
pipeline.run(10).wait()

print(pipeline.results.get())
```

`errors` contains exceptions raised by pipeline steps.

When `stop_on_error=True`, execution stops after the first exception.

When `stop_on_error=False`, the exception is stored in `errors` and execution continues with the previous result.

If multiple exceptions occur, they are stored in `errors` in execution order, with the most recent exception at the top of the stack.

## Managing Pipeline Steps

Pipeline steps can be modified before or between executions.

### `add()`

Append a step:

```python
pipeline.add((str.upper,))
```

### `insert()`

Insert a step at a one-based position:

```python
pipeline.insert(2, (str.strip,))
```

Positions range from `1` to `len(pipeline) + 1`.

### `pop()`

Remove and return a step:

```python
step = pipeline.pop(1)
```

Pipeline indexes are one-based.

### `clear()`

Remove all configured steps:

```python
pipeline.clear()
```

## Pipeline State

The `running` property indicates whether the worker thread is currently running:

```python
if pipeline.running:
	print("Pipeline is running")
```

The `step` attribute contains the one-based index of the currently executing step. It is `0` when the pipeline is not running.

A `Pipeline` instance can also be used as a boolean:

```python
if pipeline:
	print("Pipeline is running")
```

Calling a pipeline instance is equivalent to calling `run()`:

```python
pipeline(10)
```

is equivalent to:

```python
pipeline.run(10)
```

The length of a pipeline is the number of configured steps:

```python
len(pipeline)
```

A callable can be checked with the `in` operator:

```python
if add in pipeline:
	print("add is part of the pipeline")
```

Callable membership uses identity comparison.

## Functional Utilities

### `compose()`

`compose()` applies callables sequentially to a value.

The result of each callable is passed as the first argument to the next callable.

```python
from pipeline import compose

def add(value, amount):
	return value + amount

def multiply(value, factor):
	return value * factor

result = compose(
	lambda value: add(value, 5),
	lambda value: multiply(value, 2),
	default=10,
)

print(result)
```

The execution flow is:

```text
10
 ↓
add(10, 5)
 ↓
15
 ↓
multiply(15, 2)
 ↓
30
```

`compose()` executes the callables immediately and returns the final result.

An empty composition returns the supplied `default` value.

### `pipe`

`pipe` wraps a callable as a step factory.

It is useful when the same callable needs to be configured with different arguments.

```python
from pipeline import pipe

@pipe
def add(value, amount):
	return value + amount

add_five = add(5)

print(add_five(10))
```

The `pipe` object itself is called to create a `step`.

```python
add(5)
```

returns a `step` containing `add` and the argument `5`.

A `step` can be used directly as a callable:

```python
result = add_five(10)
```

It can also be placed inside a pipeline step tuple:

```python
pipeline = Pipeline([
	(add_five,),
])
```

Because `step` objects are callable, they are compatible with the standard pipeline step format without requiring special handling by `Pipeline`.

### `step`

`step` represents a callable with preconfigured arguments.

```python
from pipeline import step

add_five = step(add, 5)

print(add_five(10))
```

A `step` passes its supplied value as the first argument to the wrapped callable, followed by its configured positional and keyword arguments.

It can also be used with the pipe operator:

```python
result = 10 | add_five
```

This is equivalent to:

```python
result = add_five(10)
```

A step can be repeated with the multiplication operator:

```python
def add(value, amount):
	return (value or 0) + amount

result = step(add, 5) * 3

print(result)  # 15
```

The wrapped callable is executed once for each repetition, with each result passed to the next execution.

Repeated execution starts with `None`; each result is passed to the next execution.

#### Exporting a step

A `step` can be converted into the standard pipeline step format with `export()`:

```python
add_five = step(add, 5)

pipeline_step = add_five.export()

print(pipeline_step)
```

The exported value is one of the standard pipeline step forms:

```python
(function,)
(function, args)
(function, kwargs)
(function, args, kwargs)
```

For example:

```python
step(add, 5, amount=10).export()
```

produces:

```python
(add, (5,), {"amount": 10})
```

Empty positional or keyword arguments are omitted from the exported tuple.

#### Unpacking a step

A `step` can also be unpacked directly with the `*` operator:

```python
add_five = step(add, 5)

pipeline = Pipeline([
	(*add_five,),
])
```

This is equivalent to:

```python
pipeline = Pipeline([
	add_five.export(),
])
```

Unpacking is therefore a convenient shorthand when constructing pipeline step tuples.

`step` itself remains a general callable object and is not a special pipeline step type. `Pipeline` continues to use its standard `(function, args, kwargs)` step format.

`step` also provides convenience support for file-like objects through `<` and `>`:

```python
process_step = step(process)

result = process_step < file
process_step > file
```

These operations use the file-like object's `read()` and `write()` methods respectively.

### `tap`

`tap()` applies a side effect to a deep copy of a value and returns the original value unchanged.

This makes it useful for logging, inspection, debugging, or other side effects that should not interrupt a functional chain.

```python
from pipeline.tap import tap

value = {"count": 10}

def show(data):
	print(data)

result = tap(value, show)

print(result is value)  # True
```

The function receives a deep copy, so mutations made by the side-effect function do not modify the original value.

`tap()` can also be used as a pipeline step:

```python
from pipeline import Pipeline
from pipeline.tap import tap

def add(value, amount):
	return value + amount

pipeline = Pipeline([
	(add, (5,)),
	(tap, (print,)),
	(add, (10,)),
])

pipeline.run(10).wait()
```

The value printed by `tap()` is still passed unchanged to the next step.

### `Stack`

`Stack` is a simple LIFO stack container with optional capacity limits.

It supports common stack operations such as pushing, retrieving and removing items, with dedicated exceptions for overflow and underflow conditions.

Import it directly from its submodule:

```python
from pipeline.stack import Stack

stack = Stack()

stack.push("first")
stack.push("second")

print(stack.get())
```

`Stack` is also used internally by `Pipeline` for storing results and errors.

`Stack` raises `StackOverflowError` when pushing to a full stack and `StackUnderflowError` when accessing or removing an item from an empty stack.

For detailed stack operations and behavior, see the `pipeline.stack` module.

## API Overview

### `Pipeline`

| Member        | Description                                   |
| ------------- | --------------------------------------------- |
| `run()`       | Start asynchronous pipeline execution         |
| `run_step()`  | Execute one step synchronously                |
| `stop()`      | Stop the current execution                    |
| `skip()`      | Request the next step to be skipped           |
| `wait()`      | Wait for the current execution                |
| `rerun()`     | Restart the pipeline                          |
| `add()`       | Append a step                                 |
| `insert()`    | Insert a step                                 |
| `pop()`       | Remove and return a step                      |
| `clear()`     | Remove all steps                              |
| `running`     | Whether the worker is running                 |
| `step`        | Current one-based step index                  |
| `results`     | Stack of initial value and successful results |
| `errors`      | Stack of raised exceptions                    |

### Functional Utilities

| Member    | Description                                    |
| --------- | ---------------------------------------------- |
| `compose` | Apply callables sequentially to a value        |
| `pipe`    | Wrap a callable as a step factory              |
| `tap`     | Apply a side effect to a deep copy of a value  |

### `step`

| Member       | Description                                        |
| ------------ | -------------------------------------------------- |
| `export()`   | Convert the step to standard pipeline step format  |

### `Stack`

| Member | Description |
|---|---|
| `Stack(maxsize=0)` | Create an empty LIFO stack with optional maximum capacity. |
| `push(value)` | Push a value onto the top of the stack. |
| `get()` | Return the top value without removing it. |
| `pop()` | Remove and return the top value. |
| `clear()` | Remove all values from the stack. |
| `empty()` | Return whether the stack is empty. |
| `full()` | Return whether the stack has reached its maximum capacity. |
| `len(stack)` | Return the number of values currently in the stack. |
| `bool(stack)` | Return whether the stack contains at least one value. |
| `value in stack` | Check whether a value exists in the stack. |
| `iter(stack)` | Iterate over values from bottom to top. |
| `repr(stack)` | Return a developer-oriented representation of the stack. |

## Requirements

- Python 3.8 or newer

## Changelog

See [CHANGELOG.md](https://github.com/Hoang-Long2012/pipeline-toolkit/blob/main/CHANGELOG.md).

## License

This project is licensed under the MIT License. See [LICENSE](https://github.com/Hoang-Long2012/pipeline-toolkit/blob/main/LICENSE) for details.

## Contribution

If you'd like to contribute, feel free to submit a pull request.

If you'd like to report a bug or request a feature, please open an issue.

Copyright (C) 2026 Hoàng Long
