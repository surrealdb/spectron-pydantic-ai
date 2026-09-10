"""Auto-recall: inject relevant memory before each run with no tool call.

The history processor looks at the latest user message, recalls related
memories from Agent Memory, and prepends them as context. The agent never has to
decide to call a tool.

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
from pydantic_ai.capabilities import ProcessHistory

from agent_memory_pydantic_ai import AgentMemory, agent_memory_history_processor


async def main() -> None:
    memory = AgentMemory.connect(
        context=os.environ["AGENT_MEMORY_CONTEXT"],
        endpoint=os.environ["AGENT_MEMORY_ENDPOINT"],
        api_key=os.environ["AGENT_MEMORY_API_KEY"],
        on_behalf_of="ada",
    )

    # Seed a fact so recall has something to find.
    await memory.remember("Ada is allergic to peanuts.", memory_category="identity")

    processor = agent_memory_history_processor(memory, limit=5)
    agent = Agent(
        "openai:gpt-4o",
        instructions="You are a careful assistant. Use any provided memory context.",
        capabilities=[ProcessHistory(processor)],
    )

    result = await agent.run("Suggest a snack for my flight.")
    print(result.output)


if __name__ == "__main__":
    asyncio.run(main())
