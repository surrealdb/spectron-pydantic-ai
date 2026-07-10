"""Tests for the SpectronMemory scoped wrapper."""

from __future__ import annotations

import pytest

from spectron_pydantic_ai import SpectronImportError, SpectronMemory
from tests.conftest import FakeSpectron


async def test_scope_is_injected_into_calls(memory: SpectronMemory, client: FakeSpectron) -> None:
    await memory.remember("User prefers tea")
    kwargs = client.last("remember")
    assert kwargs["content"] == "User prefers tea"
    assert kwargs["user_id"] == "user-1"
    assert kwargs["session_id"] == "session-1"


async def test_none_values_are_not_sent(memory: SpectronMemory, client: FakeSpectron) -> None:
    await memory.recall("tea")
    kwargs = client.last("recall")
    assert "limit" not in kwargs
    assert "agent_id" not in kwargs


async def test_call_level_kwargs_override_scope(client: FakeSpectron) -> None:
    memory = SpectronMemory(client, user_id="user-1")
    await memory.recall("tea", user_id="user-2", limit=3)
    kwargs = client.last("recall")
    assert kwargs["user_id"] == "user-2"
    assert kwargs["limit"] == 3


async def test_scoped_narrows_without_mutating(client: FakeSpectron) -> None:
    base = SpectronMemory(client, user_id="user-1")
    narrowed = base.scoped(session_id="session-9")
    assert base.session_id is None
    assert narrowed.session_id == "session-9"
    assert narrowed.user_id == "user-1"
    assert narrowed.client is base.client


async def test_each_operation_dispatches(memory: SpectronMemory, client: FakeSpectron) -> None:
    await memory.remember("a")
    await memory.recall("b")
    await memory.context()
    await memory.reflect("c")
    await memory.forget("d")
    await memory.upload({"x": 1})
    await memory.inspect()
    assert client.names() == [
        "remember",
        "recall",
        "context",
        "reflect",
        "forget",
        "upload",
        "inspect",
    ]


async def test_upload_passes_data_when_given(memory: SpectronMemory, client: FakeSpectron) -> None:
    await memory.upload({"doc": "hello"})
    assert client.last("upload")["data"] == {"doc": "hello"}


def test_connect_raises_clear_error_without_sdk() -> None:
    # The Spectron SDK is not installed in the test environment, so connecting
    # should raise a helpful, typed error rather than a bare ImportError.
    with pytest.raises(SpectronImportError):
        SpectronMemory.connect("http://localhost:8000", "ns", "token")
