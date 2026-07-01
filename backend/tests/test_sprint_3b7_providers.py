"""Sprint 3B.7 – AI Provider Architecture unit tests.

Covers: metadata models, isolated registry, global registry, DummyProvider,
MockProvider (all scenarios), EchoProvider, and package exports.

No network access.  No Django DB.  All tests are deterministic.
"""

from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest
from intelligence.providers import (
    AIProvider,
    AIRequest,
    AIResponse,
    DummyProvider,
    EchoProvider,
    HealthStatus,
    MockProvider,
    MockScenario,
    ProviderCapabilities,
    ProviderMetadata,
    ProviderRegistry,
    register_provider,
)
from intelligence.providers.registry import get_provider, list_providers

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def registry() -> ProviderRegistry:
    """Fresh isolated registry – never touches the global singleton."""
    return ProviderRegistry()


@pytest.fixture()
def dummy() -> DummyProvider:
    return DummyProvider()


@pytest.fixture()
def echo() -> EchoProvider:
    return EchoProvider()


@pytest.fixture()
def text_request() -> AIRequest:
    return AIRequest(
        task="text",
        execution_context=None,
        payload={"prompt": "Hello world"},
        metadata={},
    )


@pytest.fixture()
def empty_request() -> AIRequest:
    return AIRequest(task="text", execution_context=None, payload={}, metadata={})


# ===========================================================================
# ProviderCapabilities
# ===========================================================================


class TestProviderCapabilities:
    def test_all_defaults_are_false(self) -> None:
        caps = ProviderCapabilities()
        assert caps.supports_text is False
        assert caps.supports_chat is False
        assert caps.supports_structured_output is False
        assert caps.supports_streaming is False
        assert caps.supports_embeddings is False

    def test_explicit_true_flags_are_stored(self) -> None:
        caps = ProviderCapabilities(supports_text=True, supports_chat=True)
        assert caps.supports_text is True
        assert caps.supports_chat is True
        assert caps.supports_structured_output is False

    def test_all_flags_can_be_true(self) -> None:
        caps = ProviderCapabilities(
            supports_text=True,
            supports_chat=True,
            supports_structured_output=True,
            supports_streaming=True,
            supports_embeddings=True,
        )
        assert all([
            caps.supports_text,
            caps.supports_chat,
            caps.supports_structured_output,
            caps.supports_streaming,
            caps.supports_embeddings,
        ])

    def test_is_frozen(self) -> None:
        caps = ProviderCapabilities()
        with pytest.raises(FrozenInstanceError):
            caps.supports_text = True  # type: ignore[misc]

    def test_equality_identical(self) -> None:
        assert ProviderCapabilities() == ProviderCapabilities()

    def test_equality_differs_on_flag(self) -> None:
        assert ProviderCapabilities(supports_text=True) != ProviderCapabilities()


# ===========================================================================
# HealthStatus
# ===========================================================================


class TestHealthStatus:
    def test_healthy_field(self) -> None:
        assert HealthStatus(healthy=True, message="ok").healthy is True

    def test_message_field(self) -> None:
        assert HealthStatus(healthy=False, message="down").message == "down"

    def test_timestamp_populated_by_default_factory(self) -> None:
        hs = HealthStatus(healthy=True, message="ok")
        assert isinstance(hs.timestamp, datetime)

    def test_explicit_timestamp_accepted(self) -> None:
        ts = datetime(2026, 1, 1, 12, 0, 0)
        hs = HealthStatus(healthy=True, message="ok", timestamp=ts)
        assert hs.timestamp == ts

    def test_two_instances_have_independent_timestamps(self) -> None:
        hs1 = HealthStatus(healthy=True, message="a")
        hs2 = HealthStatus(healthy=True, message="b")
        assert isinstance(hs1.timestamp, datetime)
        assert isinstance(hs2.timestamp, datetime)

    def test_is_frozen(self) -> None:
        hs = HealthStatus(healthy=True, message="ok")
        with pytest.raises(FrozenInstanceError):
            hs.healthy = False  # type: ignore[misc]


# ===========================================================================
# ProviderMetadata
# ===========================================================================


class TestProviderMetadata:
    def test_fields_are_stored(self) -> None:
        caps = ProviderCapabilities(supports_text=True)
        pm = ProviderMetadata(name="x", version="1.0", description="d", capabilities=caps)
        assert pm.name == "x"
        assert pm.version == "1.0"
        assert pm.description == "d"
        assert pm.capabilities is caps

    def test_is_frozen(self) -> None:
        pm = ProviderMetadata(
            name="x",
            version="1.0",
            description="d",
            capabilities=ProviderCapabilities(),
        )
        with pytest.raises(FrozenInstanceError):
            pm.name = "y"  # type: ignore[misc]

    def test_equality(self) -> None:
        caps = ProviderCapabilities()
        pm1 = ProviderMetadata(name="x", version="1.0", description="d", capabilities=caps)
        pm2 = ProviderMetadata(name="x", version="1.0", description="d", capabilities=caps)
        assert pm1 == pm2

    def test_inequality_on_name(self) -> None:
        caps = ProviderCapabilities()
        pm1 = ProviderMetadata(name="a", version="1.0", description="d", capabilities=caps)
        pm2 = ProviderMetadata(name="b", version="1.0", description="d", capabilities=caps)
        assert pm1 != pm2


# ===========================================================================
# ProviderRegistry – isolated instance
# ===========================================================================


class TestProviderRegistry:
    def test_get_unknown_returns_none(self, registry: ProviderRegistry) -> None:
        assert registry.get("nonexistent") is None

    def test_register_and_get(self, registry: ProviderRegistry) -> None:
        registry.register(DummyProvider)
        assert registry.get("dummy") is DummyProvider

    def test_duplicate_registration_raises_value_error(self, registry: ProviderRegistry) -> None:
        registry.register(DummyProvider)
        with pytest.raises(ValueError, match="already registered"):
            registry.register(DummyProvider)

    def test_unregister_removes_provider(self, registry: ProviderRegistry) -> None:
        registry.register(DummyProvider)
        registry.unregister("dummy")
        assert registry.get("dummy") is None

    def test_unregister_unknown_name_is_silent(self, registry: ProviderRegistry) -> None:
        registry.unregister("nonexistent")  # must not raise

    def test_list_returns_all_registered(self, registry: ProviderRegistry) -> None:
        registry.register(DummyProvider)
        registry.register(MockProvider)
        assert DummyProvider in registry.list()
        assert MockProvider in registry.list()

    def test_list_is_stable_across_calls(self, registry: ProviderRegistry) -> None:
        registry.register(DummyProvider)
        registry.register(MockProvider)
        assert registry.list() == registry.list()

    def test_default_returns_first_provider(self, registry: ProviderRegistry) -> None:
        registry.register(DummyProvider)
        assert registry.default() is DummyProvider

    def test_default_returns_none_when_empty(self, registry: ProviderRegistry) -> None:
        assert registry.default() is None

    def test_capabilities_returns_list(self, registry: ProviderRegistry) -> None:
        registry.register(DummyProvider)
        caps = registry.capabilities("dummy")
        assert isinstance(caps, list)
        assert "text" in caps

    def test_capabilities_raises_key_error_for_unknown(self, registry: ProviderRegistry) -> None:
        with pytest.raises(KeyError):
            registry.capabilities("unknown")

    def test_register_after_unregister_succeeds(self, registry: ProviderRegistry) -> None:
        registry.register(DummyProvider)
        registry.unregister("dummy")
        registry.register(DummyProvider)  # must not raise
        assert registry.get("dummy") is DummyProvider

    def test_name_falls_back_to_class_name(self, registry: ProviderRegistry) -> None:
        class _NamelessDummy(AIProvider):
            def initialize(self) -> None: ...  # noqa: ANN201
            def health_check(self):  # noqa: ANN201
                return {}
            def capabilities(self) -> list:  # noqa: ANN201
                return []
            def supports(self, task: str) -> bool:  # noqa: ANN001
                return False
            def execute(self, request: AIRequest) -> AIResponse:  # noqa: ANN001
                ...  # type: ignore[return-value]

        registry.register(_NamelessDummy)
        assert registry.get("_NamelessDummy") is _NamelessDummy


# ===========================================================================
# Global registry – read-only; providers registered on package import
# ===========================================================================


class TestGlobalRegistry:
    def test_dummy_is_registered(self) -> None:
        assert get_provider("dummy") is DummyProvider

    def test_mock_is_registered(self) -> None:
        assert get_provider("mock") is MockProvider

    def test_echo_is_registered(self) -> None:
        assert get_provider("echo") is EchoProvider

    def test_unknown_provider_returns_none(self) -> None:
        assert get_provider("_not_a_real_provider_") is None

    def test_list_contains_all_three(self) -> None:
        names = {getattr(p, "name", p.__name__) for p in list_providers()}
        assert {"dummy", "mock", "echo"}.issubset(names)

    def test_list_is_deterministic(self) -> None:
        assert list_providers() == list_providers()

    def test_global_registry_capabilities_dummy(self) -> None:
        from intelligence.providers.registry import _registry
        caps = _registry.capabilities("dummy")
        assert "text" in caps
        assert "chat" in caps

    def test_global_registry_capabilities_mock(self) -> None:
        from intelligence.providers.registry import _registry
        caps = _registry.capabilities("mock")
        assert "text" in caps
        assert "structured_output" in caps

    def test_global_registry_capabilities_echo(self) -> None:
        from intelligence.providers.registry import _registry
        assert _registry.capabilities("echo") == ["text"]

    def test_duplicate_registration_still_rejected_globally(self) -> None:
        with pytest.raises(ValueError, match="already registered"):
            register_provider(DummyProvider)


# ===========================================================================
# DummyProvider
# ===========================================================================


class TestDummyProvider:
    def test_is_subclass_of_ai_provider(self) -> None:
        assert issubclass(DummyProvider, AIProvider)

    def test_name(self, dummy: DummyProvider) -> None:
        assert dummy.name == "dummy"

    def test_version(self, dummy: DummyProvider) -> None:
        assert dummy.version == "1.0.0"

    def test_description_is_non_empty(self, dummy: DummyProvider) -> None:
        assert dummy.description

    def test_metadata_type(self, dummy: DummyProvider) -> None:
        assert isinstance(dummy.metadata, ProviderMetadata)

    def test_metadata_capabilities_type(self, dummy: DummyProvider) -> None:
        assert isinstance(dummy.metadata.capabilities, ProviderCapabilities)

    def test_capabilities_supports_text(self, dummy: DummyProvider) -> None:
        assert dummy.metadata.capabilities.supports_text is True

    def test_capabilities_supports_chat(self, dummy: DummyProvider) -> None:
        assert dummy.metadata.capabilities.supports_chat is True

    def test_capabilities_no_structured_output(self, dummy: DummyProvider) -> None:
        assert dummy.metadata.capabilities.supports_structured_output is False

    def test_capabilities_no_streaming(self, dummy: DummyProvider) -> None:
        assert dummy.metadata.capabilities.supports_streaming is False

    def test_capabilities_no_embeddings(self, dummy: DummyProvider) -> None:
        assert dummy.metadata.capabilities.supports_embeddings is False

    def test_capabilities_list_contains_text(self, dummy: DummyProvider) -> None:
        assert "text" in dummy.capabilities()

    def test_capabilities_list_contains_chat(self, dummy: DummyProvider) -> None:
        assert "chat" in dummy.capabilities()

    def test_capabilities_list_excludes_structured_output(self, dummy: DummyProvider) -> None:
        assert "structured_output" not in dummy.capabilities()

    def test_supports_text(self, dummy: DummyProvider) -> None:
        assert dummy.supports("text") is True

    def test_supports_chat(self, dummy: DummyProvider) -> None:
        assert dummy.supports("chat") is True

    def test_supports_embeddings_false(self, dummy: DummyProvider) -> None:
        assert dummy.supports("embeddings") is False

    def test_health_check_type(self, dummy: DummyProvider) -> None:
        assert isinstance(dummy.health_check(), HealthStatus)

    def test_health_check_healthy(self, dummy: DummyProvider) -> None:
        assert dummy.health_check().healthy is True

    def test_health_check_message(self, dummy: DummyProvider) -> None:
        assert dummy.health_check().message == "Dummy provider is healthy."

    def test_health_check_has_timestamp(self, dummy: DummyProvider) -> None:
        assert isinstance(dummy.health_check().timestamp, datetime)

    def test_execute_returns_ai_response(
        self, dummy: DummyProvider, text_request: AIRequest
    ) -> None:
        assert isinstance(dummy.execute(text_request), AIResponse)

    def test_execute_status_success(self, dummy: DummyProvider, text_request: AIRequest) -> None:
        assert dummy.execute(text_request).status == "success"

    def test_execute_provider_field(self, dummy: DummyProvider, text_request: AIRequest) -> None:
        assert dummy.execute(text_request).provider == "dummy"

    def test_execute_output(self, dummy: DummyProvider, text_request: AIRequest) -> None:
        assert dummy.execute(text_request).output == "Dummy provider executed successfully."

    def test_execute_is_deterministic(self, dummy: DummyProvider, text_request: AIRequest) -> None:
        assert dummy.execute(text_request) == dummy.execute(text_request)

    def test_execute_ignores_request_content(self, dummy: DummyProvider) -> None:
        req_a = AIRequest(task="text", execution_context=None, payload={"prompt": "A"}, metadata={})
        req_b = AIRequest(task="text", execution_context=None, payload={"prompt": "B"}, metadata={})
        assert dummy.execute(req_a) == dummy.execute(req_b)

    def test_metadata_is_immutable(self, dummy: DummyProvider) -> None:
        with pytest.raises(FrozenInstanceError):
            dummy.metadata.name = "changed"  # type: ignore[misc]

    def test_initialize_does_not_raise(self, dummy: DummyProvider) -> None:
        dummy.initialize()


# ===========================================================================
# MockProvider
# ===========================================================================


class TestMockScenario:
    def test_all_four_scenarios_exist(self) -> None:
        assert set(MockScenario) == {
            MockScenario.SUCCESS,
            MockScenario.FAILURE,
            MockScenario.TIMEOUT,
            MockScenario.UNSUPPORTED_CAPABILITY,
        }

    def test_scenario_values(self) -> None:
        assert MockScenario.SUCCESS == "success"
        assert MockScenario.FAILURE == "failure"
        assert MockScenario.TIMEOUT == "timeout"
        assert MockScenario.UNSUPPORTED_CAPABILITY == "unsupported_capability"


class TestMockProvider:
    def test_is_subclass_of_ai_provider(self) -> None:
        assert issubclass(MockProvider, AIProvider)

    def test_name(self) -> None:
        assert MockProvider.name == "mock"

    def test_version(self) -> None:
        assert MockProvider.version == "1.0.0"

    def test_description_is_non_empty(self) -> None:
        assert MockProvider.description

    def test_metadata_type(self) -> None:
        assert isinstance(MockProvider.metadata, ProviderMetadata)

    def test_capabilities_supports_text(self) -> None:
        assert MockProvider.metadata.capabilities.supports_text is True

    def test_capabilities_supports_chat(self) -> None:
        assert MockProvider.metadata.capabilities.supports_chat is True

    def test_capabilities_supports_structured_output(self) -> None:
        assert MockProvider.metadata.capabilities.supports_structured_output is True

    def test_capabilities_no_streaming(self) -> None:
        assert MockProvider.metadata.capabilities.supports_streaming is False

    def test_capabilities_no_embeddings(self) -> None:
        assert MockProvider.metadata.capabilities.supports_embeddings is False

    def test_capabilities_list(self) -> None:
        caps = MockProvider().capabilities()
        assert "text" in caps
        assert "chat" in caps
        assert "structured_output" in caps
        assert "streaming" not in caps

    def test_supports_text(self) -> None:
        assert MockProvider().supports("text") is True

    def test_supports_embeddings_false(self) -> None:
        assert MockProvider().supports("embeddings") is False

    def test_health_check_type(self) -> None:
        assert isinstance(MockProvider().health_check(), HealthStatus)

    def test_health_check_healthy(self) -> None:
        assert MockProvider().health_check().healthy is True

    def test_health_check_message(self) -> None:
        assert MockProvider().health_check().message == "Mock provider is healthy."

    def test_default_scenario_is_success(self, empty_request: AIRequest) -> None:
        assert MockProvider().execute(empty_request).status == "success"

    @pytest.mark.parametrize("scenario,expected_status", [
        (MockScenario.SUCCESS, "success"),
        (MockScenario.FAILURE, "error"),
        (MockScenario.TIMEOUT, "error"),
        (MockScenario.UNSUPPORTED_CAPABILITY, "error"),
    ])
    def test_scenario_returns_correct_status(
        self, scenario: MockScenario, expected_status: str, empty_request: AIRequest
    ) -> None:
        assert MockProvider(scenario).execute(empty_request).status == expected_status

    def test_success_output(self, empty_request: AIRequest) -> None:
        resp = MockProvider(MockScenario.SUCCESS).execute(empty_request)
        assert resp.output == "Mock provider executed successfully."

    def test_success_provider_field(self, empty_request: AIRequest) -> None:
        assert MockProvider(MockScenario.SUCCESS).execute(empty_request).provider == "mock"

    @pytest.mark.parametrize("scenario,expected_error", [
        (MockScenario.FAILURE, "Mock provider simulated failure."),
        (MockScenario.TIMEOUT, "Mock provider simulated timeout."),
        (MockScenario.UNSUPPORTED_CAPABILITY, "Requested capability is not supported."),
    ])
    def test_error_scenario_diagnostics(
        self, scenario: MockScenario, expected_error: str, empty_request: AIRequest
    ) -> None:
        resp = MockProvider(scenario).execute(empty_request)
        assert resp.diagnostics is not None
        assert resp.diagnostics["error"] == expected_error

    @pytest.mark.parametrize("scenario", list(MockScenario))
    def test_all_scenarios_are_deterministic(
        self, scenario: MockScenario, empty_request: AIRequest
    ) -> None:
        p = MockProvider(scenario)
        assert p.execute(empty_request) == p.execute(empty_request)

    @pytest.mark.parametrize("scenario", list(MockScenario))
    def test_no_scenario_raises(self, scenario: MockScenario, empty_request: AIRequest) -> None:
        MockProvider(scenario).execute(empty_request)  # must not raise

    def test_execute_returns_ai_response(self, empty_request: AIRequest) -> None:
        assert isinstance(MockProvider().execute(empty_request), AIResponse)

    def test_metadata_is_immutable(self) -> None:
        with pytest.raises(FrozenInstanceError):
            MockProvider.metadata.name = "changed"  # type: ignore[misc]

    def test_initialize_does_not_raise(self) -> None:
        MockProvider().initialize()


# ===========================================================================
# EchoProvider
# ===========================================================================


class TestEchoProvider:
    def test_is_subclass_of_ai_provider(self) -> None:
        assert issubclass(EchoProvider, AIProvider)

    def test_name(self, echo: EchoProvider) -> None:
        assert echo.name == "echo"

    def test_version(self, echo: EchoProvider) -> None:
        assert echo.version == "1.0.0"

    def test_description_contains_echo(self, echo: EchoProvider) -> None:
        assert "echo" in echo.description.lower()

    def test_metadata_type(self, echo: EchoProvider) -> None:
        assert isinstance(echo.metadata, ProviderMetadata)

    def test_capabilities_text_only(self, echo: EchoProvider) -> None:
        assert echo.capabilities() == ["text"]

    def test_capabilities_supports_text(self, echo: EchoProvider) -> None:
        assert echo.metadata.capabilities.supports_text is True

    def test_capabilities_no_chat(self, echo: EchoProvider) -> None:
        assert echo.metadata.capabilities.supports_chat is False

    def test_capabilities_no_structured_output(self, echo: EchoProvider) -> None:
        assert echo.metadata.capabilities.supports_structured_output is False

    def test_capabilities_no_streaming(self, echo: EchoProvider) -> None:
        assert echo.metadata.capabilities.supports_streaming is False

    def test_capabilities_no_embeddings(self, echo: EchoProvider) -> None:
        assert echo.metadata.capabilities.supports_embeddings is False

    def test_supports_text(self, echo: EchoProvider) -> None:
        assert echo.supports("text") is True

    def test_supports_chat_false(self, echo: EchoProvider) -> None:
        assert echo.supports("chat") is False

    def test_supports_embeddings_false(self, echo: EchoProvider) -> None:
        assert echo.supports("embeddings") is False

    def test_health_check_type(self, echo: EchoProvider) -> None:
        assert isinstance(echo.health_check(), HealthStatus)

    def test_health_check_healthy(self, echo: EchoProvider) -> None:
        assert echo.health_check().healthy is True

    def test_health_check_message(self, echo: EchoProvider) -> None:
        assert echo.health_check().message == "Echo provider is healthy."

    def test_execute_echoes_prompt(self, echo: EchoProvider) -> None:
        prompt = "Summarize this document"
        req = AIRequest(
            task="text", execution_context=None,
            payload={"prompt": prompt}, metadata={},
        )
        assert echo.execute(req).output == prompt

    def test_execute_status_success(self, echo: EchoProvider, text_request: AIRequest) -> None:
        assert echo.execute(text_request).status == "success"

    def test_execute_provider_field(self, echo: EchoProvider, text_request: AIRequest) -> None:
        assert echo.execute(text_request).provider == "echo"

    def test_execute_returns_ai_response(self, echo: EchoProvider, text_request: AIRequest) -> None:
        assert isinstance(echo.execute(text_request), AIResponse)

    def test_execute_missing_prompt_key_defaults_to_empty(
        self, echo: EchoProvider, empty_request: AIRequest
    ) -> None:
        assert echo.execute(empty_request).output == ""

    def test_execute_preserves_whitespace(self, echo: EchoProvider) -> None:
        prompt = "  spaces   preserved  "
        req = AIRequest(
            task="text", execution_context=None,
            payload={"prompt": prompt}, metadata={},
        )
        assert echo.execute(req).output == prompt

    def test_execute_preserves_newlines(self, echo: EchoProvider) -> None:
        prompt = "line one\nline two"
        req = AIRequest(
            task="text", execution_context=None,
            payload={"prompt": prompt}, metadata={},
        )
        assert echo.execute(req).output == prompt

    def test_execute_is_deterministic(self, echo: EchoProvider, text_request: AIRequest) -> None:
        assert echo.execute(text_request) == echo.execute(text_request)

    def test_different_prompts_produce_different_outputs(self, echo: EchoProvider) -> None:
        def run(prompt: str) -> str:
            req = AIRequest(
                task="text", execution_context=None,
                payload={"prompt": prompt}, metadata={},
            )
            return echo.execute(req).output  # type: ignore[return-value]

        assert run("A") == "A"
        assert run("B") == "B"
        assert run("A") != run("B")

    def test_metadata_is_immutable(self, echo: EchoProvider) -> None:
        with pytest.raises(FrozenInstanceError):
            echo.metadata.name = "changed"  # type: ignore[misc]

    def test_initialize_does_not_raise(self, echo: EchoProvider) -> None:
        echo.initialize()


# ===========================================================================
# Package exports (__init__.py)
# ===========================================================================


class TestPackageExports:
    def test_ai_provider_exported(self) -> None:
        import intelligence.providers as pkg
        assert pkg.AIProvider is AIProvider

    def test_ai_request_exported(self) -> None:
        import intelligence.providers as pkg
        assert pkg.AIRequest is AIRequest

    def test_ai_response_exported(self) -> None:
        import intelligence.providers as pkg
        assert pkg.AIResponse is AIResponse

    def test_provider_capabilities_exported(self) -> None:
        import intelligence.providers as pkg
        assert pkg.ProviderCapabilities is ProviderCapabilities

    def test_provider_metadata_exported(self) -> None:
        import intelligence.providers as pkg
        assert pkg.ProviderMetadata is ProviderMetadata

    def test_health_status_exported(self) -> None:
        import intelligence.providers as pkg
        assert pkg.HealthStatus is HealthStatus

    def test_dummy_provider_exported(self) -> None:
        import intelligence.providers as pkg
        assert pkg.DummyProvider is DummyProvider

    def test_mock_provider_exported(self) -> None:
        import intelligence.providers as pkg
        assert pkg.MockProvider is MockProvider

    def test_mock_scenario_exported(self) -> None:
        import intelligence.providers as pkg
        assert pkg.MockScenario is MockScenario

    def test_echo_provider_exported(self) -> None:
        import intelligence.providers as pkg
        assert pkg.EchoProvider is EchoProvider

    def test_provider_registry_exported(self) -> None:
        import intelligence.providers as pkg
        assert pkg.ProviderRegistry is ProviderRegistry

    def test_register_provider_exported(self) -> None:
        import intelligence.providers as pkg
        assert callable(pkg.register_provider)

    def test_all_list_contains_expected_names(self) -> None:
        import intelligence.providers as pkg
        expected = {
            "AIProvider", "AIRequest", "AIResponse",
            "ProviderCapabilities", "ProviderMetadata", "HealthStatus",
            "DummyProvider", "MockProvider", "MockScenario", "EchoProvider",
            "ProviderRegistry", "register_provider",
        }
        assert expected.issubset(set(pkg.__all__))
