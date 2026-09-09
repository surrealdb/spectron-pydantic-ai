"""Quickstart: give a Pydantic AI agent Agent Memory tools.

The agent decides when to recall or remember. Run it twice: in the first run it
stores a preference, in the second run it recalls it.

Prerequisites:
    pip install "agent-memory-pydantic-ai" "pydantic-ai-slim[openai]"

Environment variables:
    AGENT_MEMORY_CONTEXT, AGENT_MEMORY_ENDPOINT, AGENT_MEMORY_API_KEY
    OPENAI_API_KEY
"""

from __future__ import annotations

import asyncio
import os

from pydantic_ai import Agent

from agent_memory_pydantic_ai import AgentMemory, AgentMemoryToolset


async def main() -> None:
    memory = AgentMemory.connect(
        context=os.environ["AGENT_MEMORY_CONTEXT"],
        endpoint=os.environ["AGENT_MEMORY_ENDPOINT"],
        api_key=os.environ["AGENT_MEMORY_API_KEY"],
        on_behalf_of="ada",
    )

    agent = Agent(
        "openai:gpt-4o",
        instructions=(
            "You are a helpful assistant with long-term memory. "
            "Recall relevant memories before answering, and remember durable "
            "facts the user shares."
        ),
        toolsets=[AgentMemoryToolset(memory)],
    )

    first = await agent.run("I always travel with a window seat. Note that.")
    print(first.output)

    second = await agent.run("Which seat do I prefer on flights?")
    print(second.output)


if __name__ == "__main__":
    asyncio.run(main())
