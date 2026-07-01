"""
Neo4j graph database integration interface for Footprint Manager.

Defines the ``GraphClient`` abstract interface for Neo4j interactions.
The Footprint Manager knowledge graph (relationships between entities,
OSINT data, investigation links) will be stored in Neo4j in a future sprint.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CypherQuery:
    """
    A parameterised Cypher query.

    Attributes:
        statement: Cypher query string with ``$param`` placeholders.
        parameters: Dictionary of parameter values.
        database: Target Neo4j database (defaults to the configured default).
    """

    statement: str
    parameters: dict[str, Any] = field(default_factory=dict)
    database: str | None = None


@dataclass(frozen=True)
class GraphNode:
    """Represents a Neo4j node with labels and properties."""

    id: str
    labels: list[str]
    properties: dict[str, Any]


@dataclass(frozen=True)
class GraphRelationship:
    """Represents a Neo4j relationship between two nodes."""

    id: str
    type: str
    start_node_id: str
    end_node_id: str
    properties: dict[str, Any]


class GraphClient(abc.ABC):
    """Abstract Neo4j graph database client interface."""

    @abc.abstractmethod
    def execute(self, query: CypherQuery) -> list[dict[str, Any]]:
        """
        Execute a Cypher query and return the result rows.

        Args:
            query: The Cypher query to execute.

        Returns:
            List of result row dictionaries.
        """

    @abc.abstractmethod
    def execute_write(self, query: CypherQuery) -> list[dict[str, Any]]:
        """Execute a write transaction."""

    @abc.abstractmethod
    def health_check(self) -> bool:
        """Return True if the Neo4j instance is reachable."""

    @abc.abstractmethod
    def close(self) -> None:
        """Release the connection / driver resources."""


__all__ = [
    "CypherQuery",
    "GraphNode",
    "GraphRelationship",
    "GraphClient",
]
