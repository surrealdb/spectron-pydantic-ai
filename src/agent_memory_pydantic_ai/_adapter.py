"""Single binding point to the AgentMemory Python client.

Every import of the AgentMemory SDK lives in this module. The rest of the package
depends only on the :class:`AgentMemoryClient` protocol, so it can be tested with a
fake client and stays decoupled from the exact SDK surface.

AgentMemory ships in the base ``surrealdb`` package (v3 alpha or newer): the async
client is ``surrealdb.memory.AsyncMemory``. If it cannot be imported,
:func:`build_client` raises :class:`AgentMemoryImportError` with a clear hint.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from .exceptions import AgentMemoryImportError

_INSTALL_HINT = (
    "The AgentMemory Python client could not be imported. AgentMemory ships in the "
    "base SurrealDB SDK (v3 alpha or newer): install it with "
    "`pip install surrealdb`, or construct AgentMemoryMemory with an existing "
    "client instance via `AgentMemoryMemory(client)`."
)


@runtime_checkable
class AgentMemoryClient(Protocol):
    """The async AgentMemory operations this package relies on.

    The concrete client is ``surrealdb.memory.AsyncMemory``. Method arguments are
    passed through as keyword arguments, so this protocol stays deliberately
    permissive. ``documents`` is the SDK's document namespace, used for uploads.
    """

    documents: Any

    async def remember(self, *args: Any, **kwargs: Any) -> Any: ...

    async def remember_many(self, *args: Any, **kwargs: Any) -> Any: ...

    async def recall(self, *args: Any, **kwargs: Any) -> Any: ...

    async def query_context(self, *args: Any, **kwargs: Any) -> Any: ...

    async def reflect(self, *args: Any, **kwargs: Any) -> Any: ...

    async def forget(self, *args: Any, **kwargs: Any) -> Any: ...

    async def inspect(self, *args: Any, **kwargs: Any) -> Any: ...


def build_client(
    context: str,
    endpoint: str,
    api_key: str,
    **client_kwargs: Any,
) -> AgentMemoryClient:
    """Construct a AgentMemory client from connection details.

    Args:
        context: AgentMemory context id (e.g. ``"acme-prod"``). Calls hit
            ``/api/v1/{context}/...``.
        endpoint: Full URL of the AgentMemory host.
        api_key: Bearer token, sent as ``Authorization: Bearer <key>``.
        client_kwargs: Extra keyword arguments forwarded to the client
            (``timeout``, ``max_retries``, ``transport``).

    Returns:
        A client instance implementing :class:`AgentMemoryClient`.

    Raises:
        AgentMemoryImportError: If the AgentMemory client cannot be imported.
    """
    try:
        from surrealdb.memory import AsyncMemory
    except ImportError as exc:  # pragma: no cover - depends on the environment
        raise AgentMemoryImportError(_INSTALL_HINT) from exc

    return AsyncMemory(context, endpoint=endpoint, api_key=api_key, **client_kwargs)


__all__ = ["AgentMemoryClient", "build_client"]
