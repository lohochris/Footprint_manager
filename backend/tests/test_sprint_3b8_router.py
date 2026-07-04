# backend/tests/test_sprint_3b8_router.py
"""Sprint 3B.8 — Router unit tests.

All tests are deterministic and offline.
No Django DB, no network calls, no randomness.
"""

import pytest
from backend.intelligence.providers import (
    AIRequest,
    DummyProvider,
    EchoProvider,
    MockProvider,
    ProviderRegistry,
)
from backend.intelligence.router import NoProviderAvailableError, ProviderNotFoundError, Router

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


@pytest.fixture()
def isolated_registry() -> ProviderRegistry:
    """Fresh registry — never touches the global singleton."""
    return ProviderRegistry()


@pytest.fixture()
def populated_registry(isolated_registry: ProviderRegistry) -> ProviderRegistry:
    """Registry with all three Sprint 3B.7 providers registered."""
    isolated_registry.register(DummyProvider)
    isolated_registry.register(EchoProvider)
    isolated_registry.register(MockProvider)
    return isolated_registry


@pytest.fixture()
def router(populated_registry: ProviderRegistry) -> Router:
    """Router backed by the populated isolated registry."""
    return Router(registry=populated_registry)


# ===========================================================================
# Router construction
# ===========================================================================


class TestRouterConstruction:
    def test_default_registry_is_global_singleton(self) -> None:
        """Router() with no argument uses the global _registry singleton."""
        from backend.intelligence.providers.registry import _registry
        r = Router()
        assert r._registry is _registry

    def test_custom_registry_is_stored(self, isolated_registry: ProviderRegistry) -> None:
        r = Router(registry=isolated_registry)
        assert r._registry is isolated_registry

    def test_none_registry_falls_back_to_global(self) -> None:
        from backend.intelligence.providers.registry import _registry
        r = Router(registry=None)
        assert r._registry is _registry


# ===========================================================================
# Explicit provider selection (metadata["provider"])
# ===========================================================================


class TestExplicitSelection:
    def test_select_by_name_dummy(self, router: Router) -> None:
        req = make_request(metadata={"provider": "dummy"})
        assert router.select(req) is DummyProvider

    def test_select_by_name_echo(self, router: Router) -> None:
        req = make_request(metadata={"provider": "echo"})
        assert router.select(req) is EchoProvider

    def test_select_by_name_mock(self, router: Router) -> None:
        req = make_request(metadata={"provider": "mock"})
        assert router.select(req) is MockProvider

    def test_unknown_explicit_name_raises_provider_not_found(
        self, router: Router
    ) -> None:
        req = make_request(metadata={"provider": "nonexistent"})
        with pytest.raises(ProviderNotFoundError, match="nonexistent"):
            router.select(req)

    def test_explicit_name_overrides_task_capability(self, router: Router) -> None:
        """Even if EchoProvider doesn't support 'chat', explicit name wins."""
        req = make_request(task="chat", metadata={"provider": "echo"})
        assert router.select(req) is EchoProvider


# ===========================================================================
# Capability-based selection
# ===========================================================================


class TestCapabilitySelection:
    def test_text_task_returns_capable_provider(self, router: Router) -> None:
        """All three providers support 'text'; should return the first by priority."""
        req = make_request(task="text")
        result = router.select(req)
        # All share priority 0; insertion order: dummy first
        assert result is DummyProvider

    def test_chat_task_returns_capable_provider(self, router: Router) -> None:
        """Only dummy and mock support 'chat'; echo does not."""
        req = make_request(task="chat")
        result = router.select(req)
        assert result in (DummyProvider, MockProvider)
        # EchoProvider must not be selected for chat
        assert result is not EchoProvider

    def test_structured_output_task_returns_mock(self, router: Router) -> None:
        """Only MockProvider supports structured_output."""
        req = make_request(task="structured_output")
        assert router.select(req) is MockProvider

    def test_unknown_task_falls_back_to_default(self, router: Router) -> None:
        """No provider supports 'embeddings'; falls back to registry default."""
        req = make_request(task="embeddings")
        default = router._registry.default()
        assert router.select(req) is default

    def test_capability_selection_is_deterministic(self, router: Router) -> None:
        req = make_request(task="text")
        assert router.select(req) is router.select(req)


# ===========================================================================
# Default fallback
# ===========================================================================


class TestDefaultFallback:
    def test_unknown_task_uses_default_when_set(
        self, isolated_registry: ProviderRegistry
    ) -> None:
        isolated_registry.register(DummyProvider)
        r = Router(registry=isolated_registry)
        req = make_request(task="__no_provider_supports_this__")
        assert r.select(req) is DummyProvider

    def test_empty_registry_raises_no_provider_available(
        self, isolated_registry: ProviderRegistry
    ) -> None:
        r = Router(registry=isolated_registry)
        req = make_request(task="text")
        with pytest.raises(NoProviderAvailableError):
            r.select(req)

    def test_no_capable_provider_and_empty_raises(
        self, isolated_registry: ProviderRegistry
    ) -> None:
        r = Router(registry=isolated_registry)
        req = make_request(task="embeddings")
        with pytest.raises(NoProviderAvailableError):
            r.select(req)


# ===========================================================================
# Single-provider registry
# ===========================================================================


class TestSingleProviderRegistry:
    def test_only_echo_registered_returns_echo_for_text(
        self, isolated_registry: ProviderRegistry
    ) -> None:
        isolated_registry.register(EchoProvider)
        r = Router(registry=isolated_registry)
        assert r.select(make_request(task="text")) is EchoProvider

    def test_only_echo_registered_falls_back_for_chat(
        self, isolated_registry: ProviderRegistry
    ) -> None:
        """EchoProvider doesn't support chat; falls back to default (EchoProvider)."""
        isolated_registry.register(EchoProvider)
        r = Router(registry=isolated_registry)
        # No capable provider for 'chat'; default is EchoProvider
        assert r.select(make_request(task="chat")) is EchoProvider


# ===========================================================================
# Error message content
# ===========================================================================


class TestErrorMessages:
    def test_provider_not_found_error_contains_name(self, router: Router) -> None:
        req = make_request(metadata={"provider": "acme_llm"})
        with pytest.raises(ProviderNotFoundError, match="acme_llm"):
            router.select(req)

    def test_no_provider_available_error_contains_task(
        self, isolated_registry: ProviderRegistry
    ) -> None:
        r = Router(registry=isolated_registry)
        req = make_request(task="vision")
        with pytest.raises(NoProviderAvailableError, match="vision"):
            r.select(req)


# ===========================================================================
# Router returns class, not instance
# ===========================================================================


class TestReturnType:
    def test_select_returns_class_not_instance(self, router: Router) -> None:
        req = make_request(task="text")
        result = router.select(req)
        assert isinstance(result, type)
        assert issubclass(result, __import__(
            'backend.intelligence.providers.base', fromlist=['AIProvider']
        ).AIProvider)

    def test_returned_class_is_instantiable(self, router: Router) -> None:
        req = make_request(task="text")
        provider_cls = router.select(req)
        instance = provider_cls()
        assert callable(instance.execute)


# ===========================================================================
# Empty metadata / None metadata edge cases
# ===========================================================================


class TestEdgeCases:
    def test_empty_metadata_dict_falls_through_to_capability(
        self, router: Router
    ) -> None:
        req = make_request(task="text", metadata={})
        assert router.select(req) is not None

    def test_metadata_without_provider_key_uses_task(self, router: Router) -> None:
        req = make_request(task="structured_output", metadata={"temperature": 0.5})
        assert router.select(req) is MockProvider

    def test_provider_key_with_empty_string_falls_through(
        self, router: Router
    ) -> None:
        """Empty string is falsy — should not trigger explicit selection."""
        req = make_request(task="text", metadata={"provider": ""})
        # Empty string is falsy, so capability selection runs
        result = router.select(req)
        assert result is not None
