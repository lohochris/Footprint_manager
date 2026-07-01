# backend/tests/test_sprint_3b8_stage.py
"""Sprint 3B.8 — IntelligenceStage unit tests.

All tests are deterministic and offline.
No Django DB, no network calls, no randomness.
"""

import pytest
from apps.common.pipeline.core import ExecutionResult, Pipeline, PipelineContext
from intelligence.context import ExecutionContext
from intelligence.engine import AIExecutionEngine
from intelligence.providers import AIRequest, DummyProvider, ProviderRegistry
from intelligence.router import Router
from intelligence.stages import IntelligenceStage

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_context(
    *,
    payload: dict | None = None,
    metadata: dict | None = None,
    intelligence_enabled: bool | None = None,
    intelligence_context: object = None,
) -> PipelineContext:
    return PipelineContext(
        performed_by="test_user",
        tenant="test_tenant",
        payload=payload or {"prompt": "Hello"},
        metadata=metadata or {},
        intelligence_enabled=intelligence_enabled,
        intelligence_context=intelligence_context,
    )


def make_engine_with_dummy(*, ai_enabled: bool = True) -> AIExecutionEngine:
    """Return an AIExecutionEngine backed by an isolated registry (DummyProvider only)."""
    reg = ProviderRegistry()
    reg.register(DummyProvider)
    engine = AIExecutionEngine(router=Router(registry=reg))
    return engine


@pytest.fixture()
def enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch both flag checks so ENABLE_AI=True everywhere."""
    monkeypatch.setattr("intelligence.engine.is_feature_enabled", lambda _: True)
    monkeypatch.setattr(
        "intelligence.stages.intelligence_stage.is_feature_enabled", lambda _: True
    )


@pytest.fixture()
def disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch both flag checks so ENABLE_AI=False everywhere."""
    monkeypatch.setattr("intelligence.engine.is_feature_enabled", lambda _: False)
    monkeypatch.setattr(
        "intelligence.stages.intelligence_stage.is_feature_enabled", lambda _: False
    )


def make_stage(*, ai_enabled_flag: bool = True) -> IntelligenceStage:
    """Return an IntelligenceStage with a DummyProvider-backed engine."""
    return IntelligenceStage(engine=make_engine_with_dummy())


# ===========================================================================
# Construction
# ===========================================================================


class TestConstruction:
    def test_default_engine_is_created(self) -> None:
        stage = IntelligenceStage()
        assert isinstance(stage._engine, AIExecutionEngine)

    def test_custom_engine_is_stored(self) -> None:
        engine = make_engine_with_dummy()
        stage = IntelligenceStage(engine=engine)
        assert stage._engine is engine

    def test_priority_is_500(self) -> None:
        assert IntelligenceStage.priority == 500

    def test_name_is_intelligence_stage(self) -> None:
        assert IntelligenceStage.name == "IntelligenceStage"

    def test_is_pipeline_stage_subclass(self) -> None:
        from apps.common.pipeline.core import PipelineStage
        assert issubclass(IntelligenceStage, PipelineStage)


# ===========================================================================
# Context-level guard: intelligence_enabled=False
# ===========================================================================


class TestContextDisableGuard:
    def test_returns_same_context_when_disabled(self, enabled: None) -> None:
        stage = make_stage()
        ctx = make_context(intelligence_enabled=False)
        result_ctx = stage.execute(ctx)
        assert result_ctx is ctx

    def test_intelligence_context_unchanged_when_disabled(self, enabled: None) -> None:
        stage = make_stage()
        ctx = make_context(intelligence_enabled=False)
        result_ctx = stage.execute(ctx)
        assert result_ctx.intelligence_context is None

    def test_context_disable_overrides_enabled_flag(self, enabled: None) -> None:
        """intelligence_enabled=False skips execution even when ENABLE_AI=True."""
        stage = make_stage()
        ctx = make_context(intelligence_enabled=False)
        result_ctx = stage.execute(ctx)
        # Context unchanged — no ExecutionResult attached
        assert not isinstance(result_ctx.intelligence_context, ExecutionResult)


# ===========================================================================
# Global feature flag guard
# ===========================================================================


class TestFeatureFlagGuard:
    def test_returns_unchanged_context_when_flag_off(self, disabled: None) -> None:
        stage = make_stage()
        ctx = make_context(intelligence_enabled=None)
        result_ctx = stage.execute(ctx)
        assert result_ctx is ctx

    def test_no_execution_result_when_flag_off(self, disabled: None) -> None:
        stage = make_stage()
        ctx = make_context(intelligence_enabled=None)
        result_ctx = stage.execute(ctx)
        assert not isinstance(result_ctx.intelligence_context, ExecutionResult)

    def test_intelligence_enabled_true_bypasses_flag_check(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """intelligence_enabled=True skips the flag check in the stage."""
        monkeypatch.setattr(
            "intelligence.stages.intelligence_stage.is_feature_enabled", lambda _: False
        )
        monkeypatch.setattr("intelligence.engine.is_feature_enabled", lambda _: True)
        stage = make_stage()
        ctx = make_context(intelligence_enabled=True)
        result_ctx = stage.execute(ctx)
        # Stage bypasses its own flag check; engine runs with ENABLE_AI=True
        assert isinstance(result_ctx.intelligence_context, ExecutionResult)


# ===========================================================================
# ExecutionContext — create vs. reuse
# ===========================================================================


class TestExecutionContext:
    def test_creates_execution_context_when_none(self, enabled: None) -> None:
        stage = make_stage()
        ctx = make_context(payload={"prompt": "hi"}, metadata={"key": "val"})
        result_ctx = stage.execute(ctx)
        # intelligence_context is now an ExecutionResult containing the response
        assert isinstance(result_ctx.intelligence_context, ExecutionResult)

    def test_reuses_existing_execution_context(self, enabled: None) -> None:
        exec_ctx = ExecutionContext(data={"prior": "data"}, metadata={"hint": 1})
        stage = make_stage()
        ctx = make_context(intelligence_context=exec_ctx)
        result_ctx = stage.execute(ctx)
        # The stage should have reused exec_ctx (passed as AIRequest.execution_context)
        assert isinstance(result_ctx.intelligence_context, ExecutionResult)

    def test_non_execution_context_triggers_new_context(self, enabled: None) -> None:
        stage = make_stage()
        # intelligence_context holds something other than ExecutionContext
        ctx = make_context(intelligence_context="some_string")
        result_ctx = stage.execute(ctx)
        assert isinstance(result_ctx.intelligence_context, ExecutionResult)

    def test_new_execution_context_data_comes_from_payload(self, enabled: None) -> None:
        """When a fresh ExecutionContext is created, its data mirrors context.payload."""
        stage = make_stage()
        ctx = make_context(payload={"prompt": "test"}, intelligence_context=None)
        # We can't directly inspect the created context since it's passed to the engine,
        # but we can verify execution succeeded (DummyProvider ignores payload anyway)
        result_ctx = stage.execute(ctx)
        assert isinstance(result_ctx.intelligence_context, ExecutionResult)


# ===========================================================================
# Successful execution
# ===========================================================================


class TestSuccessfulExecution:
    def test_returns_new_pipeline_context(self, enabled: None) -> None:
        stage = make_stage()
        ctx = make_context()
        result_ctx = stage.execute(ctx)
        assert isinstance(result_ctx, PipelineContext)
        assert result_ctx is not ctx

    def test_intelligence_context_is_execution_result(self, enabled: None) -> None:
        stage = make_stage()
        result_ctx = stage.execute(make_context())
        assert isinstance(result_ctx.intelligence_context, ExecutionResult)

    def test_execution_result_is_success(self, enabled: None) -> None:
        stage = make_stage()
        result_ctx = stage.execute(make_context())
        assert result_ctx.intelligence_context.success is True

    def test_payload_is_preserved(self, enabled: None) -> None:
        stage = make_stage()
        ctx = make_context(payload={"prompt": "preserve me"})
        result_ctx = stage.execute(ctx)
        assert result_ctx.payload == {"prompt": "preserve me"}

    def test_metadata_is_preserved(self, enabled: None) -> None:
        stage = make_stage()
        ctx = make_context(metadata={"key": "value"})
        result_ctx = stage.execute(ctx)
        assert result_ctx.metadata == {"key": "value"}

    def test_ai_task_from_metadata(self, enabled: None) -> None:
        """Stage reads ai_task from metadata to build the AIRequest."""
        stage = make_stage()
        ctx = make_context(metadata={"ai_task": "chat"})
        result_ctx = stage.execute(ctx)
        # DummyProvider supports chat; execution should succeed
        assert result_ctx.intelligence_context.success is True

    def test_defaults_to_text_task_when_not_specified(self, enabled: None) -> None:
        stage = make_stage()
        ctx = make_context(metadata={})
        result_ctx = stage.execute(ctx)
        assert isinstance(result_ctx.intelligence_context, ExecutionResult)


# ===========================================================================
# Engine failure handling
# ===========================================================================


class TestEngineFailureHandling:
    def test_engine_failure_still_attaches_result(self, enabled: None) -> None:
        """Stage attaches the failure ExecutionResult rather than propagating."""
        reg = ProviderRegistry()

        class _CrashProvider(DummyProvider):
            name: str = "crash"
            def execute(self, r: AIRequest) -> None:
                raise RuntimeError("boom")

        reg.register(_CrashProvider)
        engine = AIExecutionEngine(router=Router(registry=reg))
        stage = IntelligenceStage(engine=engine)
        result_ctx = stage.execute(make_context())
        assert isinstance(result_ctx.intelligence_context, ExecutionResult)
        assert result_ctx.intelligence_context.success is False

    def test_stage_never_raises_on_provider_crash(self, enabled: None) -> None:
        reg = ProviderRegistry()

        class _CrashProvider(DummyProvider):
            name: str = "crash2"
            def execute(self, r: AIRequest) -> None:
                raise ValueError("kaboom")

        reg.register(_CrashProvider)
        stage = IntelligenceStage(engine=AIExecutionEngine(router=Router(registry=reg)))
        # Must not raise
        result_ctx = stage.execute(make_context())
        assert isinstance(result_ctx, PipelineContext)

    def test_empty_registry_produces_failure_result(self, enabled: None) -> None:
        stage = IntelligenceStage(
            engine=AIExecutionEngine(router=Router(registry=ProviderRegistry()))
        )
        result_ctx = stage.execute(make_context())
        er = result_ctx.intelligence_context
        assert isinstance(er, ExecutionResult)
        assert er.success is False


# ===========================================================================
# PipelineContext propagation
# ===========================================================================


class TestPipelineContextPropagation:
    def test_performed_by_is_preserved(self, enabled: None) -> None:
        stage = make_stage()
        ctx = make_context()
        result_ctx = stage.execute(ctx)
        assert result_ctx.performed_by == ctx.performed_by

    def test_tenant_is_preserved(self, enabled: None) -> None:
        stage = make_stage()
        ctx = make_context()
        result_ctx = stage.execute(ctx)
        assert result_ctx.tenant == ctx.tenant

    def test_execution_id_is_preserved(self, enabled: None) -> None:
        stage = make_stage()
        ctx = make_context()
        result_ctx = stage.execute(ctx)
        assert result_ctx.execution_id == ctx.execution_id

    def test_stage_works_inside_pipeline(self, enabled: None) -> None:
        stage = make_stage()
        pipeline = Pipeline([stage])
        ctx = make_context()
        result = pipeline.run(ctx)
        assert isinstance(result, ExecutionResult)
        assert result.success is True


# ===========================================================================
# Immutability
# ===========================================================================


class TestImmutability:
    def test_original_context_not_mutated(self, enabled: None) -> None:
        stage = make_stage()
        ctx = make_context(intelligence_context=None)
        stage.execute(ctx)
        # Original frozen context untouched
        assert ctx.intelligence_context is None

    def test_returns_new_context_instance(self, enabled: None) -> None:
        stage = make_stage()
        ctx = make_context()
        result_ctx = stage.execute(ctx)
        assert result_ctx is not ctx

    def test_execution_result_is_frozen(self, enabled: None) -> None:
        from dataclasses import FrozenInstanceError
        stage = make_stage()
        result_ctx = stage.execute(make_context())
        er = result_ctx.intelligence_context
        with pytest.raises(FrozenInstanceError):
            er.success = False  # type: ignore[misc]


# ===========================================================================
# Determinism
# ===========================================================================


class TestDeterminism:
    def test_same_context_produces_same_outcome(self, enabled: None) -> None:
        stage = make_stage()
        ctx = make_context()
        r1 = stage.execute(ctx)
        r2 = stage.execute(ctx)
        assert r1.intelligence_context.success == r2.intelligence_context.success
        assert r1.intelligence_context.status_code == r2.intelligence_context.status_code

    def test_skip_is_deterministic(self, disabled: None) -> None:
        stage = make_stage()
        ctx = make_context(intelligence_enabled=None)
        assert stage.execute(ctx) is stage.execute(ctx)
