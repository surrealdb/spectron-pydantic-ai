# Examples

Runnable examples for `spectron-pydantic-ai`.

## Prerequisites

Install the package with a Pydantic AI model provider. The Spectron client is
bundled in `surrealdb` (v3 alpha or newer) and installs automatically:

```bash
pip install "spectron-pydantic-ai" "pydantic-ai-slim[openai]"
```

Set the connection and model environment variables:

```bash
export SPECTRON_CONTEXT="your-context"
export SPECTRON_ENDPOINT="https://your-spectron-instance"
export SPECTRON_API_KEY="your-api-key"
export OPENAI_API_KEY="sk-..."
```

Spectron is in early preview. Without access to a live Spectron instance, the
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
