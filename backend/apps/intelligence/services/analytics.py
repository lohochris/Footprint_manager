from backend.apps.graph.dtos import EdgeDTO, NodeDTO
from backend.apps.intelligence.dto.analytics import AnalyticsResultDTO
from backend.apps.intelligence.providers.analytics import AnalyticsProvider

class AnalyticsService:
    """Service to feed graph topology into the provider and output facts."""

    def __init__(self, provider: AnalyticsProvider | None = None) -> None:
        self.provider = provider or AnalyticsProvider()

    def analyze_graph(
        self,
        tenant_id: str,
        workspace_id: str | None,
        nodes: list[NodeDTO],
        edges: list[EdgeDTO],
    ) -> AnalyticsResultDTO:
        """
        Compute pure graph analytics facts based on topology without
        risk interpretations.
        """
        return self.provider.calculate(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            nodes=nodes,
            edges=edges,
        )
