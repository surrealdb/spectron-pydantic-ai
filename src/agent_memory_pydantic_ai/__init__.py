"""AgentMemory agent memory for Pydantic AI.

This package connects SurrealDB's AgentMemory memory layer to Pydantic AI through
three surfaces:

- :class:`AgentMemoryToolset`: memory operations the agent can call as tools.
- :func:`agent_memory_history_processor`: auto-recall of relevant memory before each
  model request.
- :func:`store_run` and :func:`store_messages`: persistence of a run's messages
  back to AgentMemory.

All of these operate on a :class:`AgentMemoryMemory`, a scoped wrapper around the
AgentMemory client.
"""

from __future__ import annotations

from ._adapter import AgentMemoryClient
from .exceptions import AgentMemoryError, AgentMemoryImportError
from .history import (
    HistoryProcessor,
    agent_memory_history_processor,
    store_messages,
    store_run,
)
from .memory import AgentMemoryMemory
from .toolset import ALL_TOOLS, DEFAULT_TOOLS, AgentMemoryToolset

__version__ = "0.1.0"

__all__ = [
    "ALL_TOOLS",
    "DEFAULT_TOOLS",
    "AgentMemoryClient",
    "AgentMemoryError",
    "AgentMemoryImportError",
    "AgentMemoryMemory",
    "AgentMemoryToolset",
    "HistoryProcessor",
    "__version__",
    "agent_memory_history_processor",
    "store_messages",
    "store_run",
]
