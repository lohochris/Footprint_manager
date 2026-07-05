from backend.apps.decision_engine.dto import DecisionDTO, PolicyDTO, RecommendationDTO, RuleDTO
from backend.apps.decision_engine.models.decision import Decision
from backend.apps.decision_engine.models.policy import Policy
from backend.apps.decision_engine.models.recommendation import Recommendation


class PolicySelector:
    def get_policy_detail(self, tenant_id: str, policy_id: str) -> PolicyDTO | None:
        policy = Policy.objects.filter(tenant_id=tenant_id, id=policy_id).prefetch_related("rules").first()
        if not policy:
            return None

        rules = [
            RuleDTO(
                id=str(r.id),
                name=r.name,
                description=r.description,
                conditions=r.conditions,
                expression=r.expression,
                evaluation_order=r.evaluation_order,
                is_active=r.is_active,
            )
            for r in policy.rules.all()
        ]

        return PolicyDTO(
            id=str(policy.id),
            name=policy.name,
            description=policy.description,
            version=policy.version,
            status=policy.status,
            scope=policy.scope,
            priority=policy.priority,
            rules=rules,
        )

    def list_policies(self, tenant_id: str) -> list[PolicyDTO]:
        # Return summary policies
        policies = Policy.objects.filter(tenant_id=tenant_id).order_by("-updated_at")
        return [
            PolicyDTO(
                id=str(p.id),
                name=p.name,
                description=p.description,
                version=p.version,
                status=p.status,
                scope=p.scope,
                priority=p.priority,
                rules=[],
            )
            for p in policies
        ]


class DecisionSelector:
    def get_decision_detail(self, tenant_id: str, decision_id: str) -> DecisionDTO | None:
        decision = Decision.objects.filter(tenant_id=tenant_id, id=decision_id).first()
        if not decision:
            return None

        return DecisionDTO(
            id=str(decision.id),
            result=decision.result,
            confidence=decision.confidence,
            reasoning=decision.reasoning,
            related_entity_id=str(decision.related_entity_id) if decision.related_entity_id else None,
            related_entity_type=decision.related_entity_type,
            trace_identifier=decision.trace_identifier,
            created_at=decision.created_at,
        )


class RecommendationSelector:
    def list_recommendations_for_decision(self, tenant_id: str, decision_id: str) -> list[RecommendationDTO]:
        recs = Recommendation.objects.filter(tenant_id=tenant_id, decision_id=decision_id).order_by("created_at")
        return [
            RecommendationDTO(
                id=str(rec.id),
                decision_id=str(rec.decision_id),
                action_type=rec.action_type,
                action_payload=rec.action_payload,
                status=rec.status,
                reasoning=rec.reasoning,
            )
            for rec in recs
        ]
