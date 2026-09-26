# Contributing

Thanks for helping improve `Pipeline-Toolkit`. Contributions of bug reports, feature ideas, documentation, and code are welcome.

## Report a bug or suggest an improvement

Open an issue in the [GitHub repository](https://github.com/Hoang-Long2012/pipeline-toolkit/issues).

For a bug, include a short reproduction, what you expected to happen, what happened instead, and your Python version.

## Set up the project

Install [uv](https://docs.astral.sh/uv/) and sync the development environment from the lockfile:

```bash
uv sync --locked --group dev
```

The repository uses Python 3.14 for development.

The package itself supports Python 3.8 and newer.

## Make and check a change

Keep changes focused. Add or update tests for changed behavior, and update user-facing documentation when the public API or its behavior changes.

Before opening a pull request, run:

```bash
uv run ruff check .
uv run pytest
```

If you change dependencies, regenerate `uv.lock` with `uv lock` and include the updated lockfile.

Do not edit the lockfile by hand.

## Open a pull request

Push your branch to your fork and open a pull request against `main`. In the pull request description, explain the problem and change, list the checks you ran, and link any related issue.