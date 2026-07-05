from typing import Any, List

from backend.apps.graph.dtos import NodeDTO, EdgeDTO
from backend.apps.intelligence.dto.analytics import AnalyticsResultDTO
from backend.apps.intelligence.dto.risk import RiskAssessmentDTO
from backend.apps.intelligence.dto.recommendation import RecommendationResultDTO
from backend.apps.intelligence.services.recommendation_strategies import (
    IRecommendationStrategy,
    IsolatedEntityStrategy,
    HighCentralityStrategy,
    SuspiciousClusterStrategy,
    MissingEvidenceStrategy,
)

class RecommendationService:
    """Generates actionable recommendations based on analytics and risk scores."""

    def __init__(self, strategies: List[IRecommendationStrategy] | None = None) -> None:
        self.strategies = strategies or [
            IsolatedEntityStrategy(),
            HighCentralityStrategy(),
            SuspiciousClusterStrategy(),
            MissingEvidenceStrategy(),
        ]

    def generate_recommendations(
        self,
        tenant_id: str,
        workspace_id: str | None,
        nodes: list[NodeDTO],
        edges: list[EdgeDTO],
        analytics: AnalyticsResultDTO,
        risk: RiskAssessmentDTO,
        context: dict[str, Any],
    ) -> RecommendationResultDTO:
        recs = []
        for strategy in self.strategies:
            recs.extend(
                strategy.generate(
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    nodes=nodes,
                    edges=edges,
                    analytics=analytics,
                    risk=risk,
                    context=context,
                )
            )

        return RecommendationResultDTO(recommendations=recs)
