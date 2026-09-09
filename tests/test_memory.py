"""Tests for the AgentMemoryMemory scoped wrapper."""

from __future__ import annotations

import pytest

from agent_memory_pydantic_ai import AgentMemoryError, AgentMemoryImportError, AgentMemoryMemory
from tests.conftest import FakeAgentMemory


async def test_scope_is_injected_into_calls(
    memory: AgentMemoryMemory, client: FakeAgentMemory
) -> None:
    await memory.remember("User prefers tea")
    kwargs = client.last("remember")
    assert kwargs["text"] == "User prefers tea"
    assert kwargs["on_behalf_of"] == "user-1"
    assert kwargs["session_id"] == "session-1"
    assert kwargs["scopes"] == "org/acme"


async def test_reads_use_lens_not_scopes(
    memory: AgentMemoryMemory, client: FakeAgentMemory
) -> None:
    await memory.recall("tea")
    kwargs = client.last("recall")
    assert kwargs["lens"] == "org/acme"
    assert "scopes" not in kwargs
    assert kwargs["session_id"] == "session-1"


async def test_query_context_omits_session(
    memory: AgentMemoryMemory, client: FakeAgentMemory
) -> None:
    await memory.query_context("trip")
    kwargs = client.last("query_context")
    assert kwargs["lens"] == "org/acme"
    assert "session_id" not in kwargs


async def test_none_values_are_not_sent(memory: AgentMemoryMemory, client: FakeAgentMemory) -> None:
    await memory.recall("tea")
    kwargs = client.last("recall")
    assert "k" not in kwargs
    assert "mode" not in kwargs


async def test_call_level_kwargs_override_scope(client: FakeAgentMemory) -> None:
    memory = AgentMemoryMemory(client, on_behalf_of="user-1")
    await memory.recall("tea", on_behalf_of="user-2", k=3)
    kwargs = client.last("recall")
    assert kwargs["on_behalf_of"] == "user-2"
    assert kwargs["k"] == 3


async def test_scoped_narrows_without_mutating(client: FakeAgentMemory) -> None:
    base = AgentMemoryMemory(client, on_behalf_of="user-1")
    narrowed = base.scoped(session_id="session-9")
    assert base.session_id is None
    assert narrowed.session_id == "session-9"
    assert narrowed.on_behalf_of == "user-1"
    assert narrowed.client is base.client


async def test_each_operation_dispatches(
    memory: AgentMemoryMemory, client: FakeAgentMemory
) -> None:
    await memory.remember("a")
    await memory.recall("b")
    await memory.query_context("c")
    await memory.reflect("d")
    await memory.forget("e")
    await memory.upload(b"file-bytes")
    await memory.inspect("ref:1")
    assert client.names() == [
        "remember",
        "recall",
        "query_context",
        "reflect",
        "forget",
        "documents.upload",
        "inspect",
    ]


async def test_upload_routes_to_documents_namespace(
    memory: AgentMemoryMemory, client: FakeAgentMemory
) -> None:
    await memory.upload("/tmp/report.pdf", title="Report")
    kwargs = client.last("documents.upload")
    assert kwargs["path"] == "/tmp/report.pdf"
    assert kwargs["title"] == "Report"
    assert kwargs["scopes"] == "org/acme"


async def test_connect_wraps_built_client(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeAgentMemory()
    captured: dict[str, object] = {}

    def fake_build(context: str, endpoint: str, api_key: str, **client_kwargs: object) -> object:
        captured.update(
            context=context, endpoint=endpoint, api_key=api_key, client_kwargs=client_kwargs
        )
        return fake

    monkeypatch.setattr("agent_memory_pydantic_ai.memory.build_client", fake_build)
    memory = AgentMemoryMemory.connect(
        "acme-prod",
        "https://api.agent_memory.example",
        "sk-1",
        session_id="s1",
        scope="org/acme",
        timeout=5.0,
    )
    assert memory.client is fake
    assert memory.session_id == "s1"
    assert memory.scope == "org/acme"
    assert captured["context"] == "acme-prod"
    assert captured["endpoint"] == "https://api.agent_memory.example"
    assert captured["api_key"] == "sk-1"
    assert captured["client_kwargs"] == {"timeout": 5.0}


def test_import_error_is_a_agent_memory_error() -> None:
    assert issubclass(AgentMemoryImportError, AgentMemoryError)
    assert issubclass(AgentMemoryImportError, ImportError)
