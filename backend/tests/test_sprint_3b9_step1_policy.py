"""Sprint 3B.9 Step 1 - execution policy foundation tests.

All tests are deterministic and offline.
No provider selection, provider execution, network calls, or external AI clients.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import get_type_hints

import pytest
from intelligence.policies import ExecutionPolicy, ExecutionPolicyBuilder
from intelligence.providers import (
    AIProvider,
    AIRequest,
    DummyProvider,
    EchoProvider,
    HealthStatus,
    MockProvider,
)
from shared.constants.feature_flags import ENABLE_AI


def make_request(
    *,
    metadata: dict | None = None,
    options: dict | None = None,
) -> AIRequest:
    return AIRequest(
        task="text",
        execution_context=None,
        payload={"prompt": "hello"},
        metadata=metadata or {},
        options=options,
    )


def make_builder(
    *,
    defaults: dict | None = None,
    ai_enabled: bool = True,
) -> ExecutionPolicyBuilder:
    return ExecutionPolicyBuilder(
        defaults=defaults,
        feature_flags={ENABLE_AI: ai_enabled},
    )


class TestExecutionPolicy:
    def test_defaults(self) -> None:
        policy = ExecutionPolicy()
        assert policy.required_provider is None
        assert policy.preferred_provider is None
        assert policy.fallback_provider is None
        assert policy.fallback_mode == "none"
        assert policy.selection_strategy == "capability_first"
        assert policy.retry_enabled is False
        assert policy.max_attempts == 1
        assert policy.timeout_seconds is None
        assert policy.health_required is True
        assert policy.diagnostics_enabled is True
        assert policy.dry_run is False

    def test_is_immutable(self) -> None:
        policy = ExecutionPolicy()
        with pytest.raises(FrozenInstanceError):
            policy.required_provider = "echo"  # type: ignore[misc]

    def test_contains_no_execution_methods(self) -> None:
        policy = ExecutionPolicy()
        assert not hasattr(policy, "execute")
        assert not hasattr(policy, "select")
        assert not hasattr(policy, "health_check")


class TestExecutionPolicyBuilder:
    def test_builds_default_policy(self) -> None:
        policy = make_builder().build(make_request())
        assert policy == ExecutionPolicy()

    def test_metadata_provider_maps_to_required_provider(self) -> None:
        policy = make_builder().build(make_request(metadata={"provider": "dummy"}))
        assert policy.required_provider == "dummy"

    def test_required_provider_takes_precedence_over_legacy_provider(self) -> None:
        request = make_request(
            metadata={
                "provider": "dummy",
                "required_provider": "echo",
            }
        )
        policy = make_builder().build(request)
        assert policy.required_provider == "echo"

    def test_maps_preferred_and_fallback_provider(self) -> None:
        request = make_request(
            metadata={
                "preferred_provider": "echo",
                "fallback_provider": "dummy",
                "fallback_mode": "named",
            }
        )
        policy = make_builder().build(request)
        assert policy.preferred_provider == "echo"
        assert policy.fallback_provider == "dummy"
        assert policy.fallback_mode == "named"

    def test_maps_selection_strategy(self) -> None:
        request = make_request(metadata={"selection_strategy": "preferred_then_capable"})
        policy = make_builder().build(request)
        assert policy.selection_strategy == "preferred_then_capable"

    def test_retry_is_architecture_only_and_disabled_by_default(self) -> None:
        policy = make_builder().build(make_request())
        assert policy.retry_enabled is False
        assert policy.max_attempts == 1

    def test_retry_disabled_forces_single_attempt(self) -> None:
        request = make_request(metadata={"retry_enabled": False, "max_attempts": 5})
        policy = make_builder().build(request)
        assert policy.retry_enabled is False
        assert policy.max_attempts == 1

    def test_retry_enabled_allows_attempt_count(self) -> None:
        request = make_request(metadata={"retry_enabled": True, "max_attempts": 3})
        policy = make_builder().build(request)
        assert policy.retry_enabled is True
        assert policy.max_attempts == 3

    def test_timeout_is_normalized_to_float(self) -> None:
        request = make_request(metadata={"timeout_seconds": "2.5"})
        policy = make_builder().build(request)
        assert policy.timeout_seconds == 2.5

    def test_invalid_timeout_raises_value_error(self) -> None:
        request = make_request(metadata={"timeout_seconds": 0})
        with pytest.raises(ValueError, match="timeout_seconds"):
            make_builder().build(request)

    def test_invalid_max_attempts_raises_value_error(self) -> None:
        request = make_request(metadata={"retry_enabled": True, "max_attempts": 0})
        with pytest.raises(ValueError, match="max_attempts"):
            make_builder().build(request)

    def test_invalid_fallback_mode_raises_value_error(self) -> None:
        request = make_request(metadata={"fallback_mode": "surprise"})
        with pytest.raises(ValueError, match="fallback_mode"):
            make_builder().build(request)

    def test_invalid_selection_strategy_raises_value_error(self) -> None:
        request = make_request(metadata={"selection_strategy": "random"})
        with pytest.raises(ValueError, match="selection_strategy"):
            make_builder().build(request)

    def test_options_are_supported(self) -> None:
        request = make_request(options={"preferred_provider": "mock"})
        policy = make_builder().build(request)
        assert policy.preferred_provider == "mock"

    def test_metadata_overrides_options(self) -> None:
        request = make_request(
            metadata={"preferred_provider": "echo"},
            options={"preferred_provider": "mock"},
        )
        policy = make_builder().build(request)
        assert policy.preferred_provider == "echo"

    def test_defaults_are_supported(self) -> None:
        policy = make_builder(defaults={"fallback_mode": "capability"}).build(
            make_request()
        )
        assert policy.fallback_mode == "capability"

    def test_explicit_dry_run_argument_overrides_request_value(self) -> None:
        request = make_request(metadata={"dry_run": False})
        policy = make_builder().build(request, dry_run=True)
        assert policy.dry_run is True

    def test_diagnostics_can_be_disabled(self) -> None:
        request = make_request(metadata={"diagnostics_enabled": False})
        policy = make_builder().build(request)
        assert policy.diagnostics_enabled is False

    def test_ai_disabled_disables_health_required(self) -> None:
        policy = make_builder(ai_enabled=False).build(make_request())
        assert policy.health_required is False

    def test_builder_does_not_mutate_request_metadata(self) -> None:
        metadata = {"provider": "dummy"}
        request = make_request(metadata=metadata)
        make_builder().build(request)
        assert metadata == {"provider": "dummy"}


class TestHealthContract:
    def test_ai_provider_health_check_contract_returns_health_status(self) -> None:
        hints = get_type_hints(AIProvider.health_check)
        assert hints["return"] is HealthStatus

    @pytest.mark.parametrize(
        "provider",
        [
            DummyProvider(),
            EchoProvider(),
            MockProvider(),
        ],
    )
    def test_offline_providers_return_health_status(self, provider: AIProvider) -> None:
        assert isinstance(provider.health_check(), HealthStatus)

    @pytest.mark.parametrize(
        "provider",
        [
            DummyProvider(),
            EchoProvider(),
            MockProvider(),
        ],
    )
    def test_offline_provider_health_behavior_is_unchanged(
        self,
        provider: AIProvider,
    ) -> None:
        status = provider.health_check()
        assert status.healthy is True
        assert status.message
