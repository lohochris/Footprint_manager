# backend/apps/osint/providers/registry.py
"""Registry for OSINT discovery provider classes.

This registry mirrors the design of
``backend.intelligence.providers.registry.ProviderRegistry`` precisely:

- Class-based registration (not instance-based).
- Deterministic ordering by ``priority`` attribute (ascending).
- ``ValueError`` on duplicate registration.
- Module-level singleton plus free-function wrappers for easy import.

No side-effects or automatic registration occur; providers must call
``register_provider()`` explicitly (typically at the bottom of their
own module, matching the pattern used in ``mock_provider.py``).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Type

from .base import BaseDiscoveryProvider


class DiscoveryProviderRegistry:
    """Singleton-style container for OSINT discovery provider classes.

    All mutation methods raise ``ValueError`` on duplicate registration
    to enforce uniqueness at startup.
    """

    def __init__(self) -> None:
        self._providers: Dict[str, Type[BaseDiscoveryProvider]] = {}

    # -------------------------------------------------------------------------
    # Registration API
    # -------------------------------------------------------------------------

    def register(self, provider: Type[BaseDiscoveryProvider]) -> None:
        """Register a discovery provider class.

        The provider's unique name is taken from its ``name`` class
        attribute.  Duplicate names raise ``ValueError``.

        Parameters
        ----------
        provider:
            A subclass of ``BaseDiscoveryProvider`` with a non-empty
            ``name`` class attribute.

        Raises
        ------
        ValueError:
            If ``provider.name`` is already registered or is empty.
        """
        name = getattr(provider, "name", "")
        if not name:
            raise ValueError(
                f"Provider class '{provider.__name__}' must define a non-empty 'name' class attribute."
            )
        if name in self._providers:
            raise ValueError(
                f"Discovery provider '{name}' is already registered."
            )
        self._providers[name] = provider

    def unregister(self, name: str) -> None:
        """Remove a provider from the registry if present (no-op if absent)."""
        self._providers.pop(name, None)

    # -------------------------------------------------------------------------
    # Lookup API
    # -------------------------------------------------------------------------

    def get(self, name: str) -> Optional[Type[BaseDiscoveryProvider]]:
        """Return the provider class for *name* or ``None`` if unknown."""
        return self._providers.get(name)

    def list(self) -> List[Type[BaseDiscoveryProvider]]:
        """Return all registered providers ordered by ``priority``.

        Providers without a ``priority`` attribute are treated as priority 0.
        Lower priority values rank first (i.e. higher priority).
        """
        return sorted(
            self._providers.values(),
            key=lambda p: getattr(p, "priority", 0),
        )

    def default(self) -> Optional[Type[BaseDiscoveryProvider]]:
        """Return the first provider in priority order, or ``None`` if empty."""
        providers = self.list()
        return providers[0] if providers else None

    def capabilities(self, name: str) -> List[str]:
        """Return the capability list for the named provider.

        Instantiates the provider class temporarily; implementations are
        expected to be side-effect-free in ``capabilities()``.

        Raises
        ------
        KeyError:
            If ``name`` is not registered.
        """
        provider_cls = self.get(name)
        if provider_cls is None:
            raise KeyError(f"Discovery provider '{name}' not found in registry.")
        return provider_cls().capabilities()

    def __len__(self) -> int:
        return len(self._providers)


# ---------------------------------------------------------------------------
# Module-level singleton and free-function wrappers
# ---------------------------------------------------------------------------

_registry = DiscoveryProviderRegistry()


def register_provider(provider: Type[BaseDiscoveryProvider]) -> None:
    """Register a provider class in the module-level singleton registry."""
    _registry.register(provider)


def unregister_provider(name: str) -> None:
    """Remove a provider from the module-level singleton registry."""
    _registry.unregister(name)


def get_provider(name: str) -> Optional[Type[BaseDiscoveryProvider]]:
    """Return the provider class for *name* from the singleton registry."""
    return _registry.get(name)


def list_providers() -> List[Type[BaseDiscoveryProvider]]:
    """Return all registered providers ordered by priority."""
    return _registry.list()


def default_provider() -> Optional[Type[BaseDiscoveryProvider]]:
    """Return the highest-priority provider, or ``None`` if none registered."""
    return _registry.default()
