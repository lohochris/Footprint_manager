from typing import Iterator
from backend.apps.ai_assistant.providers.base import IAIProvider
from backend.apps.ai_assistant.dto.ai_provider_dto import (
    AICompletionRequestDTO,
    AICompletionResponseDTO,
    AIStreamChunkDTO,
)

class MockAIProvider(IAIProvider):
    """A mock provider for testing and local development without incurring costs."""

    def generate_completion(self, request: AICompletionRequestDTO) -> AICompletionResponseDTO:
        response_content = "This is a mocked response from the MockAIProvider."
        return AICompletionResponseDTO(
            content=response_content,
            prompt_tokens=10,
            completion_tokens=15,
            total_cost=0.0,
            model_used=request.model or "mock-model",
        )

    def generate_stream(self, request: AICompletionRequestDTO) -> Iterator[AIStreamChunkDTO]:
        words = ["This", " is", " a", " mocked", " stream."]
        for i, word in enumerate(words):
            yield AIStreamChunkDTO(
                content_delta=word,
                is_finished=(i == len(words) - 1),
            )
