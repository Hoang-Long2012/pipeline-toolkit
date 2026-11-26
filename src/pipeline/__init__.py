"""A small functional pipeline toolkit for Python.

Build reusable, editable pipelines that execute ordinary Python callables asynchronously in worker threads.

The main components are:

## Core components:
- [`Pipeline`](api/Pipeline.md): Execute callable steps sequentially in a worker thread with support for stopping, skipping, waiting, and rerunning pipelines.
- [`Group`](api/Group.md): Manage a collection of pipelines or sub-groups with support for collective execution, control, and container operations.
- [`Checkpoint`](api/Checkpoint.md): Store values and provide a synchronization point for coordinating pipeline execution.
- [`Stack`](api/Stack.md): A simple LIFO container with optional maximum capacity, useful for storing pipeline results and errors.

## Functional utilities:
- [`chain`](api/chain.md): Apply multiple callables or pipeline step tuples sequentially, passing each result to the next step and returning the final result.
- [`compose`](api/compose.md): Create a callable that applies multiple callables sequentially to a value.
- [`context_executor`](api/context_executor.md): Execute a context manager with a value and return its result.
- [`flow`](api/flow.md): Execute callables sequentially, yielding each intermediate result.
- [`mut`](api/mut.md): Apply a function directly to an object for side effects and return the same object.
- [`tap`](api/tap.md): Apply a side effect to a deep copy of a value while returning the original value unchanged.
- [`pipe`](api/pipe.md): Wrap a callable as a factory for creating [`step`](api/step.md) objects with preconfigured arguments.
- [`repeat`](api/repeat.md): Yield a callable step repeated a specified number of times.
- [`step`](api/step.md): Represent a callable with preconfigured arguments and provide convenient execution and composition operations.

## Example:

```python
from pipeline import Pipeline

def add(x, y):
    return x + y

def multiply(x, y):
    return x * y

pipeline = Pipeline(
    [
        (add, (1,)),
        (multiply, (2,)),
    ]
)

pipeline.run(5)

# Do something

pipeline.wait()

print(pipeline.result)  # 12
```

The value flows through each step sequentially:

```text
5
 ↓
add(5, 1)
 ↓
6
 ↓
multiply(6, 2)
 ↓
12
```
"""
from importlib.metadata import PackageNotFoundError, version

from .chain import chain as chain
from .checkpoint import Checkpoint as Checkpoint
from .compose import compose as compose
from .context_executor import context_executor as context_executor
from .flow import flow as flow
from .group import Group as Group
from .mut import mut as mut
from .pipe import pipe as pipe
from .pipe import step as step
from .pipeline import Pipeline as Pipeline
from .repeat import repeat as repeat
from .tap import tap as tap

try:
	__version__ = version("pipeline-toolkit")
except PackageNotFoundError:
	__version__ = "0.0.0-dev0"

__author__ = "Hoàng Long"
__all__ = ["Checkpoint", "Group", "Pipeline", "__author__", "__version__", "chain", "compose", "context_executor", "flow", "mut", "pipe", "repeat", "step", "tap"]
