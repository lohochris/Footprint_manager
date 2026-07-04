# backend/apps/osint/providers/noop_provider.py
"""NoOpDiscoveryProvider — deterministic offline provider for testing.

This provider mirrors the role of ``MockProvider`` in the intelligence
domain: it implements all abstract methods with predictable, side-effect-
free behaviour so that the full ``DiscoveryJobService`` execution path can
be exercised in unit tests without any external dependencies.

Behaviour
---------
- ``initialize()``      – no-op.
- ``health_check()``    – always returns healthy.
- ``capabilities()``    – declares ``person_lookup`` and ``email_lookup``.
- ``supports()``        – True for the above two capabilities.
- ``validate_target()`` – accepts any dict (no-op validation).
- ``discover()``        – returns a single deterministic raw result dict.
- ``normalize()``       – maps the raw dict to a canonical-schema dict.

The provider self-registers at import time (bottom of this module).
"""

from __future__ import annotations

from .base import BaseDiscoveryProvider
from .provider_metadata import DiscoveryHealthStatus
from .registry import register_provider

# Deterministic raw result returned by discover()
_NOOP_RAW_RESULT: dict = {
    "provider": "noop",
    "type": "profile",
    "data": {
        "name": "Jane Doe (NoOp)",
        "email": "noop@example.com",
    },
    "confidence": "1.0000",
}


class NoOpDiscoveryProvider(BaseDiscoveryProvider):
    """Deterministic offline discovery provider for unit testing.

    Parameters
    ----------
    result_count:
        Number of result dicts returned by ``discover()``.  Defaults to 1.
        Set to 0 to simulate a provider that finds nothing.
    healthy:
        Controls the return value of ``health_check()``.
        Defaults to ``True``.
    """

    name: str = "noop"
    version: str = "1.0.0"
    description: str = "Deterministic no-op provider for offline testing."
    priority: int = 9999  # lowest priority; never selected in production

    def __init__(
        self,
        result_count: int = 1,
        healthy: bool = True,
    ) -> None:
        self._result_count = result_count
        self._healthy = healthy

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

    def initialize(self) -> None:
        """No-op — nothing to initialise."""
        return

    def health_check(self) -> DiscoveryHealthStatus:
        """Return a deterministic health snapshot."""
        return DiscoveryHealthStatus(
            healthy=self._healthy,
            message=(
                "NoOp provider is healthy."
                if self._healthy
                else "NoOp provider simulated unhealthy state."
            ),
            details={"provider": self.name, "version": self.version},
        )

    # -------------------------------------------------------------------------
    # Capability contract
    # -------------------------------------------------------------------------

    def capabilities(self) -> list[str]:
        """Return a minimal capability set suitable for testing."""
        return ["person_lookup", "email_lookup"]

    def supports(self, capability: str) -> bool:
        """Return True for the two declared capabilities."""
        return capability in self.capabilities()

    # -------------------------------------------------------------------------
    # Execution contract
    # -------------------------------------------------------------------------

    def validate_target(self, input_data: dict) -> None:
        """Accept any dict without raising — no-op validation."""
        return

    def discover(self, input_data: dict) -> list[dict]:  # noqa: ARG002
        """Return ``result_count`` copies of the deterministic raw result."""
        return [_NOOP_RAW_RESULT.copy() for _ in range(self._result_count)]

    def normalize(self, raw: dict) -> dict:
        """Map the raw noop result to a minimal canonical schema."""
        return {
            "title": raw.get("data", {}).get("name", "Unknown"),
            "email": raw.get("data", {}).get("email", ""),
            "confidence": raw.get("confidence", "1.0000"),
            "source": "noop",
            "type": raw.get("type", "profile"),
        }


# Self-register in the module-level singleton registry.
register_provider(NoOpDiscoveryProvider)
