import abc
from typing import List, Optional

from django.db import transaction

from backend.apps.intelligence.dto.risk import RiskAssessmentDTO
from backend.apps.intelligence.dto.recommendation import RecommendationResultDTO
from backend.apps.intelligence.models import (
    EntityScore,
    RiskFactor,
    IntelligenceRecommendation,
)


class IIntelligenceRepository(abc.ABC):
    @abc.abstractmethod
    def save_risk_assessment(self, risk: RiskAssessmentDTO, owner_id: str) -> None:
        pass

    @abc.abstractmethod
    def save_recommendations(self, result: RecommendationResultDTO, owner_id: str) -> None:
        pass


class IntelligenceRepository(IIntelligenceRepository):
    """Handles persistence of intelligence engine outputs."""

    @transaction.atomic
    def save_risk_assessment(self, risk: RiskAssessmentDTO, owner_id: str) -> None:
        # First, we could optionally clear old scores for these nodes, or just update.
        # For this sprint, we assume simple create/update loop.
        
        for node_id, entity_risk in risk.entity_risks.items():
            # Create or update EntityScore
            score_obj, _ = EntityScore.objects.update_or_create(
                tenant_id=risk.tenant_id,
                workspace_id=risk.workspace_id,
                node_id=node_id,
                defaults={
                    "risk_score": entity_risk.risk_score,
                    "confidence_score": entity_risk.confidence_score,
                    "explanation": entity_risk.explanation,
                    "score_version": entity_risk.score_version,
                    "owner_id": owner_id,
                }
            )

            # Clear old factors and recreate
            RiskFactor.objects.filter(entity_score=score_obj).delete()
            
            factors_to_create = []
            for f in entity_risk.factors:
                factors_to_create.append(
                    RiskFactor(
                        tenant_id=risk.tenant_id,
                        entity_score=score_obj,
                        factor_type=f.factor_type,
                        weight_applied=f.weight_applied,
                        description=f.description,
                        owner_id=owner_id,
                    )
                )
            if factors_to_create:
                RiskFactor.objects.bulk_create(factors_to_create)

    @transaction.atomic
    def save_recommendations(self, result: RecommendationResultDTO, owner_id: str) -> None:
        # For simplicity, append new open recommendations. In a real system, we'd dedup.
        recs_to_create = []
        for r in result.recommendations:
            recs_to_create.append(
                IntelligenceRecommendation(
                    tenant_id=r.tenant_id,
                    workspace_id=r.workspace_id,
                    target_node_id=r.target_node_id,
                    recommendation_type=r.recommendation_type,
                    severity=r.severity,
                    reasoning=r.reasoning,
                    status=r.status,
                    owner_id=owner_id,
                )
            )
        
        if recs_to_create:
            IntelligenceRecommendation.objects.bulk_create(recs_to_create)
