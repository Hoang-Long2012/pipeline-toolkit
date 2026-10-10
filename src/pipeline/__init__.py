"""A small functional pipeline toolkit for Python.

This package provides a simple asynchronous pipeline executor along with supporting functional utilities and container components.

The main components are:

- [`Pipeline`](Pipeline.md): Execute callable steps sequentially in a worker thread with support for stopping, skipping, waiting, and rerunning execution.
- [`Checkpoint`](Checkpoint.md): Store values and provide a synchronization point for coordinating pipeline execution.
- [`Stack`](Stack.md): A simple LIFO container with optional maximum capacity, useful for storing pipeline results and errors.
- [`chain`](chain.md): Apply multiple callables sequentially, passing each result to the next callable.
- [`compose`](compose.md): Create a callable that applies multiple callables sequentially to a value.
- [`mut`](mut.md): Apply a function directly to an object for side effects and return the same object.
- [`tap`](tap.md): Apply a side effect to a deep copy of a value while returning the original value unchanged.
- [`pipe`](pipe.md): Wrap a callable as a factory for creating :class:`step` objects with preconfigured arguments.
- [`step`](step.md): Represent a callable with preconfigured arguments and provide convenient execution and composition operations.

Example:

```python
from pipeline import Pipeline

pipeline = Pipeline(
    [
        (lambda value: value + 1,),
        (lambda value: value * 2,),
    ],
    default=5
)

pipeline.run().wait().result  # 12
```
```"""
from .chain import chain as chain
from .checkpoint import Checkpoint as Checkpoint
from .compose import compose as compose
from .mut import mut as mut
from .pipe import pipe as pipe
from .pipe import step as step
from .pipeline import Pipeline as Pipeline
from .tap import tap as tap

__version__ = "0.5.5"
__author__ = "Hoàng Long"
__all__ = ["Checkpoint", "Pipeline", "__author__", "__version__", "chain", "compose", "mut", "pipe", "step", "tap"]
