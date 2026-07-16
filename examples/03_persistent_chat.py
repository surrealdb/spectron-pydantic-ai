"""Persistent chat: per-user and per-session scope, auto-recall, and persistence.

This example combines all three surfaces:

- ``scoped`` gives each user and session its own view of memory.
- the history processor injects relevant memory before each turn.
- ``store_run`` writes each turn back to Spectron so it survives restarts.

Prerequisites:
    pip install "spectron-pydantic-ai" "pydantic-ai-slim[openai]"

Environment variables:
    SPECTRON_CONTEXT, SPECTRON_ENDPOINT, SPECTRON_API_KEY
    OPENAI_API_KEY
"""

from __future__ import annotations

import asyncio
import os

from pydantic_ai import Agent
from pydantic_ai.capabilities import ProcessHistory

from spectron_pydantic_ai import SpectronMemory, spectron_history_processor, store_run


async def chat(user_id: str, session_id: str, turns: list[str]) -> None:
    base = SpectronMemory.connect(
        context=os.environ["SPECTRON_CONTEXT"],
        endpoint=os.environ["SPECTRON_ENDPOINT"],
        api_key=os.environ["SPECTRON_API_KEY"],
    )
    memory = base.scoped(on_behalf_of=user_id, session_id=session_id)

    agent = Agent(
        "openai:gpt-4o",
        instructions="You are a personal assistant with memory of past chats.",
        capabilities=[ProcessHistory(spectron_history_processor(memory))],
    )

    history = None
    for turn in turns:
        result = await agent.run(turn, message_history=history)
        print(f"user: {turn}")
        print(f"assistant: {result.output}\n")
        history = result.all_messages()
        await store_run(memory, result)


async def main() -> None:
    await chat(
        user_id="ada",
        session_id="trip-planning",
        turns=[
            "I am planning a trip to Tokyo in October.",
            "What did I say I was planning?",
        ],
    )


if __name__ == "__main__":
    asyncio.run(main())
