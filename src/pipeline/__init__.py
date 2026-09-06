"""A small functional pipeline toolkit for Python.

This package provides a simple asynchronous pipeline executor along with supporting functional utilities and container components.

The main components are:

```
	- :class:`Pipeline`: Execute callable steps sequentially in a worker thread with support for stopping, skipping, waiting, and rerunning execution.
	- :class:`Stack`: A simple LIFO container with optional maximum capacity, useful for storing pipeline results and errors.
	- :func:`compose`: Apply multiple callables sequentially to a value.
	- :func:`tap`: Apply a side effect to a deep copy of a value while returning the original value unchanged.
	- :decorator:`pipe`: Wrap a callable as a factory for creating :class:`step` objects with preconfigured arguments.
	- :class:`step`: Represent a callable with preconfigured arguments and provide convenient execution and composition operations.
```

Example:
	>>> from pipeline import Pipeline
	>>> pipeline = Pipeline([
			(lambda value: value + 1,),
			(lambda value: value * 2,),
		]
		... ], default=5
	)
	>>> pipeline.run().wait()
	>>> pipeline.results.get()
	12
"""
from .compose import compose
from .pipe import pipe, step
from .pipeline import Pipeline

__version__ = "0.2.2"
__author__ = "Hoàng Long"
__all__ = ["Pipeline", "**author**", "**version**", "compose", "pipe", "step"]