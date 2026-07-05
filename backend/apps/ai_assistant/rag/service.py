from backend.apps.ai_assistant.dto.rag_dto import RAGContextDTO
from backend.apps.ai_assistant.rag.interfaces import IRAGRetriever

class RAGService:
    """
    Orchestrates context retrieval across multiple bounded contexts
    (e.g., Evidence, Graph, OSINT) to build a unified RAG context.
    """

    def __init__(self, retrievers: list[IRAGRetriever] | None = None) -> None:
        self.retrievers = retrievers or []

    def get_context(self, tenant_id: str, workspace_id: str | None, query: str) -> RAGContextDTO:
        """Fetch and aggregate context from all registered retrievers."""
        all_sources = []

        for retriever in self.retrievers:
            context = retriever.retrieve(tenant_id, workspace_id, query)
            all_sources.extend(context.sources)

        # In a full implementation, we might rank or prune sources here.
        all_sources.sort(key=lambda s: s.relevance_score, reverse=True)

        return RAGContextDTO(
            query=query,
            sources=all_sources
        )
