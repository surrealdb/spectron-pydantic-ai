"""Tests for SpectronToolset."""

from __future__ import annotations

import pytest
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from spectron_pydantic_ai import ALL_TOOLS, DEFAULT_TOOLS, SpectronMemory, SpectronToolset
from tests.conftest import FakeSpectron


def test_default_and_all_tool_sets(memory: SpectronMemory) -> None:
    assert DEFAULT_TOOLS == ("recall", "context", "remember")
    assert set(DEFAULT_TOOLS).issubset(set(ALL_TOOLS))


def test_unknown_tool_raises(memory: SpectronMemory) -> None:
    with pytest.raises(ValueError, match="Unknown Spectron tools"):
        SpectronToolset(memory, tools=["recall", "teleport"])


async def test_default_toolset_calls_dispatch(memory: SpectronMemory, client: FakeSpectron) -> None:
    toolset = SpectronToolset(memory)
    agent = Agent(TestModel(), toolsets=[toolset])
    await agent.run("hello")
    # TestModel exercises every available tool once.
    called = set(client.names())
    assert {"recall", "context", "remember"}.issubset(called)


async def test_custom_tool_subset_limits_surface(
    memory: SpectronMemory, client: FakeSpectron
) -> None:
    toolset = SpectronToolset(memory, tools=["recall"])
    agent = Agent(TestModel(), toolsets=[toolset])
    await agent.run("hello")
    called = set(client.names())
    assert called == {"recall"}


async def test_forget_is_opt_in(memory: SpectronMemory, client: FakeSpectron) -> None:
    toolset = SpectronToolset(memory)  # defaults exclude forget
    agent = Agent(TestModel(), toolsets=[toolset])
    await agent.run("hello")
    assert "forget" not in client.names()
