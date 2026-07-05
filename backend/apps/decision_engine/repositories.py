from typing import Any

from django.db import transaction

from backend.apps.decision_engine.dto import PolicyDTO, RuleDTO
from backend.apps.decision_engine.models.decision import Decision, DecisionAudit
from backend.apps.decision_engine.models.policy import Policy, PolicyVersion
from backend.apps.decision_engine.models.recommendation import Recommendation
from backend.apps.decision_engine.models.rule import Rule


class PolicyRepository:
    def get_active_policies_by_scope(self, tenant_id: str, scope: str) -> list[Policy]:
        return list(
            Policy.objects.filter(
                tenant_id=tenant_id,
                scope=scope,
                status="ACTIVE",
            ).prefetch_related("rules")
        )

    def get_policy(self, tenant_id: str, policy_id: str) -> Policy | None:
        return Policy.objects.filter(tenant_id=tenant_id, id=policy_id).first()

    @transaction.atomic
    def save_policy_version(
        self, tenant_id: str, policy: Policy, schema_payload: dict[str, Any], published_by_id: str | None = None
    ) -> PolicyVersion:
        version_number = policy.version + 1
        policy.version = version_number
        policy.save(update_fields=["version", "updated_at"])

        return PolicyVersion.objects.create(
            tenant_id=tenant_id,
            policy=policy,
            version_number=version_number,
            schema_payload=schema_payload,
            published_by_id=published_by_id,
        )


class RuleRepository:
    def get_rules_for_policy(self, tenant_id: str, policy_id: str) -> list[Rule]:
        return list(
            Rule.objects.filter(
                tenant_id=tenant_id,
                policy_id=policy_id,
                is_active=True,
            ).order_by("evaluation_order")
        )


class DecisionRepository:
    def create_decision(
        self,
        tenant_id: str,
        result: str,
        confidence: float,
        reasoning: str,
        trace_identifier: str,
        related_entity_id: str | None = None,
        related_entity_type: str = "",
    ) -> Decision:
        return Decision.objects.create(
            tenant_id=tenant_id,
            result=result,
            confidence=confidence,
            reasoning=reasoning,
            trace_identifier=trace_identifier,
            related_entity_id=related_entity_id,
            related_entity_type=related_entity_type,
        )


class RecommendationRepository:
    def create_recommendation(
        self,
        tenant_id: str,
        decision_id: str,
        action_type: str,
        action_payload: dict[str, Any],
        reasoning: str,
    ) -> Recommendation:
        return Recommendation.objects.create(
            tenant_id=tenant_id,
            decision_id=decision_id,
            action_type=action_type,
            action_payload=action_payload,
            reasoning=reasoning,
            status="PENDING",
        )


class AuditRepository:
    def create_audit(
        self,
        tenant_id: str,
        decision_id: str | None,
        evaluated_inputs: dict[str, Any],
        rules_matched: list[str],
        policies_applied: list[str],
        recommendations_generated: list[str],
        actor_id: str | None = None,
    ) -> DecisionAudit:
        return DecisionAudit.objects.create(
            tenant_id=tenant_id,
            decision_id=decision_id,
            evaluated_inputs=evaluated_inputs,
            rules_matched=rules_matched,
            policies_applied=policies_applied,
            recommendations_generated=recommendations_generated,
            actor_id=actor_id,
        )
