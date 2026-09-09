"""Exceptions raised by the Agent Memory integration for Pydantic AI."""

from __future__ import annotations


class AgentMemoryError(Exception):
    """Base class for all errors raised by this package."""


class AgentMemoryImportError(AgentMemoryError, ImportError):
    """Raised when the Agent Memory Python client cannot be imported.

    The client ships in the base SurrealDB SDK (``surrealdb``, v3 alpha or
    newer) and may not be installed in your environment.
    """


__all__ = ["AgentMemoryError", "AgentMemoryImportError"]
