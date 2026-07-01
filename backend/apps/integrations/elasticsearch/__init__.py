"""
Elasticsearch / OpenSearch integration interface for Footprint Manager.

Defines the ``ElasticsearchClient`` abstract interface for full-text search
and analytics operations.  This wraps the lower-level ``shared.search``
abstraction with Elasticsearch-specific capabilities (aggregations, mappings).
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class IndexMapping:
    """
    Elasticsearch index mapping definition.

    Attributes:
        index: Index name.
        mappings: Elasticsearch mappings dict.
        settings: Index settings dict (shards, replicas, analyzers).
    """

    index: str
    mappings: dict[str, Any]
    settings: dict[str, Any] = field(default_factory=dict)


class ElasticsearchClient(abc.ABC):
    """Abstract Elasticsearch / OpenSearch client interface."""

    @abc.abstractmethod
    def search(
        self,
        index: str,
        body: dict[str, Any],
        *,
        size: int = 25,
        from_: int = 0,
    ) -> dict[str, Any]:
        """
        Execute a search request against *index*.

        Args:
            index: Target index name or alias.
            body: Elasticsearch DSL query body.
            size: Number of hits to return.
            from_: Offset for pagination.

        Returns:
            Raw Elasticsearch response dictionary.
        """

    @abc.abstractmethod
    def index(self, index: str, document_id: str, body: dict[str, Any]) -> None:
        """Index a document."""

    @abc.abstractmethod
    def delete(self, index: str, document_id: str) -> None:
        """Delete a document by ID."""

    @abc.abstractmethod
    def create_index(self, mapping: IndexMapping) -> None:
        """Create an index with the given mapping and settings."""

    @abc.abstractmethod
    def delete_index(self, index: str) -> None:
        """Delete an index."""

    @abc.abstractmethod
    def health_check(self) -> bool:
        """Return True if the cluster is reachable and healthy."""


__all__ = [
    "IndexMapping",
    "ElasticsearchClient",
]
