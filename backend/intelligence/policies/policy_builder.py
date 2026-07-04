"""Deterministic execution policy builder.

The builder normalizes request metadata/options into an immutable
``ExecutionPolicy``. It performs no provider selection, provider execution,
health checks, network operations, retries, or fallback execution.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from backend.intelligence.policies.execution_policy import ExecutionPolicy
from backend.intelligence.providers.request import AIRequest
from backend.shared.constants.feature_flags import ENABLE_AI, get_feature_flags


class ExecutionPolicyBuilder:
    """Build :class:`ExecutionPolicy` instances from request-local inputs."""

    _VALID_FALLBACK_MODES = frozenset(
        {"none", "named", "capability", "default_if_capable"}
    )
    _VALID_SELECTION_STRATEGIES = frozenset(
        {
            "required_only",
            "preferred_then_capable",
            "capability_first",
            "priority_first",
            "health_first",
        }
    )

    def __init__(
        self,
        *,
        defaults: Mapping[str, Any] | None = None,
        feature_flags: Mapping[str, bool] | None = None,
    ) -> None:
        """Create a policy builder.

        Args:
            defaults: Optional default policy values. Useful for tests or local
                configuration adapters.
            feature_flags: Optional feature flag snapshot. When omitted, the
                local settings-backed feature flag helper is read.
        """
        self._defaults = dict(defaults or {})
        self._feature_flags = (
            dict(feature_flags) if feature_flags is not None else get_feature_flags()
        )

    def build(self, request: AIRequest, *, dry_run: bool | None = None) -> ExecutionPolicy:
        """Return an immutable policy for *request*.

        Request metadata and options are copied before inspection so the builder
        never mutates caller-owned mappings.
        """
        metadata = dict(request.metadata or {})
        options = dict(request.options or {})
        values: dict[str, Any] = {
            "required_provider": None,
            "preferred_provider": None,
            "fallback_provider": None,
            "fallback_mode": "none",
            "selection_strategy": "capability_first",
            "retry_enabled": False,
            "max_attempts": 1,
            "timeout_seconds": None,
            "health_required": True,
            "diagnostics_enabled": True,
            "dry_run": False,
        }

        values.update(self._defaults)
        values.update(self._extract_policy_values(options))
        values.update(self._extract_policy_values(metadata))

        if values.get("required_provider") is None and metadata.get("provider"):
            values["required_provider"] = metadata["provider"]

        if dry_run is not None:
            values["dry_run"] = dry_run

        if not self._feature_flags.get(ENABLE_AI, False):
            values["health_required"] = False

        values["fallback_mode"] = self._validate_choice(
            "fallback_mode",
            values["fallback_mode"],
            self._VALID_FALLBACK_MODES,
        )
        values["selection_strategy"] = self._validate_choice(
            "selection_strategy",
            values["selection_strategy"],
            self._VALID_SELECTION_STRATEGIES,
        )
        values["max_attempts"] = self._normalize_max_attempts(values["max_attempts"])
        values["retry_enabled"] = bool(values["retry_enabled"])
        if not values["retry_enabled"]:
            values["max_attempts"] = 1
        values["timeout_seconds"] = self._normalize_timeout(values["timeout_seconds"])
        values["health_required"] = bool(values["health_required"])
        values["diagnostics_enabled"] = bool(values["diagnostics_enabled"])
        values["dry_run"] = bool(values["dry_run"])

        return ExecutionPolicy(**values)

    def _extract_policy_values(self, source: Mapping[str, Any]) -> dict[str, Any]:
        """Return recognized policy values from *source*."""
        recognized = {
            "required_provider",
            "preferred_provider",
            "fallback_provider",
            "fallback_mode",
            "selection_strategy",
            "retry_enabled",
            "max_attempts",
            "timeout_seconds",
            "health_required",
            "diagnostics_enabled",
            "dry_run",
        }
        return {key: source[key] for key in recognized if key in source}

    def _validate_choice(
        self,
        field_name: str,
        value: object,
        valid_values: frozenset[str],
    ) -> str:
        """Normalize a string choice and raise ``ValueError`` when invalid."""
        normalized = str(value).strip()
        if normalized not in valid_values:
            allowed = ", ".join(sorted(valid_values))
            raise ValueError(
                f"Invalid {field_name} '{value}'. Expected one of: {allowed}."
            )
        return normalized

    def _normalize_max_attempts(self, value: object) -> int:
        """Return a positive integer attempt count."""
        if not isinstance(value, int | str | bytes | bytearray):
            raise ValueError("max_attempts must be an integer.")
        attempts = int(value)
        if attempts < 1:
            raise ValueError("max_attempts must be greater than or equal to 1.")
        return attempts

    def _normalize_timeout(self, value: object) -> float | None:
        """Return a positive timeout value or ``None``."""
        if value is None:
            return None
        if not isinstance(value, int | float | str | bytes | bytearray):
            raise ValueError("timeout_seconds must be a number when set.")
        timeout = float(value)
        if timeout <= 0:
            raise ValueError("timeout_seconds must be greater than 0 when set.")
        return timeout
