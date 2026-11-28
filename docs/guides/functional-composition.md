# Functional Composition & Steps

## Compose Callables

`compose()` creates a reusable callable that applies each function to the previous function's result:

```python
from pipeline import compose

normalize = compose([str.strip, str.casefold])
print(normalize("  Pipeline Toolkit  "))  # "pipeline toolkit"
```

Each function in `compose()` receives one argument. An empty composition returns its input unchanged.

## Chain Pipeline Steps

`chain()` executes callables and pipeline step tuples immediately, passing each result forward:

```python
from pipeline import chain

def add(value, amount):
    return value + amount

result = chain([(add, (5,)), lambda value: value * 2], default=10)
print(result)  # 30
```

Unlike `compose()`, a `chain()` step tuple can configure additional positional or keyword arguments. `flow()` is similar but yields each intermediate value:

```python
from pipeline import flow

values = list(flow([lambda value: value + 1, lambda value: value * 2], data=10))
print(values)  # [11, 22]
```

## Configure a Step

Use `pipe` to make a callable that creates configured `step` objects. A configured step can be used as a callable inside a one-item pipeline step tuple:

```python
from pipeline import Pipeline, pipe

@pipe
def add(value, amount):
    return value + amount

pipeline = Pipeline([(add(5),)])
pipeline.run(10).wait()
print(pipeline.result)  # 15
```

`step.export()` returns the equivalent pipeline step tuple. The [`step` API](../api/step.md) documents the other operations available on step objects.

## Forward the Value to an Argument

Use `forward()` when a pipeline value belongs in a callable argument other than the first positional parameter. Integer targets are one-based positions; string targets are keyword names.

```python
from pipeline import forward

def divide(numerator, denominator):
    return numerator / denominator

result = forward(2, divide, "denominator", 10)
print(result)  # 5.0
```

See the [`compose`](../api/compose.md), [`chain`](../api/chain.md), [`flow`](../api/flow.md), and [`forward`](../api/forward.md) API pages.
