"""Shared test fixtures.

``FakeAgentMemory`` implements the AgentMemory client protocol in memory so the whole
package can be tested without a live AgentMemory service or a real model. It mirrors
the real ``surrealdb.AsyncMemory`` surface: headline verbs take their first
argument positionally, and document uploads live under a ``documents`` namespace.
"""

from __future__ import annotations

from typing import Any

import pytest

from agent_memory_pydantic_ai import AgentMemoryMemory


class FakeDocuments:
    """Stand-in for the client's ``documents`` namespace."""

    def __init__(self, parent: FakeAgentMemory) -> None:
        self._parent = parent

    async def upload(self, path: Any, **kwargs: Any) -> dict[str, Any]:
        self._parent._record("documents.upload", {"path": path, **kwargs})
        return {"ok": True}


class FakeAgentMemory:
    """An in-memory stand-in for the AgentMemory async client.

    Every call is recorded in ``calls`` as a ``(name, kwargs)`` tuple, with the
    positional argument folded into the recorded kwargs under its parameter
    name. Return values are canned so assertions can check formatting and
    dispatch.
    """

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.documents = FakeDocuments(self)

    def _record(self, name: str, kwargs: dict[str, Any]) -> None:
        self.calls.append((name, kwargs))

    def names(self) -> list[str]:
        return [name for name, _ in self.calls]

    def last(self, name: str) -> dict[str, Any]:
        for called, kwargs in reversed(self.calls):
            if called == name:
                return kwargs
        raise AssertionError(f"{name!r} was not called")

    async def remember(self, text: str | None = None, **kwargs: Any) -> dict[str, Any]:
        self._record("remember", {"text": text, **kwargs})
        return {"ok": True}

    async def remember_many(self, items: Any, **kwargs: Any) -> dict[str, Any]:
        self._record("remember_many", {"items": items, **kwargs})
        return {"ok": True}

    async def recall(self, query: str, **kwargs: Any) -> dict[str, Any]:
        self._record("recall", {"query": query, **kwargs})
        return {"results": ["User prefers tea", "User lives in Berlin"]}

    async def query_context(self, query: str = "", **kwargs: Any) -> list[str]:
        self._record("query_context", {"query": query, **kwargs})
        return ["active topic: travel planning"]

    async def reflect(self, query: str, **kwargs: Any) -> str:
        self._record("reflect", {"query": query, **kwargs})
        return "The user is planning a trip and prefers tea."

    async def forget(self, query: str, **kwargs: Any) -> dict[str, Any]:
        self._record("forget", {"query": query, **kwargs})
        return {"ok": True}

    async def inspect(self, ref: str, **kwargs: Any) -> dict[str, Any]:
        self._record("inspect", {"ref": ref, **kwargs})
        return {"memories": 2}


@pytest.fixture
def client() -> FakeAgentMemory:
    return FakeAgentMemory()


@pytest.fixture
def memory(client: FakeAgentMemory) -> AgentMemoryMemory:
    return AgentMemoryMemory(
        client,
        session_id="session-1",
        scope="org/acme",
        on_behalf_of="user-1",
    )
