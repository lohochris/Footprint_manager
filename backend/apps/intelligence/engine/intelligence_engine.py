from typing import Any

from backend.apps.graph.dtos import EdgeDTO, NodeDTO
from backend.apps.intelligence.dto.analytics import AnalyticsResultDTO
from backend.apps.intelligence.dto.risk import RiskAssessmentDTO
from backend.apps.intelligence.dto.recommendation import RecommendationResultDTO
from backend.apps.intelligence.services.analytics import AnalyticsService
from backend.apps.intelligence.services.risk import RiskService
from backend.apps.intelligence.services.recommendation import RecommendationService

class IntelligenceEngine:
    """Orchestrates analytics, risk scoring, and recommendation generation."""

    def __init__(
        self,
        analytics_service: AnalyticsService | None = None,
        risk_service: RiskService | None = None,
        recommendation_service: RecommendationService | None = None,
    ) -> None:
        self.analytics_service = analytics_service or AnalyticsService()
        self.risk_service = risk_service or RiskService()
        self.recommendation_service = recommendation_service or RecommendationService()

    def process_graph(
        self,
        tenant_id: str,
        workspace_id: str | None,
        nodes: list[NodeDTO],
        edges: list[EdgeDTO],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Runs the full intelligence pipeline on the provided graph."""

        ctx = context or {}

        # 1. Compute Analytics
        analytics = self.analytics_service.analyze_graph(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            nodes=nodes,
            edges=edges,
        )

        # 2. Score Risk
        risk = self.risk_service.assess_risk(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            nodes=nodes,
            analytics=analytics,
            context=ctx,
        )

        # 3. Generate Recommendations
        recommendations = self.recommendation_service.generate_recommendations(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            nodes=nodes,
            edges=edges,
            analytics=analytics,
            risk=risk,
            context=ctx,
        )

        return {
            "analytics": analytics,
            "risk": risk,
            "recommendations": recommendations,
        }
