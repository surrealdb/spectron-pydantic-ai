"""Single binding point to the Spectron Python client.

Every import of the Spectron SDK lives in this module. The rest of the package
depends only on the :class:`SpectronClient` protocol, so it can be tested with a
fake client and stays decoupled from the exact SDK surface.

Spectron ships in the base ``surrealdb`` package (v3 alpha or newer): the async
client is ``surrealdb.AsyncSpectron``. If it cannot be imported, :func:`build_client`
raises :class:`SpectronImportError` with a clear hint.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from .exceptions import SpectronImportError

_INSTALL_HINT = (
    "The Spectron Python client could not be imported. Spectron ships in the "
    "base SurrealDB SDK (v3 alpha or newer): install it with "
    "`pip install surrealdb`, or construct SpectronMemory with an existing "
    "client instance via `SpectronMemory(client)`."
)


@runtime_checkable
class SpectronClient(Protocol):
    """The async Spectron operations this package relies on.

    The concrete client is ``surrealdb.AsyncSpectron``. Method arguments are
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
) -> SpectronClient:
    """Construct a Spectron client from connection details.

    Args:
        context: Spectron context id (e.g. ``"acme-prod"``). Calls hit
            ``/api/v1/{context}/...``.
        endpoint: Full URL of the Spectron host.
        api_key: Bearer token, sent as ``Authorization: Bearer <key>``.
        client_kwargs: Extra keyword arguments forwarded to the client
            (``timeout``, ``max_retries``, ``transport``).

    Returns:
        A client instance implementing :class:`SpectronClient`.

    Raises:
        SpectronImportError: If the Spectron client cannot be imported.
    """
    try:
        from surrealdb import AsyncSpectron
    except ImportError as exc:  # pragma: no cover - depends on the environment
        raise SpectronImportError(_INSTALL_HINT) from exc

    return AsyncSpectron(context, endpoint=endpoint, api_key=api_key, **client_kwargs)


__all__ = ["SpectronClient", "build_client"]
