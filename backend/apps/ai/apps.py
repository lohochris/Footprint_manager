"""
AI application for Footprint Manager.

Provides the architectural foundation for AI-assisted features including:
- Multi-provider LLM gateway
- Prompt management
- Embeddings generation
- Conversation memory
- Retrieval-Augmented Generation (RAG)
- Asynchronous AI Celery tasks

No concrete LLM provider is implemented in Sprint 0.1.
All modules define interfaces and data structures only.

Sub-modules
-----------
gateway       Unified AI gateway — routes requests to the appropriate provider.
providers     AIProvider protocol and provider registry.
prompts       PromptTemplate dataclass and template registry.
embeddings    EmbeddingBackend protocol.
memory        ConversationMemory protocol.
rag           RAGPipeline interface.
tasks         Celery task definitions for async AI workloads.
tests         Unit tests for this app.
"""

from django.apps import AppConfig


class AiConfig(AppConfig):
    """Django AppConfig for the AI app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.ai"
    verbose_name = "AI"

    def ready(self) -> None:
        """Validate AI sub-modules are importable at startup."""
        import backend.apps.ai.embeddings  # noqa: F401
        import backend.apps.ai.gateway  # noqa: F401
        import backend.apps.ai.memory  # noqa: F401
        import backend.apps.ai.prompts  # noqa: F401
        import backend.apps.ai.providers  # noqa: F401
        import backend.apps.ai.rag  # noqa: F401
        import backend.apps.ai.tasks  # noqa: F401
