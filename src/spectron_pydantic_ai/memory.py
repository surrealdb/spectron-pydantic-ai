"""High-level, scoped wrapper around a Spectron client.

:class:`SpectronMemory` carries a memory scope (user, session, agent) and
forwards the seven Spectron operations to the underlying client, merging the
scope into every call. One connection can serve many users and sessions by
creating narrowed views with :meth:`SpectronMemory.scoped`.
"""

from __future__ import annotations

from typing import Any

from ._adapter import SpectronClient, build_client


def _prune(mapping: dict[str, Any]) -> dict[str, Any]:
    """Drop keys whose value is ``None`` so they are not sent to the client."""
    return {key: value for key, value in mapping.items() if value is not None}


class SpectronMemory:
    """Scoped access to Spectron memory operations.

    Args:
        client: An object implementing the Spectron client protocol.
        user_id: Optional principal the memories belong to.
        session_id: Optional conversation or session identifier.
        agent_id: Optional agent identifier.

    The scope values are added as keyword arguments to every operation. Passing
    the same keyword explicitly to a method overrides the stored scope for that
    call.
    """

    def __init__(
        self,
        client: SpectronClient,
        *,
        user_id: str | None = None,
        session_id: str | None = None,
        agent_id: str | None = None,
    ) -> None:
        self.client = client
        self.user_id = user_id
        self.session_id = session_id
        self.agent_id = agent_id

    @classmethod
    def connect(
        cls,
        url: str,
        namespace: str,
        token: str,
        *,
        user_id: str | None = None,
        session_id: str | None = None,
        agent_id: str | None = None,
        **client_kwargs: Any,
    ) -> SpectronMemory:
        """Build a client from connection details and wrap it.

        Args:
            url: Base URL of the Spectron service.
            namespace: Spectron namespace to operate in.
            token: Authentication token.
            user_id: Optional principal the memories belong to.
            session_id: Optional conversation or session identifier.
            agent_id: Optional agent identifier.
            client_kwargs: Extra keyword arguments forwarded to the client.
        """
        client = build_client(url, namespace, token, **client_kwargs)
        return cls(client, user_id=user_id, session_id=session_id, agent_id=agent_id)

    @property
    def scope(self) -> dict[str, Any]:
        """The active scope as a mapping, with unset values removed."""
        return _prune(
            {
                "user_id": self.user_id,
                "session_id": self.session_id,
                "agent_id": self.agent_id,
            }
        )

    def scoped(
        self,
        *,
        user_id: str | None = None,
        session_id: str | None = None,
        agent_id: str | None = None,
    ) -> SpectronMemory:
        """Return a new view over the same client with a narrowed scope.

        Only the values you pass are changed. Unspecified values are inherited
        from the current instance.
        """
        return SpectronMemory(
            self.client,
            user_id=user_id if user_id is not None else self.user_id,
            session_id=session_id if session_id is not None else self.session_id,
            agent_id=agent_id if agent_id is not None else self.agent_id,
        )

    def _merge(self, overrides: dict[str, Any]) -> dict[str, Any]:
        """Merge call-level keyword arguments on top of the stored scope."""
        merged = dict(self.scope)
        merged.update(overrides)
        return _prune(merged)

    async def remember(
        self,
        content: str,
        *,
        memory_type: str | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Store a new memory.

        Args:
            content: The fact, preference, or note to store.
            memory_type: Optional Spectron memory type (for example
                ``"identity"`` or ``"knowledge"``).
            metadata: Optional structured metadata to attach.
            kwargs: Extra keyword arguments forwarded to the client.
        """
        payload = self._merge({"memory_type": memory_type, "metadata": metadata, **kwargs})
        return await self.client.remember(content=content, **payload)

    async def recall(
        self,
        query: str,
        *,
        limit: int | None = None,
        **kwargs: Any,
    ) -> Any:
        """Search memory for entries relevant to a query.

        Args:
            query: Natural language query.
            limit: Optional maximum number of results.
            kwargs: Extra keyword arguments forwarded to the client.
        """
        payload = self._merge({"limit": limit, **kwargs})
        return await self.client.recall(query=query, **payload)

    async def context(self, *, query: str | None = None, **kwargs: Any) -> Any:
        """Fetch the current working set of context.

        Args:
            query: Optional query used to focus the context.
            kwargs: Extra keyword arguments forwarded to the client.
        """
        payload = self._merge({"query": query, **kwargs})
        return await self.client.context(**payload)

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
        payload = self._merge({"persist": persist, **kwargs})
        return await self.client.reflect(query=query, **payload)

    async def forget(
        self,
        target: str | None = None,
        *,
        purge: bool | None = None,
        **kwargs: Any,
    ) -> Any:
        """Delete memory.

        Args:
            target: Optional identifier or query describing what to forget.
            purge: Whether to hard-delete rather than tombstone.
            kwargs: Extra keyword arguments forwarded to the client.
        """
        payload = self._merge({"target": target, "purge": purge, **kwargs})
        return await self.client.forget(**payload)

    async def upload(self, data: Any = None, **kwargs: Any) -> Any:
        """Ingest documents, transcripts, or other artifacts.

        Args:
            data: The payload to ingest. When ``None``, pass the content through
                keyword arguments instead.
            kwargs: Extra keyword arguments forwarded to the client.
        """
        payload = self._merge(kwargs)
        if data is not None:
            payload["data"] = data
        return await self.client.upload(**payload)

    async def inspect(self, **kwargs: Any) -> Any:
        """Return diagnostic information about the memory store."""
        payload = self._merge(kwargs)
        return await self.client.inspect(**payload)


__all__ = ["SpectronMemory"]
