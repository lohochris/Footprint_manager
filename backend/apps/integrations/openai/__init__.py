"""
OpenAI integration interface for Footprint Manager.

Defines the ``OpenAIClient`` abstract interface for interacting with the
OpenAI API.  Concrete implementation will be provided in a future sprint
once the AI feature flag is enabled.

This abstraction ensures the service layer is not directly coupled to the
``openai`` SDK, enabling provider swaps and test mocking.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CompletionRequest:
    """
    Request parameters for a chat completion call.

    Attributes:
        messages: Chat history in ``[{"role": ..., "content": ...}]`` format.
        model: Model identifier (e.g. ``"gpt-4o"``).
        temperature: Sampling temperature between 0 and 2.
        max_tokens: Maximum tokens in the generated response.
        stream: Whether to stream the response.
        extra: Additional provider-specific parameters.
    """

    messages: list[dict[str, str]]
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 2048
    stream: bool = False
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CompletionResponse:
    """
    Response from a chat completion call.

    Attributes:
        content: Generated text content.
        model: Model that produced the response.
        prompt_tokens: Token count for the input.
        completion_tokens: Token count for the output.
        finish_reason: Why the model stopped (``"stop"``, ``"length"``, etc.).
    """

    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    finish_reason: str


@dataclass(frozen=True)
class EmbeddingRequest:
    """Request parameters for an embedding call."""

    input: list[str]
    model: str = "text-embedding-3-small"


@dataclass(frozen=True)
class EmbeddingResponse:
    """Response from an embedding call."""

    embeddings: list[list[float]]
    model: str
    total_tokens: int


class OpenAIClient(abc.ABC):
    """Abstract OpenAI API client interface."""

    @abc.abstractmethod
    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Execute a chat completion request."""

    @abc.abstractmethod
    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate embeddings for the provided input texts."""

    @abc.abstractmethod
    def health_check(self) -> bool:
        """Return True if the OpenAI API is reachable."""


__all__ = [
    "CompletionRequest",
    "CompletionResponse",
    "EmbeddingRequest",
    "EmbeddingResponse",
    "OpenAIClient",
]
