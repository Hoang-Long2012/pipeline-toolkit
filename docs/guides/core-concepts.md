# Core concepts

## Pipelines and steps

A `Pipeline` stores steps in order. Each step is a tuple whose first item is a callable. The current value is passed as the callable's first positional argument, and the callable's return value becomes the next value.

For example, the second step below receives the result of `add`, not the original input:

```python
def add(value, amount):
    return value + amount

def multiply(value, factor):
    return value * factor

steps = [
    (add, (5,)),
    (multiply, (2,)),
]
```

## Callable arguments

Steps can store positional arguments, keyword arguments, or both:

```python
def format_price(value, currency="$", precision=2):
    return f"{currency}{value:.{precision}f}"

steps = [
    (format_price,),  # callable only
    (format_price, ("$",)),  # additional positional arguments
    (format_price, {"currency": "$", "precision": 0}),  # keyword arguments
    (format_price, ("$",), {"precision": 0}),  # both forms
]
```

In the final form, positional arguments must be a tuple and keyword arguments must be a mapping. The callable receives the pipeline value first, followed by those configured arguments.

The `pipe` decorator is an alternative way to create configured callable steps:

```python
from pipeline import Pipeline, pipe

@pipe
def add(value, amount):
    return value + amount

pipeline = Pipeline([(add(5),)])
```

## Mutation, reuse, and editing

Pipeline configuration is mutable. Add, insert, replace, or remove steps through methods such as `add`, `insert`, `remove`, and `clear`, or through item assignment. Pipeline item indexes are one-based:

```python
from pipeline import Pipeline, pipe

@pipe
def add(value, amount):
    return value + amount

pipeline = Pipeline([(add(1),)])
pipeline.add((add(3),))
pipeline[1] = (add(10),)
```

`steps` returns a deep copy of the configured steps; editing that copy does not edit the pipeline. A run uses the configured step sequence captured when `run()` starts, so edits made afterward do not change that execution. The pipeline can be run again with a new initial value.

## Composition

Use `compose` to create a reusable callable that applies single-argument functions in order:

```python
from pipeline import compose

normalize = compose([str.strip, str.casefold])

print(normalize("  Pipeline Toolkit  "))  # "pipeline toolkit"
```

`compose` returns the input unchanged when given no callables. To combine configured pipeline steps, `pipeline + steps` returns a new pipeline with the steps appended; it leaves the original pipeline unchanged.

See the [Pipeline API](../api/Pipeline.md), [`step` API](../api/step.md), and [`compose` API](../api/compose.md) for details.
