import abc
from backend.apps.ai_assistant.dto.rag_dto import RAGContextDTO

class IRAGRetriever(abc.ABC):
    """Interface for retrieving context from a specific bounded context."""

    @abc.abstractmethod
    def retrieve(self, tenant_id: str, workspace_id: str | None, query: str) -> RAGContextDTO:
        """Retrieve relevant context for a given query."""
        pass
