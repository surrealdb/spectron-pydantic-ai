# Contributing

Thanks for your interest in improving `agent-memory-pydantic-ai`.

## Development setup

This project uses [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Checks

Run the same checks that CI runs before opening a pull request:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```

`ruff format .` applies formatting, and `ruff check --fix .` applies safe lint
fixes.

## Guidelines

- Keep the Agent Memory SDK import confined to `src/agent_memory_pydantic_ai/_adapter.py`.
  Everything else depends on the `AgentMemoryClient` protocol so it can be tested
  with a fake client.
- Add or update tests for any behaviour change. Tests must pass without a live
  Agent Memory service or a real model.
- Do not use em-dashes in code, comments, docstrings, or documentation.

## Pull requests

- Base your branch on `main`.
- Describe the change and the reasoning behind it.
- Update `CHANGELOG.md` under the `Unreleased` heading.
