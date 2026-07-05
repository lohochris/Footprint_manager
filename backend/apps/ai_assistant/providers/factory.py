from backend.apps.ai_assistant.providers.base import IAIProvider
from backend.apps.ai_assistant.providers.mock_provider import MockAIProvider
from backend.apps.ai_assistant.providers.openai_provider import OpenAIProvider
from django.conf import settings

class AIProviderFactory:
    """Factory to retrieve the appropriate AI provider."""

    @staticmethod
    def get_provider(provider_name: str | None = None) -> IAIProvider:
        """
        Returns the configured provider.
        In production, this would read from Django settings or a feature flag.
        """
        name = provider_name or getattr(settings, "DEFAULT_AI_PROVIDER", "mock")

        if name == "openai":
            return OpenAIProvider()

        # Default fallback
        return MockAIProvider()
