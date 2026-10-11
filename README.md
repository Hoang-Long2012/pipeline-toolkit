# Pipeline Toolkit

A small functional pipeline toolkit for Python.

`pipeline-toolkit` provides a simple way to build sequential pipelines from ordinary Python callables.

It also provides small utilities for composing functions, configuring callable steps, applying side effects, and managing pipeline state.

## Features

- Zero dependencies.
- Sequential functional pipeline execution.
- Asynchronous execution using a worker thread.
- Configurable pipeline steps and default values.
- Positional and keyword arguments for pipeline steps.
- Optional automatic execution during initialization.
- Stop, skip, wait, and rerun execution.
- Context manager support for pipeline execution and cleanup.
- Synchronous execution of individual pipeline steps.
- Optional execution delays and configurable daemon worker threads.
- Optional stop-on-error behavior.
- Result and error history using a LIFO stack.
- Convenient access to the most recent result or error.
- Pipeline modification and standard sequence-style operations.
- Shallow and deep pipeline copying.
- Pipeline composition, repetition, comparison, and in-place modification with standard operators.
- Sequential callable composition with `compose()` and `chain()`.
- Configurable callable steps with `pipe` and `step`.
- Side-effect operations with `tap()` and `mut()`.
- LIFO `Stack` container with optional maximum capacity.

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

A pipeline is created from an iterable of steps. Each step is a tuple containing a callable and optional arguments.

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

print(pipeline.result)  # 30
```

The value flows through each step sequentially:

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

## Documentation

See the [documentation](https://Hoang-Long2012.github.io/pipeline-toolkit) for the complete guide and API reference.

## Requirements

- Python 3.8 or newer

## Changelog

See the [changelog](https://github.com/Hoang-Long2012/pipeline-toolkit/blob/main/CHANGELOG.md).

## Contributing

Contributions are welcome.

- Submit a pull request for improvements or fixes.
- Open an issue to report a bug or request a feature.

See the [contributing guide](https://github.com/Hoang-Long2012/pipeline-toolkit/blob/main/CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License.

See the [license](https://github.com/Hoang-Long2012/pipeline-toolkit/blob/main/LICENSE) for details.

Copyright (C) 2026 Hoàng Long
