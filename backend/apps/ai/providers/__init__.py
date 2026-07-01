"""
AI provider protocol for Footprint Manager.

Defines the ``AIProvider`` abstract class that all concrete LLM providers
(OpenAI, Claude, local LLM) must implement.  Providers are registered in
the gateway's provider registry and selected based on feature flags and
request parameters.
"""

from __future__ import annotations

import abc

from backend.apps.ai.gateway import GatewayRequest, GatewayResponse


class AIProvider(abc.ABC):
    """
    Abstract AI provider.

    Each provider wraps a specific LLM API and translates between the
    gateway's provider-agnostic types and the provider's native SDK types.

    Attributes:
        name: Unique provider identifier (e.g. ``"openai"``, ``"claude"``).
        default_model: Model used when the request does not specify one.
    """

    name: str
    default_model: str

    @abc.abstractmethod
    def complete(self, request: GatewayRequest) -> GatewayResponse:
        """
        Execute a completion using this provider.

        Args:
            request: Gateway request (provider-specific fields are in ``context``).

        Returns:
            Normalised ``GatewayResponse``.
        """

    @abc.abstractmethod
    def is_available(self) -> bool:
        """
        Return True if this provider is configured and reachable.

        Used by the gateway to exclude unavailable providers during routing.
        """

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r}, model={self.default_model!r})"


class ProviderRegistry:
    """
    Registry mapping provider names to ``AIProvider`` instances.

    Providers are registered at application startup via ``apps.ai.apps.ready()``.
    The registry is consulted by the ``AIGateway`` when routing requests.
    """

    def __init__(self) -> None:
        self._providers: dict[str, AIProvider] = {}
        self._default: str | None = None

    def register(self, provider: AIProvider, *, default: bool = False) -> None:
        """
        Register *provider* under its ``name`` attribute.

        Args:
            provider: The provider instance to register.
            default: If True, sets this provider as the gateway default.
        """
        self._providers[provider.name] = provider
        if default or self._default is None:
            self._default = provider.name

    def get(self, name: str) -> AIProvider | None:
        """Return the provider registered under *name*, or None."""
        return self._providers.get(name)

    def get_default(self) -> AIProvider | None:
        """Return the default provider, or None if none are registered."""
        if self._default is None:
            return None
        return self._providers.get(self._default)

    def available(self) -> list[AIProvider]:
        """Return all registered providers that report themselves as available."""
        return [p for p in self._providers.values() if p.is_available()]

    def names(self) -> list[str]:
        """Return the names of all registered providers."""
        return list(self._providers.keys())


#: Global provider registry — populated during app.ready()
registry: ProviderRegistry = ProviderRegistry()

__all__ = [
    "AIProvider",
    "ProviderRegistry",
    "registry",
]
