# backend/intelligence/providers/echo_provider.py
"""EchoProvider – deterministic offline debug provider.

Returns the incoming prompt from ``request.payload["prompt"]`` unchanged.
Validates the provider execution pipeline without performing any AI processing.
"""

from __future__ import annotations

from .base import AIProvider
from .provider_metadata import HealthStatus, ProviderCapabilities, ProviderMetadata
from .registry import register_provider
from .request import AIRequest
from .response import AIResponse

_METADATA = ProviderMetadata(
    name="echo",
    version="1.0.0",
    description="Offline provider that echoes the incoming prompt for debugging.",
    capabilities=ProviderCapabilities(
        supports_text=True,
        supports_chat=False,
        supports_structured_output=False,
        supports_streaming=False,
        supports_embeddings=False,
    ),
)


class EchoProvider(AIProvider):
    """Debug provider that echoes the incoming prompt back unchanged.

    - No AI processing.
    - No transformations.
    - No randomness.
    - No external I/O.
    - ``execute()`` output equals ``request.payload.get("prompt", "")``.
    """

    name: str = _METADATA.name
    version: str = _METADATA.version
    description: str = _METADATA.description
    metadata: ProviderMetadata = _METADATA

    def initialize(self) -> None:
        return

    def health_check(self) -> HealthStatus:
        return HealthStatus(
            healthy=True,
            message="Echo provider is healthy.",
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

    def execute(self, request: AIRequest) -> AIResponse:
        prompt = request.payload.get("prompt", "")
        return AIResponse(
            status="success",
            provider=self.name,
            metadata={"provider_version": self.version},
            usage={},
            output=prompt,
            diagnostics=None,
        )


# Register the provider in the global registry.
register_provider(EchoProvider)
