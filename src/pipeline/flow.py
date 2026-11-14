"""Utility for executing callables sequentially and yielding intermediate results."""

def flow(steps, data=None):
	"""Execute callables sequentially, yielding each intermediate result.

	Each callable receives the result of the previous step as its single argument.
	The initial value ``data`` is passed to the first callable.

	Args:
		steps: An iterable of callables to apply sequentially.
		data: Initial value passed to the first callable.
			Defaults to ``None``.

	Yields:
		The intermediate result produced by each callable step.

	Raises:
		TypeError: If ``steps`` is not iterable, or any step is not callable.

	Example:
	```python
	def add_one(x):
	    return x + 1

	def multiply_two(x):
	    return x * 2

	list(flow([add_one, multiply_two], data=5))
	# [6, 12]
	```
	"""
	steps = tuple(steps)
	for step in steps:
		if not callable(step):
			step_name = getattr(step, "__name__", type(step).__name__)
			raise TypeError(f"{step_name} is not a callable.")
	for step in steps:
		data = step(data)
		yield data
