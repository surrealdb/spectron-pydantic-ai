"""A Pydantic AI toolset backed by Spectron memory.

:class:`SpectronToolset` exposes Spectron operations as tools the agent can
call on its own. Attach it to an agent with ``Agent(..., toolsets=[toolset])``.
The docstrings on each tool are what the model reads to decide when to call
them, so they are written for that audience.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from pydantic_ai import FunctionToolset

from ._format import format_results
from .memory import SpectronMemory

DEFAULT_TOOLS: tuple[str, ...] = ("recall", "context", "remember")
"""Operations exposed by default. Read and write, without deletion."""

ALL_TOOLS: tuple[str, ...] = (
    "recall",
    "context",
    "remember",
    "reflect",
    "forget",
)
"""Every operation the toolset can expose."""


def _make_recall(memory: SpectronMemory) -> Callable[..., Any]:
    async def recall(query: str, limit: int = 8) -> str:
        """Search long-term memory for information relevant to a query.

        Use this before answering to look up facts, user preferences, and
        details from earlier conversations. Returns a list of matching memories.
        """
        results = await memory.recall(query, k=limit)
        return format_results(results) or "No relevant memories found."

    return recall


def _make_context(memory: SpectronMemory) -> Callable[..., Any]:
    async def context(query: str = "") -> str:
        """Fetch the current working context: active topics and recent intents.

        Use this at the start of a turn to load what the conversation is
        currently about. Pass a query to focus the context, or leave it empty
        for the general working set.
        """
        results = await memory.query_context(query or "")
        return format_results(results) or "No active context."

    return context


def _make_remember(memory: SpectronMemory) -> Callable[..., Any]:
    async def remember(content: str) -> str:
        """Store a fact or preference in long-term memory for future recall.

        Use this when the user shares durable information worth keeping, such as
        a preference, a decision, or a personal detail.
        """
        await memory.remember(content)
        return "Stored in memory."

    return remember


def _make_reflect(memory: SpectronMemory) -> Callable[..., Any]:
    async def reflect(query: str) -> str:
        """Synthesise an answer from across stored memories.

        Use this for questions that require combining several remembered facts
        rather than a single lookup.
        """
        results = await memory.reflect(query)
        return format_results(results) or "Nothing to reflect on yet."

    return reflect


def _make_forget(memory: SpectronMemory) -> Callable[..., Any]:
    async def forget(target: str) -> str:
        """Delete memories matching a description or identifier.

        Use this only when the user explicitly asks to remove information.
        """
        await memory.forget(target)
        return "Removed from memory."

    return forget


_TOOL_FACTORIES: dict[str, Callable[[SpectronMemory], Callable[..., Any]]] = {
    "recall": _make_recall,
    "context": _make_context,
    "remember": _make_remember,
    "reflect": _make_reflect,
    "forget": _make_forget,
}


class SpectronToolset(FunctionToolset[Any]):
    """Expose Spectron memory operations as agent tools.

    Args:
        memory: The scoped memory the tools operate on.
        tools: Which operations to expose. Defaults to :data:`DEFAULT_TOOLS`
            (``recall``, ``context``, ``remember``). Pass a subset or
            :data:`ALL_TOOLS` to change the surface.
        id: Optional toolset identifier.

    Example:
        >>> from pydantic_ai import Agent
        >>> toolset = SpectronToolset(memory)  # doctest: +SKIP
        >>> agent = Agent("openai:gpt-4o", toolsets=[toolset])  # doctest: +SKIP
    """

    def __init__(
        self,
        memory: SpectronMemory,
        *,
        tools: Sequence[str] = DEFAULT_TOOLS,
        id: str | None = None,
    ) -> None:
        self.memory = memory
        unknown = [name for name in tools if name not in _TOOL_FACTORIES]
        if unknown:
            valid = ", ".join(_TOOL_FACTORIES)
            raise ValueError(f"Unknown Spectron tools: {', '.join(unknown)}. Valid tools: {valid}.")
        functions = [_TOOL_FACTORIES[name](memory) for name in tools]
        super().__init__(functions, id=id or "spectron")


__all__ = ["ALL_TOOLS", "DEFAULT_TOOLS", "SpectronToolset"]
