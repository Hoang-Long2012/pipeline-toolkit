# Agent Instructions

## Project

`pipeline-toolkit` is a small, dependency-free Python library for building mutable, reusable, editable asynchronous pipelines.

Keep changes minimal, predictable, and focused on the requested task.

## Scope

- Read the relevant source code and tests before making changes.
- Modify only files directly required by the task.
- Do not refactor unrelated code.
- Do not clean up, modernize, or improve surrounding code unless explicitly requested.
- Do not modify documentation, configuration, workflows, or unrelated tests unless the task requires it.
- Do not change implementation code merely to make a test pass when the task is specifically about tests.
- Preserve existing public APIs and behavior unless the task explicitly requests a behavior change.

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
2. Run the smallest relevant test command.
3. Run additional checks only when they are necessary for the requested change.

Do not automatically:

- run the entire test suite when focused tests are sufficient;
- run unrelated commands;
- run formatters;
- rebuild documentation;
- build distributions;
- modify generated files;
- inspect or modify unrelated parts of the repository.

If an additional check would be useful but is not necessary, suggest it instead of running it automatically.

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
- Do not install packages globally.

## Task Completion

Before finishing:

- Verify that only the intended files changed.
- Review the final diff.
- Report what was changed.
- Report the verification command actually run and its result.
- If something was intentionally not run, do not pretend that it was verified.

When the requested task is complete, stop. Do not continue with unrelated improvements.
