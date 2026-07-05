from dataclasses import dataclass, field
from typing import Literal

@dataclass
class AIChatMessageDTO:
    """Represents a single message in a conversation."""
    role: Literal["user", "assistant", "system"]
    content: str

@dataclass
class AICompletionRequestDTO:
    """Standardized request for AI providers."""
    messages: list[AIChatMessageDTO]
    model: str
    tenant_id: str
    workspace_id: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None
    stream: bool = False

@dataclass
class AICompletionResponseDTO:
    """Standardized response from AI providers."""
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_cost: float
    model_used: str

@dataclass
class AIStreamChunkDTO:
    """Standardized chunk for streaming AI responses."""
    content_delta: str
    is_finished: bool
