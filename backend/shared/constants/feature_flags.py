"""Feature flag names and access helpers."""

from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings


@dataclass(frozen=True)
class FeatureFlag:
    """Definition of a platform feature flag."""

    name: str
    env_var: str
    description: str


ENABLE_AI = "ENABLE_AI"
ENABLE_DISCOVERY = "ENABLE_DISCOVERY"
ENABLE_GRAPH = "ENABLE_GRAPH"
ENABLE_COMPLIANCE = "ENABLE_COMPLIANCE"
ENABLE_REPORTING = "ENABLE_REPORTING"

FEATURE_FLAG_DEFINITIONS: tuple[FeatureFlag, ...] = (
    FeatureFlag(ENABLE_AI, "FEATURE_ENABLE_AI", "AI gateway and provider integration"),
    FeatureFlag(ENABLE_DISCOVERY, "FEATURE_ENABLE_DISCOVERY", "Discovery workflows"),
    FeatureFlag(ENABLE_GRAPH, "FEATURE_ENABLE_GRAPH", "Graph-backed intelligence"),
    FeatureFlag(ENABLE_COMPLIANCE, "FEATURE_ENABLE_COMPLIANCE", "Compliance workflows"),
    FeatureFlag(ENABLE_REPORTING, "FEATURE_ENABLE_REPORTING", "Reporting workflows"),
)

FEATURE_FLAG_NAMES: frozenset[str] = frozenset(flag.name for flag in FEATURE_FLAG_DEFINITIONS)


def get_feature_flags() -> dict[str, bool]:
    """Return configured platform feature flags from Django settings."""
    configured = getattr(settings, "FEATURE_FLAGS", {})
    return {name: bool(configured.get(name, False)) for name in FEATURE_FLAG_NAMES}


def is_feature_enabled(name: str) -> bool:
    """Return True when the named feature flag is enabled."""
    if name not in FEATURE_FLAG_NAMES:
        raise KeyError(f"Unknown feature flag: {name}")
    return get_feature_flags()[name]


__all__ = [
    "FeatureFlag",
    "FEATURE_FLAG_DEFINITIONS",
    "FEATURE_FLAG_NAMES",
    "ENABLE_AI",
    "ENABLE_DISCOVERY",
    "ENABLE_GRAPH",
    "ENABLE_COMPLIANCE",
    "ENABLE_REPORTING",
    "get_feature_flags",
    "is_feature_enabled",
]
