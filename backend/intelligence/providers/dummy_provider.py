# backend/intelligence/providers/dummy_provider.py
"""DummyProvider – deterministic offline provider for testing the execution lifecycle.

Provides a static successful response without any external dependencies.
"""

from dataclasses import dataclass
from typing import List, Dict, Any

from .base import AIProvider
from .request import AIRequest
from .response import AIResponse
from .registry import register_provider


@dataclass(frozen=True)
class ProviderMeta:
    name: str = "dummy"
    version: str = "1.0.0"
    description: str = "Offline dummy provider for validation of the execution pipeline."
    capabilities: List[str] = ("text", "chat")


class DummyProvider(AIProvider):
    """Concrete implementation of AIProvider that always succeeds.

    - Always available, healthy, and configured.
    - Supports text and chat capabilities only.
    - Returns a deterministic AIResponse.
    """

    name = ProviderMeta.name
    version = ProviderMeta.version
    description = ProviderMeta.description
    _capabilities = ProviderMeta.capabilities

    def initialize(self) -> None:
        # No initialization needed for dummy provider.
        return

    def health_check(self) -> Dict[str, Any]:
        return {
            "available": True,
            "configured": True,
            "enabled": True,
            "version": self.version,
            "status": "healthy",
        }

    def capabilities(self) -> List[str]:
        return list(self._capabilities)

    # Capability helpers
    def supports_text(self) -> bool:
        return "text" in self._capabilities

    def supports_chat(self) -> bool:
        return "chat" in self._capabilities

    def supports_structured_output(self) -> bool:
        return "structured_output" in self._capabilities

    def supports_streaming(self) -> bool:
        return "streaming" in self._capabilities

    def supports_embeddings(self) -> bool:
        return "embeddings" in self._capabilities

    def supports(self, task: str) -> bool:
        # Generic support check based on capability name.
        return task in self._capabilities

    def execute(self, request: AIRequest) -> AIResponse:
        # Return a fixed successful response.
        return AIResponse(
            status="success",
            provider=self.name,
            metadata={"provider_version": self.version},
            usage={},
            output="Dummy provider executed successfully.",
            diagnostics=None,
        )

# Register the provider in the global registry.
register_provider(DummyProvider)
