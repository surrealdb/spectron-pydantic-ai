"""Tests for AgentMemoryToolset."""

from __future__ import annotations

import pytest
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from agent_memory_pydantic_ai import ALL_TOOLS, DEFAULT_TOOLS, AgentMemory, AgentMemoryToolset
from tests.conftest import FakeAgentMemory


def test_default_and_all_tool_sets(memory: AgentMemory) -> None:
    assert DEFAULT_TOOLS == ("recall", "context", "remember")
    assert set(DEFAULT_TOOLS).issubset(set(ALL_TOOLS))


def test_unknown_tool_raises(memory: AgentMemory) -> None:
    with pytest.raises(ValueError, match="Unknown Agent Memory tools"):
        AgentMemoryToolset(memory, tools=["recall", "teleport"])


async def test_default_toolset_calls_dispatch(memory: AgentMemory, client: FakeAgentMemory) -> None:
    toolset = AgentMemoryToolset(memory)
    agent = Agent(TestModel(), toolsets=[toolset])
    await agent.run("hello")
    # TestModel exercises every available tool once. The "context" tool is
    # backed by the client's query_context verb.
    called = set(client.names())
    assert {"recall", "query_context", "remember"}.issubset(called)


async def test_custom_tool_subset_limits_surface(
    memory: AgentMemory, client: FakeAgentMemory
) -> None:
    toolset = AgentMemoryToolset(memory, tools=["recall"])
    agent = Agent(TestModel(), toolsets=[toolset])
    await agent.run("hello")
    called = set(client.names())
    assert called == {"recall"}


async def test_forget_is_opt_in(memory: AgentMemory, client: FakeAgentMemory) -> None:
    toolset = AgentMemoryToolset(memory)  # defaults exclude forget
    agent = Agent(TestModel(), toolsets=[toolset])
    await agent.run("hello")
    assert "forget" not in client.names()
