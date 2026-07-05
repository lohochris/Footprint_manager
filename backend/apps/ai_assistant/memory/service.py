import uuid
from typing import cast, Literal
from backend.apps.ai_assistant.models import AssistantMessage
from backend.apps.ai_assistant.dto.ai_provider_dto import AIChatMessageDTO

class MemoryService:
    """Manages conversational history windows and summarization."""

    def get_session_history(self, session_id: str, max_messages: int = 10) -> list[AIChatMessageDTO]:
        """Fetch the last N messages from a session."""
        messages = AssistantMessage.objects.filter(session_id=uuid.UUID(str(session_id))).order_by("-created_at")[:max_messages]
        # Reverse to get chronological order
        chronological_messages = list(reversed(messages))

        return [
            AIChatMessageDTO(role=cast(Literal["user", "assistant", "system"], m.role), content=str(m.content))
            for m in chronological_messages
        ]
