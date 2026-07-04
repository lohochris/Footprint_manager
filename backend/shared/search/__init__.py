"""
Search backend abstraction for Footprint Manager.

Defines the ``SearchBackend`` protocol and associated data structures
(``SearchQuery``, ``SearchResult``) that all concrete search implementations
must satisfy.

Planned backends:
- PostgreSQL Full Text Search (default, Sprint 1)
- Elasticsearch (future)
- OpenSearch (future)

The abstraction ensures the service layer is decoupled from the chosen
search technology, enabling seamless backend swaps.

Usage::

    from backend.shared.search import SearchBackend, SearchQuery, SearchResult

    def search_investigations(
        backend: SearchBackend,
        q: str,
    ) -> SearchResult:
        query = SearchQuery(text=q, index="investigations", limit=25)
        return backend.search(query)
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SearchQuery:
    """
    Structured search request.

    Attributes:
        text: Free-text query string.
        index: Target index or model name.
        filters: Field-level equality filters (e.g. ``{"status": "active"}``).
        limit: Maximum number of results to return.
        offset: Number of results to skip (for offset-based pagination).
        fields: Whitelist of fields to include in the response (empty = all).
        highlight: Whether to include highlighted excerpt snippets.
        sort_by: Field name to sort results by.
        sort_dir: ``"asc"`` or ``"desc"`` (default: ``"desc"`` by relevance).
    """

    text: str
    index: str
    filters: dict[str, Any] = field(default_factory=dict)
    limit: int = 25
    offset: int = 0
    fields: list[str] = field(default_factory=list)
    highlight: bool = False
    sort_by: str | None = None
    sort_dir: str = "desc"


@dataclass(frozen=True)
class SearchHit:
    """
    A single result item from a search operation.

    Attributes:
        id: Primary key of the matched record.
        score: Relevance score assigned by the search backend.
        source: Full or partial record data.
        highlights: Highlighted field excerpts (empty if not requested).
    """

    id: str
    score: float
    source: dict[str, Any]
    highlights: dict[str, list[str]] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchResult:
    """
    Response from a search operation.

    Attributes:
        hits: Ordered list of matching documents.
        total: Total number of matching documents (before pagination).
        took_ms: Time taken by the backend to execute the query, in ms.
        query: The original query that produced this result.
    """

    hits: list[SearchHit]
    total: int
    took_ms: float
    query: SearchQuery


class SearchBackend(abc.ABC):
    """
    Abstract search backend interface.

    Concrete implementations must provide ``search`` and ``index_document``
    at minimum.  Backends that support bulk indexing should also override
    ``index_documents``.
    """

    @abc.abstractmethod
    def search(self, query: SearchQuery) -> SearchResult:
        """
        Execute *query* and return matching documents.

        Args:
            query: Structured search request.

        Returns:
            ``SearchResult`` with matching hits and metadata.
        """

    @abc.abstractmethod
    def index_document(self, index: str, document_id: str, body: dict[str, Any]) -> None:
        """
        Add or update a document in *index*.

        Args:
            index: Target index name.
            document_id: Unique document identifier.
            body: Document fields to index.
        """

    @abc.abstractmethod
    def delete_document(self, index: str, document_id: str) -> None:
        """
        Remove a document from *index*.

        Args:
            index: Target index name.
            document_id: Unique document identifier to remove.
        """

    def index_documents(self, index: str, documents: list[tuple[str, dict[str, Any]]]) -> None:
        """
        Bulk-index multiple documents.

        The default implementation calls ``index_document`` in a loop.
        Backends that support bulk operations should override this for
        efficiency.

        Args:
            index: Target index name.
            documents: List of ``(document_id, body)`` tuples.
        """
        for doc_id, body in documents:
            self.index_document(index, doc_id, body)


__all__ = [
    "SearchQuery",
    "SearchHit",
    "SearchResult",
    "SearchBackend",
]
