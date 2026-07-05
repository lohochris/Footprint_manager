import logging
from typing import Any

from django.db import transaction

from backend.apps.decision_engine.dto import EvaluationInputDTO, EvaluationResultDTO
from backend.apps.decision_engine.engine.coordinator import DecisionEngineCoordinator
from backend.apps.decision_engine.repositories import (
    AuditRepository,
    DecisionRepository,
    PolicyRepository,
    RecommendationRepository,
)

logger = logging.getLogger(__name__)


class DecisionService:
    def __init__(
        self,
        coordinator: DecisionEngineCoordinator | None = None,
        decision_repository: DecisionRepository | None = None,
        recommendation_repository: RecommendationRepository | None = None,
        audit_repository: AuditRepository | None = None,
    ):
        self.coordinator = coordinator or DecisionEngineCoordinator()
        self.decision_repository = decision_repository or DecisionRepository()
        self.recommendation_repository = recommendation_repository or RecommendationRepository()
        self.audit_repository = audit_repository or AuditRepository()

    @transaction.atomic
    def process_event(self, input_data: EvaluationInputDTO) -> EvaluationResultDTO:
        """
        Evaluate policies against the input data, persist the decision and recommendations,
        and write to the audit log.
        """
        logger.info(f"Processing event for trace: {input_data.trace_identifier}")

        # 1. Evaluate
        result_dto = self.coordinator.evaluate(input_data)

        # 2. Persist Decision
        decision = self.decision_repository.create_decision(
            tenant_id=input_data.tenant_id,
            result=result_dto.decision.result,
            confidence=result_dto.decision.confidence,
            reasoning=result_dto.decision.reasoning,
            trace_identifier=input_data.trace_identifier,
            related_entity_id=result_dto.decision.related_entity_id,
            related_entity_type=result_dto.decision.related_entity_type,
        )

        # 3. Persist Recommendations
        recs_created = []
        for rec_dto in result_dto.recommendations:
            rec = self.recommendation_repository.create_recommendation(
                tenant_id=input_data.tenant_id,
                decision_id=str(decision.id),
                action_type=rec_dto.action_type,
                action_payload=rec_dto.action_payload,
                reasoning=rec_dto.reasoning,
            )
            recs_created.append(str(rec.id))

        # 4. Audit
        self.audit_repository.create_audit(
            tenant_id=input_data.tenant_id,
            decision_id=str(decision.id),
            evaluated_inputs=input_data.payload,
            rules_matched=result_dto.matched_rule_ids,
            policies_applied=result_dto.applied_policy_ids,
            recommendations_generated=recs_created,
            actor_id=None,  # System generated via event
        )

        logger.info(f"Decision {decision.id} persisted for trace {input_data.trace_identifier}")

        # Note: If this system was actually triggering actions, we would emit a generic
        # `RecommendationGenerated` event here onto the Shared Domain Event Bus for the Orchestrator
        # to pick up. For Sprint 16, we just persist them for tracking and execution.

        return result_dto


class PolicyService:
    def __init__(self, policy_repository: PolicyRepository | None = None):
        self.policy_repository = policy_repository or PolicyRepository()

    def publish_policy(self, tenant_id: str, policy_id: str, actor_id: str) -> bool:
        """
        Snapshot the current rules and bump the policy version.
        """
        policy = self.policy_repository.get_policy(tenant_id, policy_id)
        if not policy:
            return False

        # In a real system, you'd serialize the rules into schema_payload
        schema_payload = {
            "rules": [
                {
                    "name": r.name,
                    "conditions": r.conditions,
                    "evaluation_order": r.evaluation_order,
                }
                for r in policy.rules.all()
            ]
        }

        self.policy_repository.save_policy_version(
            tenant_id=tenant_id,
            policy=policy,
            schema_payload=schema_payload,
            published_by_id=actor_id,
        )

        policy.status = "ACTIVE"
        policy.save(update_fields=["status"])

        return True
