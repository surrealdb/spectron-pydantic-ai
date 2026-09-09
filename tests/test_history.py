"""Tests for the history processor and persistence helpers."""

from __future__ import annotations

from pydantic_ai import (
    Agent,
    ModelRequest,
    ModelResponse,
    SystemPromptPart,
    TextPart,
    UserPromptPart,
)
from pydantic_ai.capabilities import ProcessHistory
from pydantic_ai.models.test import TestModel

from agent_memory_pydantic_ai import (
    AgentMemoryMemory,
    agent_memory_history_processor,
    store_messages,
    store_run,
)
from tests.conftest import FakeAgentMemory


def _system_texts(messages: list) -> list[str]:
    return [
        part.content
        for message in messages
        if isinstance(message, ModelRequest)
        for part in message.parts
        if isinstance(part, SystemPromptPart)
    ]


async def test_processor_injects_recalled_memory(
    memory: AgentMemoryMemory, client: FakeAgentMemory
) -> None:
    processor = agent_memory_history_processor(memory)
    agent = Agent(TestModel(), capabilities=[ProcessHistory(processor)])
    result = await agent.run("Where do I live?")

    assert "recall" in client.names()
    injected = _system_texts(result.all_messages())
    assert any("User lives in Berlin" in text for text in injected)
    assert any("Relevant memory from AgentMemory" in text for text in injected)


async def test_context_mode_uses_context_operation(
    memory: AgentMemoryMemory, client: FakeAgentMemory
) -> None:
    processor = agent_memory_history_processor(memory, mode="context")
    agent = Agent(TestModel(), capabilities=[ProcessHistory(processor)])
    result = await agent.run("What are we working on?")

    assert "query_context" in client.names()
    injected = _system_texts(result.all_messages())
    assert any("travel planning" in text for text in injected)


async def test_recall_mode_skips_when_no_user_text(
    memory: AgentMemoryMemory, client: FakeAgentMemory
) -> None:
    processor = agent_memory_history_processor(memory)
    # A history with no user prompt should not trigger a recall call.
    messages = [ModelResponse(parts=[TextPart(content="hi")])]

    class _Ctx:
        pass

    out = await processor(_Ctx(), messages)  # type: ignore[arg-type]
    assert out is messages
    assert "recall" not in client.names()


async def test_custom_template_is_applied(memory: AgentMemoryMemory) -> None:
    processor = agent_memory_history_processor(memory, template=lambda block: f"MEMORY::\n{block}")
    agent = Agent(TestModel(), capabilities=[ProcessHistory(processor)])
    result = await agent.run("Where do I live?")
    injected = _system_texts(result.all_messages())
    assert any(text.startswith("MEMORY::") for text in injected)


async def test_store_messages_builds_transcript(
    memory: AgentMemoryMemory, client: FakeAgentMemory
) -> None:
    messages = [
        ModelRequest(parts=[UserPromptPart(content="I prefer window seats")]),
        ModelResponse(parts=[TextPart(content="Noted, window seats it is.")]),
    ]
    await store_messages(memory, messages)
    transcript = client.last("remember_many")["items"]
    assert transcript == [
        {"role": "user", "content": "I prefer window seats"},
        {"role": "assistant", "content": "Noted, window seats it is."},
    ]


async def test_store_messages_skips_empty(
    memory: AgentMemoryMemory, client: FakeAgentMemory
) -> None:
    result = await store_messages(memory, [])
    assert result is None
    assert "remember_many" not in client.names()


async def test_store_run_persists_new_messages(
    memory: AgentMemoryMemory, client: FakeAgentMemory
) -> None:
    agent = Agent(TestModel())
    result = await agent.run("hello")
    await store_run(memory, result)
    assert "remember_many" in client.names()
    transcript = client.last("remember_many")["items"]
    assert any(turn["role"] == "user" for turn in transcript)
