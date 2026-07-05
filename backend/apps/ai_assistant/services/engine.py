from backend.apps.ai_assistant.providers.factory import AIProviderFactory
from backend.apps.ai_assistant.rag.service import RAGService
from backend.apps.ai_assistant.prompts.service import PromptService
from backend.apps.ai_assistant.memory.service import MemoryService
from backend.apps.ai_assistant.models import AssistantSession, AssistantMessage, AIInteractionLog
from backend.apps.ai_assistant.dto.ai_provider_dto import AICompletionRequestDTO, AIChatMessageDTO
import uuid

class AIIntelligenceEngine:
    """
    Facade orchestrating the entire AI pipeline:
    User Message -> RAG Context -> Prompt Assembly -> LLM Invocation -> Persistence.
    """

    def __init__(
        self,
        rag_service: RAGService | None = None,
        prompt_service: PromptService | None = None,
        memory_service: MemoryService | None = None,
    ) -> None:
        self.rag_service = rag_service or RAGService()
        self.prompt_service = prompt_service or PromptService()
        self.memory_service = memory_service or MemoryService()

    def chat(self, session_id: str, user_message: str, user_id: str | None = None) -> str:
        """Process a single conversational turn."""
        session = AssistantSession.objects.get(id=session_id)

        # 1. Fetch RAG Context
        rag_context = self.rag_service.get_context(
            tenant_id=str(session.tenant_id),
            workspace_id=str(session.workspace_id) if session.workspace_id else None,
            query=user_message,
        )

        # 2. Assemble System Prompt
        system_prompt_text = self.prompt_service.assemble(
            tenant_id=str(session.tenant_id),
            template_name="default_chat",
            template_version="v1",
            rag_context=rag_context,
        )
        system_message = AIChatMessageDTO(role="system", content=system_prompt_text)

        # 3. Retrieve Memory
        history = self.memory_service.get_session_history(session_id=session_id)

        # 4. Save the user's message
        AssistantMessage.objects.create(
            session=session,
            role="user",
            content=user_message,
        )
        new_user_message = AIChatMessageDTO(role="user", content=user_message)

        # 5. Build full payload
        messages = [system_message] + history + [new_user_message]
        request_dto = AICompletionRequestDTO(
            messages=messages,
            model="default-model",
            tenant_id=str(session.tenant_id),
            workspace_id=str(session.workspace_id) if session.workspace_id else None,
        )

        # 6. Call Provider
        provider = AIProviderFactory.get_provider()
        response_dto = provider.generate_completion(request_dto)

        # 7. Persistence & Logging
        AssistantMessage.objects.create(
            session=session,
            role="assistant",
            content=response_dto.content,
            tokens_used=response_dto.completion_tokens,
        )

        AIInteractionLog.objects.create(
            tenant_id=session.tenant_id,
            workspace_id=session.workspace_id,
            provider=provider.__class__.__name__,
            model=response_dto.model_used,
            prompt_tokens=response_dto.prompt_tokens,
            completion_tokens=response_dto.completion_tokens,
            cost=response_dto.total_cost,
            status="success",
        )

        return response_dto.content
