from dataclasses import dataclass, field

@dataclass(frozen=True)
class RecommendationDTO:
    tenant_id: str
    workspace_id: str | None
    recommendation_type: str
    severity: str
    reasoning: str
    target_node_id: str | None = None
    status: str = "open"

@dataclass(frozen=True)
class RecommendationResultDTO:
    recommendations: list[RecommendationDTO] = field(default_factory=list)
