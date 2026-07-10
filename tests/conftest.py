"""Shared test fixtures.

``FakeSpectron`` implements the Spectron client protocol in memory so the whole
package can be tested without a live Spectron service or a real model.
"""

from __future__ import annotations

from typing import Any

import pytest

from spectron_pydantic_ai import SpectronMemory


class FakeSpectron:
    """An in-memory stand-in for the Spectron async client.

    Every call is recorded in ``calls`` as a ``(name, kwargs)`` tuple. Return
    values are canned so assertions can check formatting and dispatch.
    """

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def _record(self, name: str, kwargs: dict[str, Any]) -> None:
        self.calls.append((name, kwargs))

    def names(self) -> list[str]:
        return [name for name, _ in self.calls]

    def last(self, name: str) -> dict[str, Any]:
        for called, kwargs in reversed(self.calls):
            if called == name:
                return kwargs
        raise AssertionError(f"{name!r} was not called")

    async def remember(self, **kwargs: Any) -> dict[str, Any]:
        self._record("remember", kwargs)
        return {"ok": True}

    async def recall(self, **kwargs: Any) -> dict[str, Any]:
        self._record("recall", kwargs)
        return {"results": ["User prefers tea", "User lives in Berlin"]}

    async def context(self, **kwargs: Any) -> list[str]:
        self._record("context", kwargs)
        return ["active topic: travel planning"]

    async def reflect(self, **kwargs: Any) -> str:
        self._record("reflect", kwargs)
        return "The user is planning a trip and prefers tea."

    async def forget(self, **kwargs: Any) -> dict[str, Any]:
        self._record("forget", kwargs)
        return {"ok": True}

    async def upload(self, **kwargs: Any) -> dict[str, Any]:
        self._record("upload", kwargs)
        return {"ok": True}

    async def inspect(self, **kwargs: Any) -> dict[str, Any]:
        self._record("inspect", kwargs)
        return {"memories": 2}


@pytest.fixture
def client() -> FakeSpectron:
    return FakeSpectron()


@pytest.fixture
def memory(client: FakeSpectron) -> SpectronMemory:
    return SpectronMemory(client, user_id="user-1", session_id="session-1")
