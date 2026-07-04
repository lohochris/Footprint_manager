import pytest
from backend.intelligence.provider_state import ProviderLifecycleState
from backend.intelligence.policy import PolicyEngine
from backend.intelligence.policies.execution_policy import ExecutionPolicy
from backend.intelligence.providers.base import AIProvider
from backend.intelligence.providers.request import AIRequest
from backend.intelligence.providers.response import AIResponse
from backend.intelligence.providers.provider_metadata import HealthStatus
from backend.intelligence.router import Router, NoProviderAvailableError
from backend.intelligence.engine import AIExecutionEngine
from backend.intelligence.providers.registry import ProviderRegistry

@pytest.fixture(autouse=True)
def ai_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch get_feature_flags and is_feature_enabled so ENABLE_AI returns True."""
    monkeypatch.setattr(
        "backend.intelligence.engine.is_feature_enabled",
        lambda flag: True,
    )
    monkeypatch.setattr(
        "backend.intelligence.policies.policy_builder.get_feature_flags",
        lambda: {"ENABLE_AI": True},
    )

# 1. Test ProviderLifecycleState
def test_provider_lifecycle_state_values():
    assert ProviderLifecycleState.INITIALIZED == "initialized"
    assert ProviderLifecycleState.ACTIVE == "active"
    assert ProviderLifecycleState.DEACTIVATED == "deactivated"
    assert ProviderLifecycleState.TERMINATED == "terminated"

# Mock provider for testing
class MockTestProvider(AIProvider):
    name = "mock_test_provider"
    version = "1.0.0"
    description = "Mock provider for combined tests"

    def __init__(self, healthy=True, state=ProviderLifecycleState.ACTIVE):
        self._healthy = healthy
        self._lifecycle_state = state
        self.initialize_called = 0
        self.execute_called = 0

    def initialize(self):
        self.initialize_called += 1

    def health_check(self) -> HealthStatus:
        return HealthStatus(healthy=self._healthy, message="Mock health check")

    def capabilities(self):
        return ["text"]

    def supports(self, task: str) -> bool:
        return task == "text"

    def execute(self, request: AIRequest) -> AIResponse:
        self.execute_called += 1
        return AIResponse(
            status="success",
            provider=self.name,
            metadata={},
            usage={},
            output="Executed successfully",
            diagnostics=None,
        )

# 2. Test PolicyEngine
class TestPolicyEngineUnit:
    def test_evaluate_active_and_healthy(self):
        engine = PolicyEngine()
        provider = MockTestProvider(healthy=True, state=ProviderLifecycleState.ACTIVE)
        policy = ExecutionPolicy(health_required=True)
        res = engine.evaluate(None, provider, policy)
        assert res.allowed is True
        assert res.diagnostics["allowed"] is True

    def test_evaluate_inactive_rejected(self):
        engine = PolicyEngine()
        provider = MockTestProvider(healthy=True, state=ProviderLifecycleState.DEACTIVATED)
        policy = ExecutionPolicy(health_required=True)
        res = engine.evaluate(None, provider, policy)
        assert res.allowed is False
        assert "lifecycle state" in res.reason

    def test_evaluate_unhealthy_rejected_when_health_required(self):
        engine = PolicyEngine()
        provider = MockTestProvider(healthy=False, state=ProviderLifecycleState.ACTIVE)
        policy = ExecutionPolicy(health_required=True)
        res = engine.evaluate(None, provider, policy)
        assert res.allowed is False
        assert "unhealthy" in res.reason

    def test_evaluate_unhealthy_allowed_when_health_not_required(self):
        engine = PolicyEngine()
        provider = MockTestProvider(healthy=False, state=ProviderLifecycleState.ACTIVE)
        policy = ExecutionPolicy(health_required=False)
        res = engine.evaluate(None, provider, policy)
        assert res.allowed is True

    def test_evaluate_required_provider_mismatch(self):
        engine = PolicyEngine()
        provider = MockTestProvider(healthy=True, state=ProviderLifecycleState.ACTIVE)
        policy = ExecutionPolicy(required_provider="other_provider")
        res = engine.evaluate(None, provider, policy)
        assert res.allowed is False
        assert "does not match required provider" in res.reason

# 3. Test Health-Aware Routing
class TestHealthAwareRouting:
    def test_select_only_healthy_and_active_providers(self):
        registry = ProviderRegistry()

        class UnhealthyProvider(MockTestProvider):
            name = "unhealthy_p"
            def __init__(self):
                super().__init__(healthy=False, state=ProviderLifecycleState.ACTIVE)

        class InactiveProvider(MockTestProvider):
            name = "inactive_p"
            def __init__(self):
                super().__init__(healthy=True, state=ProviderLifecycleState.DEACTIVATED)

        class HealthyActiveProvider(MockTestProvider):
            name = "healthy_active_p"
            def __init__(self):
                super().__init__(healthy=True, state=ProviderLifecycleState.ACTIVE)

        registry.register(UnhealthyProvider)
        registry.register(InactiveProvider)
        registry.register(HealthyActiveProvider)

        router = Router(registry=registry)
        req = AIRequest(task="text", execution_context=None, payload={}, metadata={})
        selected = router.select(req)
        assert selected is HealthyActiveProvider

    def test_select_raises_no_provider_available_when_none_healthy(self):
        registry = ProviderRegistry()
        class UnhealthyProvider(MockTestProvider):
            name = "unhealthy_p"
            def __init__(self):
                super().__init__(healthy=False, state=ProviderLifecycleState.ACTIVE)
        registry.register(UnhealthyProvider)
        router = Router(registry=registry)
        req = AIRequest(task="text", execution_context=None, payload={}, metadata={})
        with pytest.raises(NoProviderAvailableError):
            router.select(req)

# 4. Test Engine Policy Integration & Diagnostics
class TestEnginePolicyIntegration:
    def test_engine_attaches_diagnostics_on_success(self):
        registry = ProviderRegistry()
        registry.register(MockTestProvider)
        router = Router(registry=registry)
        engine = AIExecutionEngine(router=router)

        req = AIRequest(task="text", execution_context=None, payload={}, metadata={})
        res = engine.execute(req)

        assert res.success is True
        assert "diagnostics" in res.metadata
        diagnostics = res.metadata["diagnostics"]
        assert diagnostics["allowed"] is True
        assert diagnostics["attempts"] == 1
        assert diagnostics["provider"] == "mock_test_provider"

    def test_engine_attaches_diagnostics_on_policy_rejection(self):
        registry = ProviderRegistry()
        class InactiveTestProvider(MockTestProvider):
            name = "inactive_test"
            def __init__(self):
                super().__init__(healthy=True, state=ProviderLifecycleState.DEACTIVATED)
        registry.register(InactiveTestProvider)
        router = Router(registry=registry)

        engine = AIExecutionEngine(router=router)
        req = AIRequest(task="text", execution_context=None, payload={}, metadata={"provider": "inactive_test"})
        res = engine.execute(req)

        assert res.success is False
        assert "diagnostics" in res.metadata
        diagnostics = res.metadata["diagnostics"]
        assert diagnostics["allowed"] is False
        assert diagnostics["lifecycle_state"] == ProviderLifecycleState.DEACTIVATED

    def test_engine_dry_run_diagnostics(self):
        engine = AIExecutionEngine()
        req = AIRequest(task="text", execution_context=None, payload={}, metadata={})
        res = engine.execute(req, dry_run=True)

        assert res.success is True
        assert res.metadata["dry_run"] is True
        assert res.metadata["diagnostics"]["dry_run"] is True
