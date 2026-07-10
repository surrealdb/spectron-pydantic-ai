"""Spectron agent memory for Pydantic AI.

This package connects SurrealDB's Spectron memory layer to Pydantic AI through
three surfaces:

- :class:`SpectronToolset`: memory operations the agent can call as tools.
- :func:`spectron_history_processor`: auto-recall of relevant memory before each
  model request.
- :func:`store_run` and :func:`store_messages`: persistence of a run's messages
  back to Spectron.

All of these operate on a :class:`SpectronMemory`, a scoped wrapper around the
Spectron client.
"""

from __future__ import annotations

from ._adapter import SpectronClient
from .exceptions import SpectronError, SpectronImportError
from .history import (
    HistoryProcessor,
    spectron_history_processor,
    store_messages,
    store_run,
)
from .memory import SpectronMemory
from .toolset import ALL_TOOLS, DEFAULT_TOOLS, SpectronToolset

__version__ = "0.1.0"

__all__ = [
    "ALL_TOOLS",
    "DEFAULT_TOOLS",
    "HistoryProcessor",
    "SpectronClient",
    "SpectronError",
    "SpectronImportError",
    "SpectronMemory",
    "SpectronToolset",
    "__version__",
    "spectron_history_processor",
    "store_messages",
    "store_run",
]
