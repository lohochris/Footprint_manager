# backend/tests/test_sprint_3b8_engine.py
"""Sprint 3B.8 — AIExecutionEngine unit tests.

All tests are deterministic and offline.
No Django DB, no network calls, no randomness.
"""

import pytest
from backend.apps.common.pipeline.core import ExecutionResult
from backend.intelligence.engine import AIExecutionEngine
from backend.intelligence.providers import (
    AIRequest,
    AIResponse,
    DummyProvider,
    MockProvider,
    MockScenario,
    ProviderRegistry,
)
from backend.intelligence.router import Router

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_request(
    task: str = "text",
    metadata: dict | None = None,
    payload: dict | None = None,
) -> AIRequest:
    return AIRequest(
        task=task,
        execution_context=None,
        payload=payload or {},
        metadata=metadata or {},
    )


def make_engine(
    *,
    registry: ProviderRegistry | None = None,
    router: Router | None = None,
) -> AIExecutionEngine:
    """Return an engine backed by an isolated registry with DummyProvider."""
    if router is not None:
        return AIExecutionEngine(router=router)
    reg = registry or ProviderRegistry()
    if registry is None:
        reg.register(DummyProvider)
    return AIExecutionEngine(router=Router(registry=reg))


@pytest.fixture()
def ai_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch is_feature_enabled so ENABLE_AI returns True."""
    monkeypatch.setattr(
        "backend.intelligence.engine.is_feature_enabled",
        lambda flag: True,
    )


@pytest.fixture()
def ai_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch is_feature_enabled so ENABLE_AI returns False."""
    monkeypatch.setattr(
        "backend.intelligence.engine.is_feature_enabled",
        lambda flag: False,
    )


# ===========================================================================
# Construction
# ===========================================================================


class TestEngineConstruction:
    def test_default_router_is_created(self) -> None:
        engine = AIExecutionEngine()
        assert isinstance(engine._router, Router)

    def test_custom_router_is_stored(self) -> None:
        reg = ProviderRegistry()
        router = Router(registry=reg)
        engine = AIExecutionEngine(router=router)
        assert engine._router is router

    def test_none_router_creates_default(self) -> None:
        engine = AIExecutionEngine(router=None)
        assert isinstance(engine._router, Router)


# ===========================================================================
# ENABLE_AI=False gate
# ===========================================================================


class TestFeatureFlagGate:
    def test_returns_failure_when_ai_disabled(self, ai_disabled: None) -> None:
        engine = make_engine()
        result = engine.execute(make_request())
        assert result.success is False

    def test_status_code_503_when_disabled(self, ai_disabled: None) -> None:
        engine = make_engine()
        result = engine.execute(make_request())
        assert result.status_code == 503

    def test_error_message_mentions_enable_ai(self, ai_disabled: None) -> None:
        engine = make_engine()
        result = engine.execute(make_request())
        assert "ENABLE_AI" in str(result.error)

    def test_metadata_marks_ai_not_enabled(self, ai_disabled: None) -> None:
        engine = make_engine()
        result = engine.execute(make_request())
        assert result.metadata.get("ai_enabled") is False

    def test_disabled_flag_takes_precedence_over_dry_run(self, ai_disabled: None) -> None:
        engine = make_engine()
        result = engine.execute(make_request(), dry_run=True)
        assert result.success is False
        assert result.status_code == 503


# ===========================================================================
# Dry-run mode
# ===========================================================================


class TestDryRun:
    def test_dry_run_returns_success(self, ai_enabled: None) -> None:
        engine = make_engine()
        result = engine.execute(make_request(), dry_run=True)
        assert result.success is True

    def test_dry_run_data_is_none(self, ai_enabled: None) -> None:
        engine = make_engine()
        result = engine.execute(make_request(task="text"), dry_run=True)
        assert result.data is None

    def test_dry_run_metadata_contains_flag(self, ai_enabled: None) -> None:
        engine = make_engine()
        result = engine.execute(make_request(), dry_run=True)
        assert result.metadata.get("dry_run") is True

    def test_dry_run_metadata_contains_task(self, ai_enabled: None) -> None:
        engine = make_engine()
        result = engine.execute(make_request(task="chat"), dry_run=True)
        assert result.metadata.get("task") == "chat"

    def test_dry_run_status_code_200(self, ai_enabled: None) -> None:
        engine = make_engine()
        result = engine.execute(make_request(), dry_run=True)
        assert result.status_code == 200

    def test_dry_run_skips_provider(self, ai_enabled: None) -> None:
        """An empty registry would raise — but dry_run never reaches selection."""
        empty_reg = ProviderRegistry()
        engine = AIExecutionEngine(router=Router(registry=empty_reg))
        result = engine.execute(make_request(), dry_run=True)
        assert result.success is True


# ===========================================================================
# Successful execution
# ===========================================================================


class TestSuccessfulExecution:
    def test_returns_execution_result(self, ai_enabled: None) -> None:
        engine = make_engine()
        result = engine.execute(make_request())
        assert isinstance(result, ExecutionResult)

    def test_success_is_true(self, ai_enabled: None) -> None:
        engine = make_engine()
        result = engine.execute(make_request())
        assert result.success is True

    def test_data_is_ai_response(self, ai_enabled: None) -> None:
        engine = make_engine()
        result = engine.execute(make_request())
        assert isinstance(result.data, AIResponse)

    def test_data_status_is_success(self, ai_enabled: None) -> None:
        engine = make_engine()
        result = engine.execute(make_request())
        assert result.data.status == "success"

    def test_status_code_200(self, ai_enabled: None) -> None:
        engine = make_engine()
        result = engine.execute(make_request())
        assert result.status_code == 200

    def test_metadata_contains_provider(self, ai_enabled: None) -> None:
        engine = make_engine()
        result = engine.execute(make_request())
        assert "provider" in result.metadata
        assert result.metadata["provider"] == "dummy"

    def test_metadata_contains_task(self, ai_enabled: None) -> None:
        engine = make_engine()
        result = engine.execute(make_request(task="text"))
        assert result.metadata["task"] == "text"

    def test_execution_time_is_non_negative(self, ai_enabled: None) -> None:
        engine = make_engine()
        result = engine.execute(make_request())
        assert result.execution_time >= 0.0

    def test_error_is_none_on_success(self, ai_enabled: None) -> None:
        engine = make_engine()
        result = engine.execute(make_request())
        assert result.error is None


# ===========================================================================
# Provider failure scenarios (via MockProvider response contract)
# ===========================================================================


class TestProviderFailureResponse:
    def _mock_engine(self, scenario: MockScenario) -> AIExecutionEngine:
        reg = ProviderRegistry()
        reg.register(MockProvider)

        class _FixedMockRouter(Router):
            def select(self, request: AIRequest) -> type:  # noqa: ANN001
                return MockProvider

        engine = AIExecutionEngine(router=_FixedMockRouter(registry=reg))
        original_execute = engine.execute

        def patched_execute(
            req: AIRequest, *, dry_run: bool = False
        ) -> ExecutionResult:
            # Directly construct engine with scenario-aware router
            reg2 = ProviderRegistry()

            class _ScenarioCls(MockProvider):
                def execute(self, r: AIRequest) -> AIResponse:
                    return MockProvider(scenario).execute(r)
                name: str = "mock"

            reg2.register(_ScenarioCls)
            e = AIExecutionEngine(router=Router(registry=reg2))
            return original_execute.__func__(e, req, dry_run=dry_run)

        return engine

    def test_failure_scenario_returns_success_false(self, ai_enabled: None) -> None:
        reg = ProviderRegistry()
        reg.register(MockProvider)
        # Use a subclass to force FAILURE scenario
        class _FailureMock(MockProvider):
            name: str = "failmock"
            def execute(self, r: AIRequest) -> AIResponse:  # noqa: ANN001
                return MockProvider(MockScenario.FAILURE).execute(r)

        reg2 = ProviderRegistry()
        reg2.register(_FailureMock)
        req2 = make_request(task="text", metadata={"provider": "failmock"})
        engine = AIExecutionEngine(router=Router(registry=reg2))
        result = engine.execute(req2)
        assert result.success is False

    def test_failure_scenario_status_code_502(self, ai_enabled: None) -> None:
        reg = ProviderRegistry()

        class _FailureMock(MockProvider):
            name: str = "failmock"
            def execute(self, r: AIRequest) -> AIResponse:  # noqa: ANN001
                return MockProvider(MockScenario.FAILURE).execute(r)

        reg.register(_FailureMock)
        engine = AIExecutionEngine(router=Router(registry=reg))
        result = engine.execute(make_request(task="text"))
        assert result.status_code == 502


# ===========================================================================
# Provider selection failure
# ===========================================================================


class TestSelectionFailure:
    def test_empty_registry_returns_failure(self, ai_enabled: None) -> None:
        reg = ProviderRegistry()
        engine = AIExecutionEngine(router=Router(registry=reg))
        result = engine.execute(make_request())
        assert result.success is False

    def test_empty_registry_status_503(self, ai_enabled: None) -> None:
        reg = ProviderRegistry()
        engine = AIExecutionEngine(router=Router(registry=reg))
        result = engine.execute(make_request())
        assert result.status_code == 503

    def test_unknown_explicit_provider_returns_failure(self, ai_enabled: None) -> None:
        engine = make_engine()
        req = make_request(metadata={"provider": "does_not_exist"})
        result = engine.execute(req)
        assert result.success is False

    def test_selection_failure_never_raises(self, ai_enabled: None) -> None:
        reg = ProviderRegistry()
        engine = AIExecutionEngine(router=Router(registry=reg))
        # Must not raise — must return ExecutionResult
        result = engine.execute(make_request())
        assert isinstance(result, ExecutionResult)


# ===========================================================================
# Provider exception handling (crash inside execute())
# ===========================================================================


class TestProviderExceptionHandling:
    def test_crashing_provider_returns_failure(self, ai_enabled: None) -> None:
        class _CrashProvider(DummyProvider):
            name: str = "crash"
            def execute(self, r: AIRequest) -> AIResponse:  # noqa: ANN001
                raise RuntimeError("simulated crash")

        reg = ProviderRegistry()
        reg.register(_CrashProvider)
        engine = AIExecutionEngine(router=Router(registry=reg))
        result = engine.execute(make_request())
        assert result.success is False

    def test_crashing_provider_never_raises(self, ai_enabled: None) -> None:
        class _CrashProvider(DummyProvider):
            name: str = "crash2"
            def execute(self, r: AIRequest) -> AIResponse:  # noqa: ANN001
                raise ValueError("kaboom")

        reg = ProviderRegistry()
        reg.register(_CrashProvider)
        engine = AIExecutionEngine(router=Router(registry=reg))
        # Must not raise
        result = engine.execute(make_request())
        assert isinstance(result, ExecutionResult)

    def test_crashing_provider_status_500(self, ai_enabled: None) -> None:
        class _CrashProvider(DummyProvider):
            name: str = "crash3"
            def execute(self, r: AIRequest) -> AIResponse:  # noqa: ANN001
                raise Exception("generic crash")

        reg = ProviderRegistry()
        reg.register(_CrashProvider)
        engine = AIExecutionEngine(router=Router(registry=reg))
        result = engine.execute(make_request())
        assert result.status_code == 500

    def test_crashing_provider_error_is_captured(self, ai_enabled: None) -> None:
        class _CrashProvider(DummyProvider):
            name: str = "crash4"
            def execute(self, r: AIRequest) -> AIResponse:  # noqa: ANN001
                raise RuntimeError("captured")

        reg = ProviderRegistry()
        reg.register(_CrashProvider)
        engine = AIExecutionEngine(router=Router(registry=reg))
        result = engine.execute(make_request())
        assert isinstance(result.error, RuntimeError)
        assert "captured" in str(result.error)


# ===========================================================================
# Immutability preservation
# ===========================================================================


class TestImmutability:
    def test_request_is_not_mutated(self, ai_enabled: None) -> None:
        req = make_request(task="text", payload={"prompt": "hello"})
        engine = make_engine()
        engine.execute(req)
        # Frozen dataclass — any mutation attempt would have raised FrozenInstanceError
        assert req.task == "text"
        assert req.payload == {"prompt": "hello"}

    def test_result_data_is_frozen_ai_response(self, ai_enabled: None) -> None:
        from dataclasses import FrozenInstanceError
        engine = make_engine()
        result = engine.execute(make_request())
        response = result.data
        with pytest.raises(FrozenInstanceError):
            response.status = "changed"  # type: ignore[misc]


# ===========================================================================
# Determinism
# ===========================================================================


class TestDeterminism:
    def test_same_request_produces_same_outcome(self, ai_enabled: None) -> None:
        engine = make_engine()
        req = make_request()
        r1 = engine.execute(req)
        r2 = engine.execute(req)
        assert r1.success == r2.success
        assert r1.status_code == r2.status_code
        assert r1.data == r2.data

    def test_dry_run_is_deterministic(self, ai_enabled: None) -> None:
        engine = make_engine()
        req = make_request(task="structured_output")
        r1 = engine.execute(req, dry_run=True)
        r2 = engine.execute(req, dry_run=True)
        assert r1.success == r2.success
        assert r1.metadata == r2.metadata
