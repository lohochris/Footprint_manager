from backend.apps.ai_assistant.rag.interfaces import IRAGRetriever
from backend.apps.ai_assistant.dto.rag_dto import RAGContextDTO, RAGSourceDTO

class EvidenceRetriever(IRAGRetriever):
    """Retrieves document summaries and text extracts from the Evidence domain."""

    def retrieve(self, tenant_id: str, workspace_id: str | None, query: str) -> RAGContextDTO:
        # Pseudo-implementation interacting with EvidenceService
        sources = [
            RAGSourceDTO(
                source_type="evidence",
                source_id="mock-evid-123",
                content="This is a mock evidence extract matching the query.",
                relevance_score=0.85
            )
        ]
        return RAGContextDTO(query=query, sources=sources)

class GraphRetriever(IRAGRetriever):
    """Retrieves nodes, edges, and risk scores from the Graph Intelligence domain."""

    def retrieve(self, tenant_id: str, workspace_id: str | None, query: str) -> RAGContextDTO:
        # Pseudo-implementation interacting with IntelligenceEngine / GraphService
        sources = [
            RAGSourceDTO(
                source_type="graph_node",
                source_id="mock-node-456",
                content="Mock Graph Node showing connection between Entity A and Entity B.",
                relevance_score=0.9
            )
        ]
        return RAGContextDTO(query=query, sources=sources)

class OSINTRetriever(IRAGRetriever):
    """Retrieves discovered identifiers from the OSINT domain."""

    def retrieve(self, tenant_id: str, workspace_id: str | None, query: str) -> RAGContextDTO:
        # Pseudo-implementation interacting with OSINTService
        sources = [
            RAGSourceDTO(
                source_type="osint_identifier",
                source_id="mock-osint-789",
                content="Mock OSINT finding: email test@example.com linked to target.",
                relevance_score=0.75
            )
        ]
        return RAGContextDTO(query=query, sources=sources)
