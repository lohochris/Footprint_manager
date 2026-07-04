# backend/apps/osint/providers/__init__.py
"""OSINT provider interface package.

Public surface:
    BaseDiscoveryProvider       – ABC defining the seven-method contract.
    DiscoveryHealthStatus       – Frozen dataclass for health snapshots.
    DiscoveryProviderRegistry   – Class registry with priority ordering.
    register_provider           – Free-function for module-level registration.
    get_provider                – Singleton registry lookup.
    list_providers              – All registered providers in priority order.
    default_provider            – First provider in priority order.
    NoOpDiscoveryProvider       – Offline deterministic test provider.
"""

from .base import BaseDiscoveryProvider
from .noop_provider import NoOpDiscoveryProvider
from .provider_metadata import DiscoveryHealthStatus
from .registry import (
    DiscoveryProviderRegistry,
    default_provider,
    get_provider,
    list_providers,
    register_provider,
    unregister_provider,
)

__all__ = [
    "BaseDiscoveryProvider",
    "DiscoveryHealthStatus",
    "DiscoveryProviderRegistry",
    "NoOpDiscoveryProvider",
    "default_provider",
    "get_provider",
    "list_providers",
    "register_provider",
    "unregister_provider",
]
