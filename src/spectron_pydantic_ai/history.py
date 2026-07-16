"""Auto-recall history processor and persistence helpers.

The history processor injects relevant memory before each model request, so the
agent gets baseline context without having to call a tool. The persistence
helpers write a run's messages back to Spectron so conversations survive across
sessions.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Literal

from pydantic_ai import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    RunContext,
    SystemPromptPart,
    TextPart,
    UserPromptPart,
)

from ._format import format_results
from .memory import SpectronMemory

HistoryProcessor = Callable[[RunContext[Any], list[ModelMessage]], Awaitable[list[ModelMessage]]]

DEFAULT_HEADER = "Relevant memory from Spectron:"


def _latest_user_text(messages: list[ModelMessage]) -> str | None:
    """Return the text of the most recent user prompt, if any."""
    for message in reversed(messages):
        if isinstance(message, ModelRequest):
            for part in message.parts:
                if isinstance(part, UserPromptPart) and isinstance(part.content, str):
                    return part.content
    return None


def spectron_history_processor(
    memory: SpectronMemory,
    *,
    mode: Literal["recall", "context"] = "recall",
    limit: int = 8,
    role: Literal["system", "user"] = "system",
    header: str = DEFAULT_HEADER,
    template: Callable[[str], str] | None = None,
) -> HistoryProcessor:
    """Build a history processor that injects relevant memory before each request.

    Register the result with ``Agent(..., capabilities=[ProcessHistory(proc)])``.

    Args:
        memory: The scoped memory to query.
        mode: ``"recall"`` searches by the latest user prompt; ``"context"``
            fetches the current working set.
        limit: Maximum number of memories to recall (``recall`` mode only).
        role: Whether the injected block is a system or user message.
        header: Line placed above the memory block. Ignored when ``template``
            is given.
        template: Optional function that renders the final text from the
            formatted memory block.

    Returns:
        An async history processor.
    """

    def render(block: str) -> str:
        if template is not None:
            return template(block)
        return f"{header}\n{block}"

    async def process(ctx: RunContext[Any], messages: list[ModelMessage]) -> list[ModelMessage]:
        query = _latest_user_text(messages)
        if mode == "context":
            results = await memory.query_context(query or "")
        else:
            if not query:
                return messages
            results = await memory.recall(query, k=limit)

        block = format_results(results)
        if not block:
            return messages

        text = render(block)
        part = SystemPromptPart(content=text) if role == "system" else UserPromptPart(content=text)
        return [ModelRequest(parts=[part]), *messages]

    return process


def _messages_to_transcript(messages: list[ModelMessage]) -> list[dict[str, str]]:
    """Extract a list of ``{"role", "content"}`` turns from model messages."""
    transcript: list[dict[str, str]] = []
    for message in messages:
        if isinstance(message, ModelRequest):
            for part in message.parts:
                if isinstance(part, SystemPromptPart) and part.content:
                    transcript.append({"role": "system", "content": part.content})
                elif isinstance(part, UserPromptPart) and isinstance(part.content, str):
                    transcript.append({"role": "user", "content": part.content})
        elif isinstance(message, ModelResponse):
            for part in message.parts:
                if isinstance(part, TextPart) and part.content:
                    transcript.append({"role": "assistant", "content": part.content})
    return transcript


async def store_messages(
    memory: SpectronMemory,
    messages: list[ModelMessage],
    *,
    extract: str = "whole_conversation",
    **kwargs: Any,
) -> Any:
    """Persist a list of model messages to Spectron.

    The messages are reduced to a ``{"role", "content"}`` transcript and stored
    with Spectron's ``remember_many`` batch operation. Extra keyword arguments
    are forwarded. Returns ``None`` when there is nothing to store.
    """
    transcript = _messages_to_transcript(messages)
    if not transcript:
        return None
    return await memory.remember_many(transcript, extract=extract, **kwargs)


async def store_run(
    memory: SpectronMemory,
    result: Any,
    *,
    include_all: bool = False,
    **kwargs: Any,
) -> Any:
    """Persist the messages from a completed agent run.

    Args:
        memory: The scoped memory to store into.
        result: An ``AgentRunResult`` (the return value of ``agent.run``).
        include_all: Store the full history rather than only the new messages
            produced by this run.
        kwargs: Extra keyword arguments forwarded to ``remember_many``.
    """
    messages = result.all_messages() if include_all else result.new_messages()
    return await store_messages(memory, messages, **kwargs)


__all__ = ["HistoryProcessor", "spectron_history_processor", "store_messages", "store_run"]
