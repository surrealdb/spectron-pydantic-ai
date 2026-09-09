# Examples

Runnable examples for `agent-memory-pydantic-ai`.

## Prerequisites

Install the package with a Pydantic AI model provider. The Agent Memory client is
bundled in `surrealdb` (v3 alpha or newer) and installs automatically:

```bash
pip install "agent-memory-pydantic-ai" "pydantic-ai-slim[openai]"
```

Set the connection and model environment variables:

```bash
export AGENT_MEMORY_CONTEXT="your-context"
export AGENT_MEMORY_ENDPOINT="https://your-agent_memory-instance"
export AGENT_MEMORY_API_KEY="your-api-key"
export OPENAI_API_KEY="sk-..."
```

Agent Memory is in early preview. Without access to a live Agent Memory instance, the
examples that connect to a service will not run, but the package itself installs
and its tests pass without one.

## Files

| File | What it shows |
| --- | --- |
| `01_toolset_quickstart.py` | Give an agent memory tools it can call on its own. |
| `02_auto_recall.py` | Inject relevant memory before each run with a history processor. |
| `03_persistent_chat.py` | Per-user and per-session scope, auto-recall, and persistence combined. |

## Running

```bash
python examples/01_toolset_quickstart.py
python examples/02_auto_recall.py
python examples/03_persistent_chat.py
```
