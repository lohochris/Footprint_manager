"""
Retrieval-Augmented Generation (RAG) pipeline interface for Footprint Manager.

Defines the ``RAGPipeline`` abstract interface for context retrieval and
augmented prompt construction.  Concrete implementations will combine the
search backend (``shared.search``) with the embedding backend
(``apps.ai.embeddings``) to retrieve relevant context chunks for LLM queries.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RetrievedChunk:
    """
    A document chunk retrieved by the RAG pipeline.

    Attributes:
        id: Unique identifier of the source document or chunk.
        content: Text content of the chunk.
        score: Relevance score (higher is more relevant).
        source: Origin metadata (document title, URL, entity ID, etc.).
        metadata: Additional provider-specific metadata.
    """

    id: str
    content: str
    score: float
    source: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGRequest:
    """
    Request for context retrieval to augment an LLM prompt.

    Attributes:
        query: Natural-language query to find relevant context for.
        index: Search index or collection to retrieve from.
        top_k: Maximum number of chunks to retrieve.
        min_score: Minimum relevance score threshold (0–1).
        filters: Metadata filters applied during retrieval.
    """

    query: str
    index: str
    top_k: int = 5
    min_score: float = 0.0
    filters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RAGResult:
    """
    Result of a RAG retrieval operation.

    Attributes:
        chunks: Retrieved and ranked document chunks.
        context: Pre-formatted context string ready for prompt injection.
        total_retrieved: Total chunks considered before filtering.
    """

    chunks: list[RetrievedChunk]
    context: str
    total_retrieved: int


class RAGPipeline(abc.ABC):
    """
    Abstract RAG pipeline interface.

    Implementations combine embedding-based similarity search with optional
    reranking to retrieve the most relevant context chunks for a query.
    """

    @abc.abstractmethod
    def retrieve(self, request: RAGRequest) -> RAGResult:
        """
        Retrieve relevant chunks for *request*.

        Args:
            request: RAG retrieval parameters.

        Returns:
            ``RAGResult`` containing ranked chunks and formatted context.
        """

    @abc.abstractmethod
    def index_document(
        self,
        index: str,
        document_id: str,
        content: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Embed and index a document for future retrieval.

        Args:
            index: Target index name.
            document_id: Unique document identifier.
            content: Raw text content to embed and store.
            metadata: Optional metadata attached to the document.
        """

    @abc.abstractmethod
    def delete_document(self, index: str, document_id: str) -> None:
        """Remove a document from the retrieval index."""


__all__ = [
    "RetrievedChunk",
    "RAGRequest",
    "RAGResult",
    "RAGPipeline",
]
