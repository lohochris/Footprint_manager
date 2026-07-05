import abc
from typing import Iterator
from backend.apps.ai_assistant.dto.ai_provider_dto import (
    AICompletionRequestDTO,
    AICompletionResponseDTO,
    AIStreamChunkDTO,
)

class IAIProvider(abc.ABC):
    """Abstract interface for all AI interactions."""

    @abc.abstractmethod
    def generate_completion(self, request: AICompletionRequestDTO) -> AICompletionResponseDTO:
        """Generate a complete, synchronous response."""
        pass

    @abc.abstractmethod
    def generate_stream(self, request: AICompletionRequestDTO) -> Iterator[AIStreamChunkDTO]:
        """Generate a streaming response chunk by chunk."""
        pass
