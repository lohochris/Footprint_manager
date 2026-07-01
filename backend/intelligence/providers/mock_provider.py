# backend/intelligence/providers/mock_provider.py
"""MockProvider – deterministic offline provider for testing AI execution flows.

Supports four explicit scenarios (success, failure, timeout,
unsupported_capability).  The scenario is configured at construction time;
no randomness or external I/O is used.
"""

from __future__ import annotations

from enum import StrEnum

from .base import AIProvider
from .provider_metadata import HealthStatus, ProviderCapabilities, ProviderMetadata
from .registry import register_provider
from .request import AIRequest
from .response import AIResponse


class MockScenario(StrEnum):
    """Explicit scenario selector for MockProvider."""

    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    UNSUPPORTED_CAPABILITY = "unsupported_capability"


_METADATA = ProviderMetadata(
    name="mock",
    version="1.0.0",
    description="Deterministic mock provider for testing AI execution flows.",
    capabilities=ProviderCapabilities(
        supports_text=True,
        supports_chat=True,
        supports_structured_output=True,
        supports_streaming=False,
        supports_embeddings=False,
    ),
)

# Pre-built deterministic responses keyed by scenario.
_RESPONSES: dict[MockScenario, AIResponse] = {
    MockScenario.SUCCESS: AIResponse(
        status="success",
        provider="mock",
        metadata={"provider_version": "1.0.0"},
        usage={},
        output="Mock provider executed successfully.",
        diagnostics=None,
    ),
    MockScenario.FAILURE: AIResponse(
        status="error",
        provider="mock",
        metadata={"provider_version": "1.0.0"},
        usage={},
        output=None,
        diagnostics={"error": "Mock provider simulated failure."},
    ),
    MockScenario.TIMEOUT: AIResponse(
        status="error",
        provider="mock",
        metadata={"provider_version": "1.0.0"},
        usage={},
        output=None,
        diagnostics={"error": "Mock provider simulated timeout."},
    ),
    MockScenario.UNSUPPORTED_CAPABILITY: AIResponse(
        status="error",
        provider="mock",
        metadata={"provider_version": "1.0.0"},
        usage={},
        output=None,
        diagnostics={"error": "Requested capability is not supported."},
    ),
}


class MockProvider(AIProvider):
    """Deterministic test provider for AI execution flow validation.

    The scenario governs what ``execute()`` returns; all behaviour is
    entirely offline and free of randomness.

    Parameters
    ----------
    scenario:
        One of the :class:`MockScenario` values.  Defaults to
        ``MockScenario.SUCCESS``.
    """

    name: str = _METADATA.name
    version: str = _METADATA.version
    description: str = _METADATA.description
    metadata: ProviderMetadata = _METADATA

    def __init__(self, scenario: MockScenario = MockScenario.SUCCESS) -> None:
        self._scenario = scenario

    def initialize(self) -> None:
        return

    def health_check(self) -> HealthStatus:
        return HealthStatus(
            healthy=True,
            message="Mock provider is healthy.",
        )

    def capabilities(self) -> list[str]:
        caps = self.metadata.capabilities
        result: list[str] = []
        if caps.supports_text:
            result.append("text")
        if caps.supports_chat:
            result.append("chat")
        if caps.supports_structured_output:
            result.append("structured_output")
        if caps.supports_streaming:
            result.append("streaming")
        if caps.supports_embeddings:
            result.append("embeddings")
        return result

    def supports(self, task: str) -> bool:
        return task in self.capabilities()

    def execute(self, request: AIRequest) -> AIResponse:  # noqa: ARG002
        return _RESPONSES[self._scenario]


# Register the provider in the global registry.
register_provider(MockProvider)
