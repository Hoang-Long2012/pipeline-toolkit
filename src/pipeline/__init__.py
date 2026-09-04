"""A small functional pipeline toolkit for Python.

This package provides a simple asynchronous pipeline executor along with supporting container and utility components.

The main components are:

	- :class:`Pipeline`: Execute callable steps sequentially in a worker thread.
	- :class:`Stack`: A simple LIFO container for storing values and errors.
	- :func:`tap`: Apply a side effect to a deep copy of a value while returning the original value unchanged.

Example:
	>>> from pipeline import Pipeline
	>>> pipeline = Pipeline(
	...     (lambda value: value + 1,),
	...     (lambda value: value * 2,),
	... )
	>>> pipeline.run(5).wait()
	>>> pipeline.results.get()
	12
"""
from .pipeline import Pipeline
__version__ = "0.1.0"
__author__ = "Hoàng Long"
__all__ = ["__version__", "__author__", "Pipeline"]