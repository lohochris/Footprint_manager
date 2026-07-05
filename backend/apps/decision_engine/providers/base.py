import abc
from typing import Any

from backend.apps.decision_engine.dto import EvaluationInputDTO, RuleDTO


class BaseRuleProvider(abc.ABC):
    """Abstract base class for rule evaluation engines."""

    @abc.abstractmethod
    def evaluate_rule(self, rule: RuleDTO, input_data: EvaluationInputDTO) -> bool:
        """Evaluate a single rule against the provided input data."""
        pass


class BaseDecisionProvider(abc.ABC):
    """Abstract base class for decision recommendation engines."""

    @abc.abstractmethod
    def generate_recommendations(self, matched_rules: list[RuleDTO], input_data: EvaluationInputDTO) -> list[dict[str, Any]]:
        """Generate a list of recommended actions based on matched rules."""
        pass
