# Group Documentation

This document provides an overview of **grouping** capabilities in the `pipeline-toolkit`.

## What is a Group?

A *group* is a logical collection of pipeline steps that can be managed as a single unit.  Groups are useful when you want to:
- Apply the same configuration (e.g., error handling, retries) to multiple steps.
- Enable/disable a subset of the pipeline dynamically.
- Re‑use a set of steps across different pipelines.

## Defining a Group

A group is defined by wrapping a list of steps with the `Group` helper provided by the library:

```python
from pipeline import Pipeline, Group

def step_a(x):
    return x + 1

def step_b(x):
    return x * 2

# Create a group containing two steps
my_group = Group([
    (step_a, ()),
    (step_b, ()),
])

# Use the group as a single step in a pipeline
pipeline = Pipeline([
    my_group,
    (lambda y: y - 3, ()),
])

pipeline.run(5).wait()
print(pipeline.result)  # (5 + 1) * 2 - 3 = 9
```

## Group Options

When creating a `Group`, you can pass optional keyword arguments that affect all contained steps:
- `error_handler`: A callable that will be invoked if any step in the group raises an exception.
- `retry`: An integer specifying how many times to retry a failing step.
- `on_start` / `on_finish`: Callables executed before the first step and after the last step, respectively.

```python
my_group = Group([
    (step_a, ()),
    (step_b, ()),
], error_handler=log_error, retry=2)
```

## Enabling / Disabling a Group

A group can be toggled on or off at runtime using the `enabled` attribute:

```python
my_group.enabled = False  # Skips all steps inside the group
```

When disabled, the group simply passes the input value through unchanged.

## Nesting Groups

Groups can be nested inside other groups, allowing you to build a hierarchy of logical sections.

```python
inner = Group([(step_a, ()), (step_b, ())])
outer = Group([inner, (step_c, ())])
```

## When to Use Groups

- **Modular pipelines**: Break a large pipeline into reusable sub‑pipelines.
- **Conditional execution**: Enable or disable a block of steps based on configuration.
- **Shared configuration**: Apply the same error handling or retry policy to many steps without repeating code.

For more details, see the [API Reference](https://Hoang-Long2012.github.io/pipeline-toolkit) under the *Group* section.
