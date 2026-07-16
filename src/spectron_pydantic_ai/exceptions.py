"""Exceptions raised by the Spectron integration for Pydantic AI."""

from __future__ import annotations


class SpectronError(Exception):
    """Base class for all errors raised by this package."""


class SpectronImportError(SpectronError, ImportError):
    """Raised when the Spectron Python client cannot be imported.

    The client ships in the base SurrealDB SDK (``surrealdb``, v3 alpha or
    newer) and may not be installed in your environment.
    """


__all__ = ["SpectronError", "SpectronImportError"]
