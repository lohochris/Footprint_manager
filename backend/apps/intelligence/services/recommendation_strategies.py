import abc
from decimal import Decimal
from typing import Any, List

from backend.apps.graph.dtos import NodeDTO, EdgeDTO
from backend.apps.intelligence.dto.analytics import AnalyticsResultDTO, NodeCentralityDTO
from backend.apps.intelligence.dto.risk import RiskAssessmentDTO
from backend.apps.intelligence.dto.recommendation import RecommendationDTO
from backend.apps.intelligence.models.enums import RecommendationType, Severity

class IRecommendationStrategy(abc.ABC):
    """Defines deterministic recommendation strategies for insights."""

    @abc.abstractmethod
    def generate(
        self,
        tenant_id: str,
        workspace_id: str | None,
        nodes: list[NodeDTO],
        edges: list[EdgeDTO],
        analytics: AnalyticsResultDTO,
        risk: RiskAssessmentDTO,
        context: dict[str, Any],
    ) -> List[RecommendationDTO]:
        pass


class IsolatedEntityStrategy(IRecommendationStrategy):
    """Flags isolated entities that might require further investigation to link them."""

    def generate(
        self,
        tenant_id: str,
        workspace_id: str | None,
        nodes: list[NodeDTO],
        edges: list[EdgeDTO],
        analytics: AnalyticsResultDTO,
        risk: RiskAssessmentDTO,
        context: dict[str, Any],
    ) -> List[RecommendationDTO]:
        recs = []
        for node in nodes:
            metrics = analytics.node_metrics.get(node.id)
            if metrics and metrics.degree == Decimal("0.0000"):
                recs.append(
                    RecommendationDTO(
                        tenant_id=tenant_id,
                        workspace_id=workspace_id,
                        recommendation_type=RecommendationType.ISOLATED_ENTITY,
                        severity=Severity.LOW,
                        reasoning=f"Entity '{node.label}' is completely isolated in the graph. Consider expanding discovery.",
                        target_node_id=node.id,
                    )
                )
        return recs


class HighCentralityStrategy(IRecommendationStrategy):
    """Flags highly central entities as key figures in the investigation."""

    def generate(
        self,
        tenant_id: str,
        workspace_id: str | None,
        nodes: list[NodeDTO],
        edges: list[EdgeDTO],
        analytics: AnalyticsResultDTO,
        risk: RiskAssessmentDTO,
        context: dict[str, Any],
    ) -> List[RecommendationDTO]:
        recs = []
        for node in nodes:
            metrics = analytics.node_metrics.get(node.id)
            if metrics and metrics.degree > Decimal("0.8000"):
                recs.append(
                    RecommendationDTO(
                        tenant_id=tenant_id,
                        workspace_id=workspace_id,
                        recommendation_type=RecommendationType.HIGH_CENTRALITY,
                        severity=Severity.HIGH,
                        reasoning=f"Entity '{node.label}' acts as a major hub with extreme centrality.",
                        target_node_id=node.id,
                    )
                )
        return recs


class SuspiciousClusterStrategy(IRecommendationStrategy):
    """Flags completely connected components where risk is collectively high."""

    def generate(
        self,
        tenant_id: str,
        workspace_id: str | None,
        nodes: list[NodeDTO],
        edges: list[EdgeDTO],
        analytics: AnalyticsResultDTO,
        risk: RiskAssessmentDTO,
        context: dict[str, Any],
    ) -> List[RecommendationDTO]:
        recs = []
        for component in analytics.components:
            if len(component.node_ids) < 3:
                continue
            
            high_risk_count = 0
            for nid in component.node_ids:
                if nid in risk.entity_risks and risk.entity_risks[nid].risk_score > Decimal("0.6000"):
                    high_risk_count += 1
            
            if high_risk_count >= 2:
                recs.append(
                    RecommendationDTO(
                        tenant_id=tenant_id,
                        workspace_id=workspace_id,
                        recommendation_type=RecommendationType.SUSPICIOUS_CLUSTER,
                        severity=Severity.CRITICAL,
                        reasoning=f"Detected a dense cluster ({component.component_id}) containing multiple high-risk entities.",
                        target_node_id=None,
                    )
                )
        return recs


class MissingEvidenceStrategy(IRecommendationStrategy):
    """Flags high risk nodes that lack underlying evidence references."""

    def generate(
        self,
        tenant_id: str,
        workspace_id: str | None,
        nodes: list[NodeDTO],
        edges: list[EdgeDTO],
        analytics: AnalyticsResultDTO,
        risk: RiskAssessmentDTO,
        context: dict[str, Any],
    ) -> List[RecommendationDTO]:
        recs = []
        # In a real scenario, this would inspect node provenance or edge evidence references
        for node in nodes:
            entity_risk = risk.entity_risks.get(node.id)
            if entity_risk and entity_risk.risk_score > Decimal("0.7000"):
                # Simplistic check if evidence is missing
                # We assume metadata["evidence_ids"] exists for nodes.
                has_evidence = bool(node.metadata.get("evidence_ids", []))
                if not has_evidence:
                    recs.append(
                        RecommendationDTO(
                            tenant_id=tenant_id,
                            workspace_id=workspace_id,
                            recommendation_type=RecommendationType.MISSING_EVIDENCE,
                            severity=Severity.MEDIUM,
                            reasoning=f"Entity '{node.label}' has high risk but no directly linked evidence.",
                            target_node_id=node.id,
                        )
                    )
        return recs
