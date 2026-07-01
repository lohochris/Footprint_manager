"""Immutable execution policy model.

The policy is a data contract only. It does not select providers, run health
checks, execute retries, or call external systems.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionPolicy:
    """Configuration governing an AI execution attempt.

    This dataclass intentionally contains no execution logic. Normalization and
    validation belong in :class:`ExecutionPolicyBuilder`.
    """

    required_provider: str | None = None
    preferred_provider: str | None = None
    fallback_provider: str | None = None
    fallback_mode: str = "none"
    selection_strategy: str = "capability_first"
    retry_enabled: bool = False
    max_attempts: int = 1
    timeout_seconds: float | None = None
    health_required: bool = True
    diagnostics_enabled: bool = True
    dry_run: bool = False
