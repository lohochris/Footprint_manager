from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class RuleDTO:
    id: str | None
    name: str
    description: str
    conditions: dict[str, Any]
    expression: str
    evaluation_order: int
    is_active: bool


@dataclass(frozen=True)
class PolicyDTO:
    id: str | None
    name: str
    description: str
    version: int
    status: str
    scope: str
    priority: int
    rules: list[RuleDTO] = field(default_factory=list)


@dataclass(frozen=True)
class DecisionDTO:
    id: str | None
    result: str
    confidence: float
    reasoning: str
    related_entity_id: str | None
    related_entity_type: str
    trace_identifier: str
    created_at: datetime | None = None


@dataclass(frozen=True)
class RecommendationDTO:
    id: str | None
    decision_id: str
    action_type: str
    action_payload: dict[str, Any]
    status: str
    reasoning: str


@dataclass(frozen=True)
class EvaluationInputDTO:
    tenant_id: str
    event_type: str
    payload: dict[str, Any]
    trace_identifier: str


@dataclass(frozen=True)
class EvaluationResultDTO:
    decision: DecisionDTO
    recommendations: list[RecommendationDTO] = field(default_factory=list)
    matched_rule_ids: list[str] = field(default_factory=list)
    applied_policy_ids: list[str] = field(default_factory=list)


__all__ = [
    "RuleDTO",
    "PolicyDTO",
    "DecisionDTO",
    "RecommendationDTO",
    "EvaluationInputDTO",
    "EvaluationResultDTO",
]
