# backend/intelligence/providers/registry.py
"""Registry for AI provider classes.

The registry holds mapping from a provider's unique name to its class. It
provides deterministic ordering based on an optional ``priority`` attribute
(ascending – lower value means higher priority). No side‑effects or automatic
registration occur; the application must call ``register_provider`` explicitly.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Type

from .base import AIProvider


class ProviderRegistry:
    """Singleton‑style container for AI provider classes.

    The class itself is lightweight; a module‑level instance ``_registry`` is
    created for convenience. All mutation methods raise ``ValueError`` on
    duplicate registration to enforce uniqueness.
    """

    def __init__(self) -> None:
        self._providers: Dict[str, Type[AIProvider]] = {}

    # ---------------------------------------------------------------------
    # Registration API
    # ---------------------------------------------------------------------
    def register(self, provider: Type[AIProvider]) -> None:
        """Register a provider class.

        The provider's unique name is taken from a ``name`` attribute if it
        exists; otherwise the class name is used. Duplicate names raise a
        ``ValueError``.
        """
        name = getattr(provider, "name", provider.__name__)
        if name in self._providers:
            raise ValueError(f"Provider '{name}' is already registered.")
        self._providers[name] = provider

    def unregister(self, name: str) -> None:
        """Remove a provider from the registry if present."""
        self._providers.pop(name, None)

    # ---------------------------------------------------------------------
    # Lookup API
    # ---------------------------------------------------------------------
    def get(self, name: str) -> Optional[Type[AIProvider]]:
        """Return the provider class for *name* or ``None`` if unknown."""
        return self._providers.get(name)

    def list(self) -> List[Type[AIProvider]]:
        """Return all registered providers ordered by ``priority``.

        Providers without a ``priority`` attribute are treated as priority ``0``.
        """
        return sorted(
            self._providers.values(),
            key=lambda p: getattr(p, "priority", 0),
        )

    def default(self) -> Optional[Type[AIProvider]]:
        """Return the first provider in the ordered list or ``None`` if empty."""
        providers = self.list()
        return providers[0] if providers else None

    def capabilities(self, name: str) -> List[str]:
        """Return the capability list for the named provider.

        Raises ``KeyError`` if the provider is not registered.
        """
        provider_cls = self.get(name)
        if provider_cls is None:
            raise KeyError(f"Provider '{name}' not found.")
        # Instantiate temporarily to call ``capabilities`` – implementations are
        # expected to be side‑effect free.
        return provider_cls().capabilities()


# Module‑level singleton for easy import
_registry = ProviderRegistry()


def register_provider(provider: Type[AIProvider]) -> None:
    """Convenient wrapper around the singleton registry's ``register`` method."""
    _registry.register(provider)


def unregister_provider(name: str) -> None:
    _registry.unregister(name)


def get_provider(name: str) -> Optional[Type[AIProvider]]:
    return _registry.get(name)


def list_providers() -> List[Type[AIProvider]]:
    return _registry.list()


def default_provider() -> Optional[Type[AIProvider]]:
    return _registry.default()
