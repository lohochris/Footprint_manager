from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any
from .analytics import AnalyticsResultDTO

@dataclass(frozen=True)
class RiskFactorDTO:
    factor_type: str
    weight_applied: Decimal
    description: str

@dataclass(frozen=True)
class EntityRiskDTO:
    node_id: str
    risk_score: Decimal
    confidence_score: Decimal
    factors: list[RiskFactorDTO] = field(default_factory=list)
    explanation: dict[str, Any] = field(default_factory=dict)
    score_version: str = "1.0.0"

@dataclass(frozen=True)
class RiskAssessmentDTO:
    tenant_id: str
    workspace_id: str | None = None
    investigation_id: str | None = None
    aggregate_risk_score: Decimal = Decimal("0.0000")
    flagged_entities_count: int = 0
    entity_risks: dict[str, EntityRiskDTO] = field(default_factory=dict)
