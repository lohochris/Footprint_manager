from decimal import Decimal
from typing import Any, List

from backend.apps.graph.dtos import NodeDTO
from backend.apps.intelligence.dto.analytics import AnalyticsResultDTO, NodeCentralityDTO
from backend.apps.intelligence.dto.risk import EntityRiskDTO, RiskAssessmentDTO, RiskFactorDTO
from backend.apps.intelligence.services.risk_strategies import (
    CentralityStrategy,
    ConfidenceStrategy,
    IRiskStrategy,
    WatchlistProximityStrategy,
)

class RiskService:
    """Aggregates strategy outputs into final entity risk assessments."""

    def __init__(self, strategies: List[IRiskStrategy] | None = None) -> None:
        self.strategies = strategies or [
            WatchlistProximityStrategy(),
            CentralityStrategy(),
            ConfidenceStrategy(),
        ]

    def assess_risk(
        self,
        tenant_id: str,
        workspace_id: str | None,
        nodes: list[NodeDTO],
        analytics: AnalyticsResultDTO,
        context: dict[str, Any],
    ) -> RiskAssessmentDTO:
        entity_risks = {}
        total_risk = Decimal("0.0000")
        flagged_count = 0

        for node in nodes:
            metrics = analytics.node_metrics.get(node.id, NodeCentralityDTO(node_id=node.id))

            factors = []
            for strategy in self.strategies:
                factors.extend(strategy.evaluate(node, metrics, analytics, context))

            baseline = Decimal("0.1000")
            risk_score = baseline
            for f in factors:
                risk_score += f.weight_applied

            risk_score = min(max(risk_score, Decimal("0.0000")), Decimal("1.0000"))

            explanation = {
                "final_score": float(risk_score),
                "baseline": float(baseline),
                "factors": [{"type": f.factor_type, "weight": float(f.weight_applied)} for f in factors],
            }

            if risk_score > Decimal("0.5000"):
                flagged_count += 1

            total_risk += risk_score

            entity_risks[node.id] = EntityRiskDTO(
                node_id=node.id,
                risk_score=risk_score,
                confidence_score=node.confidence,
                factors=factors,
                explanation=explanation,
                score_version="1.0.0",
            )

        aggregate_risk_score = total_risk / Decimal(str(len(nodes))) if nodes else Decimal("0.0000")

        return RiskAssessmentDTO(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            aggregate_risk_score=aggregate_risk_score,
            flagged_entities_count=flagged_count,
            entity_risks=entity_risks,
        )
