"""Quickstart: give a Pydantic AI agent Spectron memory tools.

The agent decides when to recall or remember. Run it twice: in the first run it
stores a preference, in the second run it recalls it.

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

from spectron_pydantic_ai import SpectronMemory, SpectronToolset


async def main() -> None:
    memory = SpectronMemory.connect(
        context=os.environ["SPECTRON_CONTEXT"],
        endpoint=os.environ["SPECTRON_ENDPOINT"],
        api_key=os.environ["SPECTRON_API_KEY"],
        on_behalf_of="ada",
    )

    agent = Agent(
        "openai:gpt-4o",
        instructions=(
            "You are a helpful assistant with long-term memory. "
            "Recall relevant memories before answering, and remember durable "
            "facts the user shares."
        ),
        toolsets=[SpectronToolset(memory)],
    )

    first = await agent.run("I always travel with a window seat. Note that.")
    print(first.output)

    second = await agent.run("Which seat do I prefer on flights?")
    print(second.output)


if __name__ == "__main__":
    asyncio.run(main())
