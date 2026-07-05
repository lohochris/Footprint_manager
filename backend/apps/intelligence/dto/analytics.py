from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

@dataclass(frozen=True)
class NodeCentralityDTO:
    node_id: str
    degree: Decimal = Decimal("0.0000")
    betweenness: Decimal = Decimal("0.0000")
    closeness: Decimal = Decimal("0.0000")

@dataclass(frozen=True)
class ComponentDTO:
    component_id: str
    node_ids: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class AnalyticsResultDTO:
    tenant_id: str
    workspace_id: str | None = None
    node_metrics: dict[str, NodeCentralityDTO] = field(default_factory=dict)
    components: list[ComponentDTO] = field(default_factory=list)
    statistics: dict[str, Any] = field(default_factory=dict)
