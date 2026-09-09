"""High-level, scoped wrapper around a AgentMemory client.

:class:`AgentMemoryMemory` carries a memory scope and forwards AgentMemory operations
to the underlying client, merging the scope into every call. The scope maps
onto the SDK's own primitives:

- ``session_id`` — the conversation, forwarded to the verbs that accept it
  (``remember``, ``recall``, ``remember_many``).
- ``scope`` — a AgentMemory ``ScopeArg`` forwarded as ``scopes=`` on writes and as
  ``lens=`` on reads, so one wrapper can partition memory by tenant/topic.
- ``on_behalf_of`` — the principal a call acts for, forwarded to every verb.

One connection can serve many users and sessions by creating narrowed views
with :meth:`AgentMemoryMemory.scoped`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._adapter import AgentMemoryClient, build_client

if TYPE_CHECKING:
    from surrealdb.memory import ScopeArg
else:  # runtime: keep the package importable without the SDK installed
    ScopeArg = Any


def _prune(mapping: dict[str, Any]) -> dict[str, Any]:
    """Drop keys whose value is ``None`` so they are not sent to the client."""
    return {key: value for key, value in mapping.items() if value is not None}


class AgentMemoryMemory:
    """Scoped access to AgentMemory memory operations.

    Args:
        client: An object implementing the AgentMemory client protocol.
        session_id: Optional conversation or session identifier.
        scope: Optional AgentMemory scope (``ScopeArg``) applied as ``scopes`` on
            writes and ``lens`` on reads.
        on_behalf_of: Optional principal the operations act for.

    The scope values are added as keyword arguments to every operation that
    accepts them. Passing the same keyword explicitly to a method overrides the
    stored scope for that call.
    """

    def __init__(
        self,
        client: AgentMemoryClient,
        *,
        session_id: str | None = None,
        scope: ScopeArg = None,
        on_behalf_of: str | None = None,
    ) -> None:
        self.client = client
        self.session_id = session_id
        self.scope = scope
        self.on_behalf_of = on_behalf_of

    @classmethod
    def connect(
        cls,
        context: str,
        endpoint: str,
        api_key: str,
        *,
        session_id: str | None = None,
        scope: ScopeArg = None,
        on_behalf_of: str | None = None,
        **client_kwargs: Any,
    ) -> AgentMemoryMemory:
        """Build a client from connection details and wrap it.

        Args:
            context: AgentMemory context id (e.g. ``"acme-prod"``).
            endpoint: Full URL of the AgentMemory host.
            api_key: Bearer token.
            session_id: Optional conversation or session identifier.
            scope: Optional AgentMemory scope applied to every operation.
            on_behalf_of: Optional principal the operations act for.
            client_kwargs: Extra keyword arguments forwarded to the client
                (``timeout``, ``max_retries``, ``transport``).
        """
        client = build_client(context, endpoint, api_key, **client_kwargs)
        return cls(client, session_id=session_id, scope=scope, on_behalf_of=on_behalf_of)

    def scoped(
        self,
        *,
        session_id: str | None = None,
        scope: ScopeArg = None,
        on_behalf_of: str | None = None,
    ) -> AgentMemoryMemory:
        """Return a new view over the same client with a narrowed scope.

        Only the values you pass are changed. Unspecified values are inherited
        from the current instance.
        """
        return AgentMemoryMemory(
            self.client,
            session_id=session_id if session_id is not None else self.session_id,
            scope=scope if scope is not None else self.scope,
            on_behalf_of=on_behalf_of if on_behalf_of is not None else self.on_behalf_of,
        )

    def _write_scope(self) -> dict[str, Any]:
        """Scope keywords for write verbs (``scopes`` + session + principal)."""
        return {
            "session_id": self.session_id,
            "scopes": self.scope,
            "on_behalf_of": self.on_behalf_of,
        }

    def _read_scope(self, *, with_session: bool = True) -> dict[str, Any]:
        """Scope keywords for read verbs (``lens`` + principal, session optional)."""
        base: dict[str, Any] = {"lens": self.scope, "on_behalf_of": self.on_behalf_of}
        if with_session:
            base["session_id"] = self.session_id
        return base

    @staticmethod
    def _merge(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
        """Merge call-level keyword arguments on top of a scope base."""
        merged = dict(base)
        merged.update(overrides)
        return _prune(merged)

    async def remember(
        self,
        text: str | None = None,
        *,
        infer: str | None = None,
        memory_category: str | None = None,
        labels: list[str] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Store a new memory.

        Args:
            text: The fact, preference, or note to store.
            infer: Extraction path (``"full"``, ``"triples"``, ``"preview"``,
                ``"none"``).
            memory_category: Optional AgentMemory memory category.
            labels: Optional ``key=value`` labels recorded on the rows.
            kwargs: Extra keyword arguments forwarded to the client.
        """
        payload = self._merge(
            self._write_scope(),
            {"infer": infer, "memory_category": memory_category, "labels": labels, **kwargs},
        )
        return await self.client.remember(text, **payload)

    async def remember_many(
        self,
        items: list[dict[str, Any]],
        *,
        extract: str | None = None,
        infer: str | None = None,
        labels: list[str] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Store a batch of items (e.g. a conversation) in one call.

        Args:
            items: Records to store, such as ``{"role": ..., "content": ...}``.
            extract: Batch extraction mode (``"per_message"`` or
                ``"whole_conversation"``).
            infer: Extraction path forwarded to the client.
            labels: Optional ``key=value`` labels recorded on the rows.
            kwargs: Extra keyword arguments forwarded to the client.
        """
        payload = self._merge(
            self._write_scope(),
            {"extract": extract, "infer": infer, "labels": labels, **kwargs},
        )
        return await self.client.remember_many(items, **payload)

    async def recall(
        self,
        query: str,
        *,
        k: int | None = None,
        mode: str | None = None,
        labels: list[str] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Search memory for entries relevant to a query.

        Args:
            query: Natural language query.
            k: Optional maximum number of results.
            mode: Optional recall mode.
            labels: Optional label filters.
            kwargs: Extra keyword arguments forwarded to the client.
        """
        payload = self._merge(
            self._read_scope(with_session=True),
            {"k": k, "mode": mode, "labels": labels, **kwargs},
        )
        return await self.client.recall(query, **payload)

    async def query_context(
        self,
        query: str = "",
        *,
        k: int | None = None,
        labels: list[str] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Fetch the working context for a query.

        Args:
            query: Query used to focus the context.
            k: Optional maximum number of items.
            labels: Optional label filters.
            kwargs: Extra keyword arguments forwarded to the client.
        """
        payload = self._merge(
            self._read_scope(with_session=False),
            {"k": k, "labels": labels, **kwargs},
        )
        return await self.client.query_context(query, **payload)

    async def reflect(
        self,
        query: str,
        *,
        persist: bool | None = None,
        **kwargs: Any,
    ) -> Any:
        """Synthesise an answer from stored memory, optionally persisting it.

        Args:
            query: The question to reflect on.
            persist: Whether to store the synthesised result as new facts.
            kwargs: Extra keyword arguments forwarded to the client.
        """
        payload = self._merge(
            {"on_behalf_of": self.on_behalf_of},
            {"persist": persist, **kwargs},
        )
        return await self.client.reflect(query, **payload)

    async def forget(
        self,
        query: str,
        *,
        purge: bool | None = None,
        **kwargs: Any,
    ) -> Any:
        """Delete memory matching a query.

        Args:
            query: Query describing what to forget.
            purge: Whether to hard-delete rather than tombstone.
            kwargs: Extra keyword arguments forwarded to the client.
        """
        payload = self._merge(
            {"on_behalf_of": self.on_behalf_of},
            {"purge": purge, **kwargs},
        )
        return await self.client.forget(query, **payload)

    async def inspect(self, ref: str, **kwargs: Any) -> Any:
        """Return diagnostic information about a memory reference.

        Args:
            ref: The reference to inspect.
            kwargs: Extra keyword arguments forwarded to the client.
        """
        payload = self._merge({"on_behalf_of": self.on_behalf_of}, kwargs)
        return await self.client.inspect(ref, **payload)

    async def upload(
        self,
        path: Any,
        *,
        content_type: str | None = None,
        filename: str | None = None,
        title: str | None = None,
        source: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Ingest a document via the AgentMemory documents namespace.

        Args:
            path: File path, file-like object, or bytes to upload.
            content_type: Optional MIME type.
            filename: Optional filename to record.
            title: Optional document title.
            source: Optional source identifier.
            kwargs: Extra keyword arguments forwarded to the client.
        """
        payload = self._merge(
            {"scopes": self.scope, "on_behalf_of": self.on_behalf_of},
            {
                "content_type": content_type,
                "filename": filename,
                "title": title,
                "source": source,
                **kwargs,
            },
        )
        return await self.client.documents.upload(path, **payload)


__all__ = ["AgentMemoryMemory"]
