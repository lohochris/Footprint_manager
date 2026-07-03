"""
AI Gateway for Footprint Manager.

The gateway is the single entry point for all AI operations within the
platform.  It decouples service-layer code from specific LLM providers by:

1. Accepting provider-agnostic ``GatewayRequest`` objects.
2. Selecting the appropriate provider via the provider registry.
3. Delegating to the provider's ``complete`` method.
4. Normalising the response into a ``GatewayResponse``.

Usage::

    from backend.apps.ai.gateway import AIGateway, GatewayRequest

    gateway: AIGateway = ...  # injected or resolved from settings

    response = gateway.complete(
        GatewayRequest(prompt="Summarise this investigation.", context={})
    )
    print(response.text)
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GatewayRequest:
    """
    Provider-agnostic AI completion request.

    Attributes:
        prompt: The user-facing prompt or instruction.
        system: Optional system-level instruction.
        context: Arbitrary context data injected into the prompt template.
        provider: Explicitly requested provider name (None = use default).
        model: Explicitly requested model name (None = use provider default).
        max_tokens: Maximum tokens in the response.
        temperature: Sampling temperature (0–1).
        stream: Whether to stream the response.
        metadata: Arbitrary metadata for logging / tracing.
    """

    prompt: str
    system: str | None = None
    context: dict[str, Any] = field(default_factory=dict)
    provider: str | None = None
    model: str | None = None
    max_tokens: int = 2048
    temperature: float = 0.7
    stream: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GatewayResponse:
    """
    Normalised AI completion response.

    Attributes:
        text: Generated text content.
        provider: Name of the provider that produced the response.
        model: Model identifier used.
        prompt_tokens: Number of tokens in the prompt.
        completion_tokens: Number of tokens in the response.
        finish_reason: Reason the model stopped generating.
        metadata: Additional provider-specific response metadata.
    """

    text: str
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    finish_reason: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        """Total token consumption for this completion."""
        return self.prompt_tokens + self.completion_tokens


class AIGateway(abc.ABC):
    """
    Abstract AI gateway interface.

    Concrete implementation will resolve the active provider from settings
    and delegate appropriately.
    """

    @abc.abstractmethod
    def complete(self, request: GatewayRequest) -> GatewayResponse:
        """
        Execute an AI completion request.

        Args:
            request: Provider-agnostic completion request.

        Returns:
            Normalised ``GatewayResponse``.
        """

    @abc.abstractmethod
    def available_providers(self) -> list[str]:
        """Return the names of all registered and enabled providers."""


__all__ = [
    "GatewayRequest",
    "GatewayResponse",
    "AIGateway",
]
