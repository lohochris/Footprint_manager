# backend/intelligence/providers/provider_metadata.py
"""Immutable metadata models for AI provider registration.

These dataclasses describe provider identity, version, capability flags,
and health state.  They contain no execution logic, no network operations,
and no abstract methods.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class ProviderCapabilities:
    """Boolean capability flags for an AI provider.

    All capabilities default to ``False``; a concrete provider declaration
    should explicitly set the flags it supports to ``True``.
    """

    supports_text: bool = False
    supports_chat: bool = False
    supports_structured_output: bool = False
    supports_streaming: bool = False
    supports_embeddings: bool = False


@dataclass(frozen=True)
class HealthStatus:
    """Immutable snapshot of a provider's health at a point in time.

    Attributes
    ----------
    healthy:
        ``True`` when the provider is considered operational.
    message:
        Human-readable description of the health state.
    timestamp:
        UTC datetime at which the snapshot was created.  Populated
        automatically via ``default_factory`` when not supplied.
    """

    healthy: bool
    message: str
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(tz=UTC)
    )


@dataclass(frozen=True)
class ProviderMetadata:
    """Immutable identity and capability description of an AI provider.

    Attributes
    ----------
    name:
        Unique machine-readable provider identifier.
    version:
        Semantic version string of the provider implementation.
    description:
        Human-readable summary of the provider's purpose.
    capabilities:
        Declared capability flags for this provider.
    """

    name: str
    version: str
    description: str
    capabilities: ProviderCapabilities
