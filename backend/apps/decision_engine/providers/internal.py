from typing import Any

from backend.apps.decision_engine.dto import EvaluationInputDTO, RuleDTO
from backend.apps.decision_engine.providers.base import BaseDecisionProvider, BaseRuleProvider


class InternalRuleProvider(BaseRuleProvider):
    """Evaluates rules using a built-in JSON condition structure."""

    def evaluate_rule(self, rule: RuleDTO, input_data: EvaluationInputDTO) -> bool:
        if not rule.conditions:
            return False

        # MVP implementation: AND logic for all conditions
        for condition in rule.conditions.get("allOf", []):
            field = condition.get("field")
            operator = condition.get("operator")
            expected_value = condition.get("value")

            actual_value = self._get_nested_value(input_data.payload, field)

            if not self._evaluate_condition(actual_value, operator, expected_value):
                return False

        return True

    def _get_nested_value(self, payload: dict[str, Any], path: str) -> Any:
        keys = path.split(".")
        val = payload
        for key in keys:
            if isinstance(val, dict) and key in val:
                val = val[key]
            else:
                return None
        return val

    def _evaluate_condition(self, actual: Any, operator: str, expected: Any) -> bool:
        if operator == "==":
            return actual == expected
        elif operator == "!=":
            return actual != expected
        elif operator == ">" and actual is not None and expected is not None:
            return actual > expected
        elif operator == "<" and actual is not None and expected is not None:
            return actual < expected
        elif operator == ">=" and actual is not None and expected is not None:
            return actual >= expected
        elif operator == "<=" and actual is not None and expected is not None:
            return actual <= expected
        elif operator == "IN" and isinstance(expected, list):
            return actual in expected
        return False


class InternalDecisionProvider(BaseDecisionProvider):
    """Generates recommendations based on the matched rule definitions."""

    def generate_recommendations(self, matched_rules: list[RuleDTO], input_data: EvaluationInputDTO) -> list[dict[str, Any]]:
        recommendations = []
        for rule in matched_rules:
            # Assuming rules define actions in a custom field or we map them.
            # For this MVP, if a rule has an "actions" list in its conditions dict, we extract it.
            actions = rule.conditions.get("actions", [])
            for action in actions:
                recommendations.append(
                    {
                        "action_type": action.get("type", "UNKNOWN"),
                        "action_payload": action.get("payload", {}),
                        "reasoning": f"Matched rule: {rule.name}",
                    }
                )
        return recommendations
