# Examples

Runnable examples for `spectron-pydantic-ai`.

## Prerequisites

Install the package with a Pydantic AI model provider and the Spectron client:

```bash
pip install "spectron-pydantic-ai" "pydantic-ai-slim[openai]" "surrealdb[spectron]"
```

Set the connection and model environment variables:

```bash
export SPECTRON_URL="https://your-spectron-instance"
export SPECTRON_NAMESPACE="your-namespace"
export SPECTRON_TOKEN="your-token"
export OPENAI_API_KEY="sk-..."
```

Spectron is in early preview. If the `surrealdb[spectron]` client is not yet
available in your environment, the examples that connect to a live service will
not run, but the package itself installs and its tests pass without it.

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
