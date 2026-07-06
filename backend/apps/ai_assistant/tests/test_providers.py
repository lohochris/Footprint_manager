import pytest
from backend.apps.ai_assistant.providers.mock_provider import MockAIProvider
from backend.apps.ai_assistant.providers.openai_provider import OpenAIProvider
from backend.apps.ai_assistant.providers.factory import AIProviderFactory
from backend.apps.ai_assistant.dto.ai_provider_dto import AICompletionRequestDTO, AIChatMessageDTO

def test_mock_provider():
    provider = MockAIProvider()
    req = AICompletionRequestDTO(
        messages=[AIChatMessageDTO(role="user", content="Hello")],
        model="mock-model",
        tenant_id="test",
    )
    res = provider.generate_completion(req)
    assert "mock response" in res.content.lower()
    assert res.model_used == "mock-model"
    assert res.prompt_tokens > 0
    assert res.completion_tokens > 0

def test_openai_provider_stub():
    provider = OpenAIProvider()
    req = AICompletionRequestDTO(
        messages=[AIChatMessageDTO(role="user", content="Hello")],
        model="gpt-4",
        tenant_id="test",
    )
    res = provider.generate_completion(req)
    assert res.content == "[OpenAI Stub] Received 1 messages. Returning canned response."
    assert res.model_used == "gpt-4"

def test_provider_factory():
    provider = AIProviderFactory.get_provider("mock")
    assert isinstance(provider, MockAIProvider)

    provider = AIProviderFactory.get_provider("openai")
    assert isinstance(provider, OpenAIProvider)
