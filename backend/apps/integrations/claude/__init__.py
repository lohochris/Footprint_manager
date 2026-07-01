"""
Anthropic Claude integration interface for Footprint Manager.

Defines the ``ClaudeClient`` abstract interface for interacting with the
Anthropic Messages API.  Concrete implementation will be provided in a
future sprint once the AI feature flag is enabled.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ClaudeMessage:
    """A single message in a Claude conversation turn."""

    role: str  # "user" or "assistant"
    content: str


@dataclass(frozen=True)
class ClaudeRequest:
    """
    Request parameters for a Claude Messages API call.

    Attributes:
        messages: Conversation history.
        model: Model identifier (e.g. ``"claude-sonnet-4-5"``).
        max_tokens: Maximum tokens in the response.
        system: Optional system prompt.
        temperature: Sampling temperature between 0 and 1.
        extra: Additional Anthropic-specific parameters.
    """

    messages: list[ClaudeMessage]
    model: str = "claude-sonnet-4-5"
    max_tokens: int = 2048
    system: str | None = None
    temperature: float = 0.7
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ClaudeResponse:
    """
    Response from a Claude Messages API call.

    Attributes:
        content: Generated text content.
        model: Model that produced the response.
        input_tokens: Token count for the input.
        output_tokens: Token count for the output.
        stop_reason: Why the model stopped (``"end_turn"``, ``"max_tokens"``, etc.).
    """

    content: str
    model: str
    input_tokens: int
    output_tokens: int
    stop_reason: str


class ClaudeClient(abc.ABC):
    """Abstract Anthropic Claude API client interface."""

    @abc.abstractmethod
    def complete(self, request: ClaudeRequest) -> ClaudeResponse:
        """Execute a Messages API request."""

    @abc.abstractmethod
    def health_check(self) -> bool:
        """Return True if the Anthropic API is reachable."""


__all__ = [
    "ClaudeMessage",
    "ClaudeRequest",
    "ClaudeResponse",
    "ClaudeClient",
]
