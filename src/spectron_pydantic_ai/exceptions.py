"""Exceptions raised by the Spectron integration for Pydantic AI."""

from __future__ import annotations


class SpectronError(Exception):
    """Base class for all errors raised by this package."""


class SpectronImportError(SpectronError, ImportError):
    """Raised when the Spectron Python client cannot be imported.

    Spectron is in early preview. The client ships as an extra of the SurrealDB
    SDK and may not be installed or published yet in your environment.
    """


__all__ = ["SpectronError", "SpectronImportError"]
