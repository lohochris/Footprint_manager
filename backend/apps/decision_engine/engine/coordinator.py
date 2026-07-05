import logging
from typing import Any

from backend.apps.decision_engine.dto import (
    DecisionDTO,
    EvaluationInputDTO,
    EvaluationResultDTO,
    RecommendationDTO,
)
from backend.apps.decision_engine.providers.base import BaseDecisionProvider, BaseRuleProvider
from backend.apps.decision_engine.providers.internal import InternalDecisionProvider, InternalRuleProvider
from backend.apps.decision_engine.repositories import PolicyRepository, RuleRepository

logger = logging.getLogger(__name__)


class DecisionEngineCoordinator:
    """Coordinates policy evaluation, delegates to providers, and generates results."""

    def __init__(
        self,
        policy_repository: PolicyRepository | None = None,
        rule_repository: RuleRepository | None = None,
        rule_provider: BaseRuleProvider | None = None,
        decision_provider: BaseDecisionProvider | None = None,
    ):
        self.policy_repository = policy_repository or PolicyRepository()
        self.rule_repository = rule_repository or RuleRepository()
        self.rule_provider = rule_provider or InternalRuleProvider()
        self.decision_provider = decision_provider or InternalDecisionProvider()

    def evaluate(self, input_data: EvaluationInputDTO) -> EvaluationResultDTO:
        logger.info(f"Starting evaluation for {input_data.trace_identifier}")

        policies = self.policy_repository.get_active_policies_by_scope(
            tenant_id=input_data.tenant_id,
            scope=input_data.event_type,
        )

        matched_rules = []
        applied_policy_ids = []
        highest_priority = -1
        decision_result = "UNDETERMINED"
        confidence = 1.0

        for policy in sorted(policies, key=lambda p: p.priority, reverse=True):
            rules = self.rule_repository.get_rules_for_policy(input_data.tenant_id, str(policy.id))
            policy_matched = False

            for rule in rules:
                rule_dto = rule  # In a real app we'd map this, assuming rule_provider accepts model or we map it
                # Convert model to DTO for provider
                rule_dto_obj = self._map_rule_to_dto(rule)
                is_match = self.rule_provider.evaluate_rule(rule_dto_obj, input_data)

                if is_match:
                    matched_rules.append(rule_dto_obj)
                    policy_matched = True

                    # Basic conflict resolution: Highest priority policy dictates result
                    if policy.priority > highest_priority:
                        highest_priority = policy.priority
                        # Assume rule condition defines 'decision_result' or we default to ESCALATED
                        decision_result = rule.conditions.get("decision_result", "ESCALATED")
                        confidence = rule.conditions.get("confidence", 0.9)

            if policy_matched:
                applied_policy_ids.append(str(policy.id))

        recommendations_dicts = self.decision_provider.generate_recommendations(matched_rules, input_data)
        recommendations = [
            RecommendationDTO(
                id=None,
                decision_id="",  # Will be populated after persistence
                action_type=rec["action_type"],
                action_payload=rec["action_payload"],
                status="PENDING",
                reasoning=rec["reasoning"],
            )
            for rec in recommendations_dicts
        ]

        decision_dto = DecisionDTO(
            id=None,
            result=decision_result,
            confidence=confidence,
            reasoning=f"Evaluated {len(policies)} policies, matched {len(matched_rules)} rules.",
            related_entity_id=input_data.payload.get("entity_id"),
            related_entity_type=input_data.payload.get("entity_type", ""),
            trace_identifier=input_data.trace_identifier,
        )

        return EvaluationResultDTO(
            decision=decision_dto,
            recommendations=recommendations,
            matched_rule_ids=[str(r.id) for r in matched_rules],
            applied_policy_ids=applied_policy_ids,
        )

    def _map_rule_to_dto(self, rule: Any) -> Any:
        from backend.apps.decision_engine.dto import RuleDTO

        return RuleDTO(
            id=str(rule.id),
            name=rule.name,
            description=rule.description,
            conditions=rule.conditions,
            expression=rule.expression,
            evaluation_order=rule.evaluation_order,
            is_active=rule.is_active,
        )
