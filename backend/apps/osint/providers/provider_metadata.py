# backend/apps/osint/providers/provider_metadata.py
"""Immutable metadata models for OSINT provider registration.

This module mirrors ``backend.intelligence.providers.provider_metadata``
exactly in spirit.  It defines the health snapshot dataclass used by the
``BaseDiscoveryProvider`` contract.

No execution logic, no network operations, no abstract methods.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class DiscoveryHealthStatus:
    """Immutable snapshot of a discovery provider's health at a point in time.

    Attributes
    ----------
    healthy:
        ``True`` when the provider is considered operational.
    message:
        Human-readable description of the current health state.
    timestamp:
        UTC datetime at which the snapshot was created.  Populated
        automatically via ``default_factory`` when not supplied.
    details:
        Optional key-value bag for provider-specific diagnostics
        (e.g. rate-limit remaining, upstream latency).
    """

    healthy: bool
    message: str
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(tz=UTC)
    )
    details: dict = field(default_factory=dict)


__all__ = ["DiscoveryHealthStatus"]
