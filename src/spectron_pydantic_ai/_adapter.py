"""Single binding point to the Spectron Python client.

Every import of the Spectron SDK lives in this module. The rest of the package
depends only on the :class:`SpectronClient` protocol, so it can be tested with a
fake client and stays decoupled from the exact SDK surface.

Spectron is in early preview. The async client is expected to ship as
``surrealdb.spectron.Spectron`` and to be installable with
``pip install "surrealdb[spectron]"``. If that module is not importable,
:func:`build_client` raises :class:`SpectronImportError` with a clear hint.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from .exceptions import SpectronImportError

_INSTALL_HINT = (
    "The Spectron Python client could not be imported. Spectron is in early "
    'preview: install the client with `pip install "surrealdb[spectron]"` once '
    "you have access, or construct SpectronMemory with an existing client "
    "instance via `SpectronMemory(client)`."
)


@runtime_checkable
class SpectronClient(Protocol):
    """The async Spectron operations this package relies on.

    The concrete client is ``surrealdb.spectron.Spectron``. Only the seven
    memory verbs are needed here. Method arguments are passed through as keyword
    arguments, so this protocol stays deliberately permissive.
    """

    async def remember(self, *args: Any, **kwargs: Any) -> Any: ...

    async def recall(self, *args: Any, **kwargs: Any) -> Any: ...

    async def context(self, *args: Any, **kwargs: Any) -> Any: ...

    async def reflect(self, *args: Any, **kwargs: Any) -> Any: ...

    async def forget(self, *args: Any, **kwargs: Any) -> Any: ...

    async def upload(self, *args: Any, **kwargs: Any) -> Any: ...

    async def inspect(self, *args: Any, **kwargs: Any) -> Any: ...


def build_client(
    url: str,
    namespace: str,
    token: str,
    **client_kwargs: Any,
) -> SpectronClient:
    """Construct a Spectron client from connection details.

    Args:
        url: Base URL of the Spectron service.
        namespace: Spectron namespace to operate in.
        token: Authentication token.
        client_kwargs: Extra keyword arguments forwarded to the client.

    Returns:
        A client instance implementing :class:`SpectronClient`.

    Raises:
        SpectronImportError: If the Spectron client cannot be imported.
    """
    try:
        from surrealdb.spectron import Spectron  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - depends on the environment
        raise SpectronImportError(_INSTALL_HINT) from exc

    return Spectron(url=url, namespace=namespace, token=token, **client_kwargs)


__all__ = ["SpectronClient", "build_client"]
