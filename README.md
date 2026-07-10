# spectron-pydantic-ai

Spectron agent memory for [Pydantic AI](https://ai.pydantic.dev).

[Spectron](https://surrealdb.com/platform/spectron) is SurrealDB's memory and
knowledge layer for AI agents. This package connects it to Pydantic AI through
that framework's own extension points, so an agent can remember facts across
runs, recall them when they are relevant, and keep a durable record of its
conversations.

It gives you three surfaces, which you can use on their own or together:

- **Memory tools** (`SpectronToolset`): expose `recall`, `context`, `remember`,
  and more as tools the agent calls when it decides to.
- **Auto-recall** (`spectron_history_processor`): inject relevant memory before
  each model request, with no tool call required.
- **Persistence** (`store_run`, `store_messages`): write a run's messages back
  to Spectron so conversations survive across sessions.

## Status

Spectron is in early preview. The Python client ships as an extra of the
SurrealDB SDK (`pip install "surrealdb[spectron]"`). Until you have access to a
Spectron instance, you can still install this package, wire it into an agent,
and run the test suite: every Spectron call goes through a small client protocol
that is easy to fake.

## Install

```bash
pip install spectron-pydantic-ai
```

To run against a live Spectron instance and a model provider:

```bash
pip install "spectron-pydantic-ai" "pydantic-ai-slim[openai]" "surrealdb[spectron]"
```

## Quickstart

```python
import asyncio
from pydantic_ai import Agent
from spectron_pydantic_ai import SpectronMemory, SpectronToolset

async def main():
    memory = SpectronMemory.connect(
        url="https://your-spectron-instance",
        namespace="your-namespace",
        token="your-token",
        user_id="ada",
    )
    agent = Agent("openai:gpt-4o", toolsets=[SpectronToolset(memory)])
    result = await agent.run("Remember that I prefer window seats.")
    print(result.output)

asyncio.run(main())
```

## Auto-recall

Inject relevant memory before every run without giving the agent a tool. The
processor reads the latest user message, recalls related memories, and prepends
them as context.

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import ProcessHistory
from spectron_pydantic_ai import spectron_history_processor

processor = spectron_history_processor(memory)
agent = Agent("openai:gpt-4o", capabilities=[ProcessHistory(processor)])
```

Use `mode="context"` to load the current working set instead of searching by the
latest message.

> Note on versions: Pydantic AI registers history processors through the
> `capabilities` argument with `ProcessHistory`, as shown above. Older releases
> used a `history_processors=[...]` argument instead. The processor function
> returned by `spectron_history_processor` works with both; only the way you
> attach it to the agent differs. Check the version installed in your project.

## Persistence

Store a run's messages so the next session can recall them:

```python
from spectron_pydantic_ai import store_run

result = await agent.run("I am planning a trip to Tokyo.")
await store_run(memory, result)
```

## Scoping and multi-tenancy

`SpectronMemory` carries a scope (`user_id`, `session_id`, `agent_id`) that is
added to every operation. One connection can serve many users and sessions by
creating narrowed views:

```python
base = SpectronMemory(client)
alice = base.scoped(user_id="alice", session_id="s1")
bob = base.scoped(user_id="bob", session_id="s2")
```

## API

| Name | Purpose |
| --- | --- |
| `SpectronMemory` | Scoped wrapper over the Spectron client. `connect(...)`, `scoped(...)`, and the seven operations. |
| `SpectronToolset` | Pydantic AI toolset exposing memory operations as tools. |
| `spectron_history_processor` | Build a history processor for auto-recall. |
| `store_run`, `store_messages` | Persist messages back to Spectron. |
| `SpectronClient` | Protocol describing the client this package needs. |
| `SpectronError`, `SpectronImportError` | Exceptions raised by the package. |

The toolset exposes `recall`, `context`, and `remember` by default. Pass
`tools=ALL_TOOLS` (or a subset) to also expose `reflect` and `forget`:

```python
from spectron_pydantic_ai import ALL_TOOLS, SpectronToolset

toolset = SpectronToolset(memory, tools=ALL_TOOLS)
```

## Examples

See the [`examples`](examples) directory for runnable scripts covering the
toolset, auto-recall, and a persistent multi-turn chat.

## Development

This project uses [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```

## License

Apache License 2.0. See [LICENSE](LICENSE).
