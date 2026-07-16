"""Auto-recall: inject relevant memory before each run with no tool call.

The history processor looks at the latest user message, recalls related
memories from Spectron, and prepends them as context. The agent never has to
decide to call a tool.

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

from spectron_pydantic_ai import SpectronMemory, spectron_history_processor


async def main() -> None:
    memory = SpectronMemory.connect(
        context=os.environ["SPECTRON_CONTEXT"],
        endpoint=os.environ["SPECTRON_ENDPOINT"],
        api_key=os.environ["SPECTRON_API_KEY"],
        on_behalf_of="ada",
    )

    # Seed a fact so recall has something to find.
    await memory.remember("Ada is allergic to peanuts.", memory_category="identity")

    processor = spectron_history_processor(memory, limit=5)
    agent = Agent(
        "openai:gpt-4o",
        instructions="You are a careful assistant. Use any provided memory context.",
        capabilities=[ProcessHistory(processor)],
    )

    result = await agent.run("Suggest a snack for my flight.")
    print(result.output)


if __name__ == "__main__":
    asyncio.run(main())
