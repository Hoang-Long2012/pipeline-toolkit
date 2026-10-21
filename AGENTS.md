# Agent Instructions

## Project

`pipeline-toolkit` is a small, dependency-free Python library for building mutable, reusable, editable asynchronous pipelines.

It also provides small utilities for composing functions, configuring callable steps, applying side effects, and managing pipeline state.

Keep changes minimal, predictable, and focused on the requested task.

## Philosophy

`pipeline-toolkit` intentionally favors simplicity, mutability, reusability, and editability over abstraction, immutability, and feature breadth.

The project is a small library, not a framework. Its purpose is to provide simple building blocks that remain understandable, composable, and directly controllable by the caller.

### Core Principles

- **Mutable by design.** Pipeline state and configuration are allowed to change over its lifetime. Do not introduce immutability merely because it appears safer or more modern.
- **Reusable by design.** A pipeline is not necessarily a one-shot execution object. Its steps and configuration may be reused across executions.
- **Editable by design.** Pipelines are intended to be inspected and modified after creation. Do not replace this model with frozen or builder-only abstractions unless explicitly requested.
- **Simple over clever.** Prefer direct, explicit implementations over abstractions that exist primarily to make the code look more elegant.
- **Library over framework.** The library should provide mechanisms without imposing an application architecture or lifecycle on its users.
- **Behavior over ceremony.** Public behavior and a small, predictable API matter more than architectural purity.
- **Minimalism is intentional.** A missing feature is not necessarily an oversight. Do not add functionality merely because similar libraries provide it.
- **Backward compatibility matters.** Existing behavior and API design are part of the project's identity. A redesign should require an explicit request, not an inferred improvement.
- **Different is not automatically wrong.** When the project intentionally behaves differently from common patterns, preserve that behavior unless the task explicitly asks to change it.

### Design Boundary

When considering a change, ask:

1. Does it solve the requested problem?
2. Does it preserve the project's mutable, reusable, and editable model?
3. Does it make the library simpler for users, rather than merely more sophisticated internally?
4. Does it introduce a new abstraction or convention that the project does not otherwise need?

If the answer to the last question is yes, prefer the existing design unless the task explicitly requires otherwise.

Do not reinterpret the project's design goals as problems to be fixed.

## Scope

- Read the relevant source code and tests before making changes.
- Modify only files directly required by the task.
- Do not refactor unrelated code.
- Do not clean up, modernize, or improve surrounding code unless explicitly requested.
- Do not modify documentation, configuration, workflows, or unrelated tests unless the task requires it.
- Do not change implementation code merely to make a test pass when the task is specifically about tests.
- Preserve existing public APIs and behavior unless the task explicitly requests a behavior change.
- Treat the requested task as an exhaustive scope, not as a starting point for broader improvements.

## Implementation Guidelines

- Preserve the existing public model before introducing new abstractions or redesigning existing ones.
- Prefer extending the existing implementation over replacing it with a new architecture.
- Keep state ownership explicit. Do not move state between objects merely to make the implementation appear cleaner.
- Keep control flow explicit and predictable. Avoid hidden behavior, implicit lifecycle management, or unnecessary indirection.
- Prefer composition of small existing utilities over introducing parallel implementations of the same concept.
- Reuse existing internal helpers and conventions when they already express the required behavior.
- Keep public APIs small. Do not expose internal mechanisms unless they provide a clear and intentional user-facing capability.
- Do not add configuration options, extension points, hooks, callbacks, or abstractions speculatively.
- Preserve meaningful distinctions between related concepts. Do not merge APIs or states merely because they appear similar internally.
- Preserve established semantics for return values, exceptions, state transitions, and object lifecycle.
- When behavior changes, update the implementation only as far as necessary to establish the requested semantics.
- Prefer explicit exceptions for invalid operations or impossible states over silent fallbacks that hide errors.
- Do not add defensive behavior that changes established semantics unless the requested task requires it.
- Avoid premature optimization. Optimize only when there is a demonstrated problem or an explicit performance requirement.
- Avoid compatibility layers for hypothetical future versions or use cases.
- Do not introduce patterns solely because they are common in other libraries or considered best practice elsewhere.
- When multiple implementations satisfy the requirement, prefer the smallest implementation that fits the existing architecture and project philosophy.
- Treat internal simplicity as a feature. A slightly repetitive implementation may be preferable to a generalized abstraction if the abstraction adds more complexity than value.

## Code Style

- Preserve the existing formatting and coding style.
- Use tabs for Python indentation.
- Prefer straightforward, readable Python over unnecessary abstractions.
- Do not introduce unnecessary dependencies.
- Follow the existing project architecture instead of introducing new patterns without a clear need.
- Do not rewrite working code simply because another implementation looks cleaner.

## Formatting

- **Never run `ruff format`.**
- Never automatically format or reformat the repository.
- Do not change formatting of existing code unless formatting is explicitly part of the task.
- `ruff check` is a lint check, not a formatting command. Do not use it as a reason to reformat files.
- If formatting appears inconsistent but is unrelated to the task, leave it unchanged.

## Tests

- Prefer focused tests for the behavior being changed.
- Keep tests independent and deterministic.
- Prefer one clear behavior or failure case per test.
- Do not add tests for behavior that the implementation does not claim to provide.
- Do not over-specify implementation details when public behavior is sufficient.
- Avoid unnecessary mocks, timing assumptions, or external dependencies.
- When modifying tests, inspect the current implementation first and test its intended existing behavior.

## Verification

After making changes:

1. Inspect the diff.
2. Run linter on areas that have changed.
3. Run type-checker on areas that have changed.
4. Run the smallest relevant test command.
5. Run additional checks only when they are necessary for the requested change.

Do not automatically:

- run the entire test suite when focused tests are sufficient;
- run unrelated commands;
- run formatters;
- rebuild documentation;
- build distributions;
- modify generated files;
- inspect or modify unrelated parts of the repository.

If an additional check would be useful but is not necessary, suggest it instead of running it automatically.

If the changes involve `pyproject.toml`, run validate-pyproject and report the results output.

## Git

Do not perform Git operations that modify repository history or the remote unless explicitly requested.

In particular, do not automatically:

- commit;
- amend;
- reset;
- restore unrelated changes;
- rebase;
- merge;
- create or delete branches;
- create tags;
- push;
- force-push.

Read-only commands such as `git status`, `git diff`, and `git log` are allowed when relevant to the task.

Never discard or overwrite the user's existing uncommitted work.

## Dependency Management

- Do not add, remove, or upgrade dependencies unless explicitly requested.
- Prefer the project's existing `uv` workflow.
- Do not modify lock files merely as a side effect of an unrelated task.
- If the requested change explicitly requires modifying lock files, update them and clearly indicate that.
- Do not install packages globally.

## Task Completion

Before finishing:

- Verify that only the intended files changed.
- Review the final diff.
- Report what was changed.
- Report the verification command actually run and its result.
- If something was intentionally not run, do not pretend that it was verified.

When the requested task is complete, stop. Do not continue with unrelated improvements.
