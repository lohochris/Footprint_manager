from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class NodeDTO:
    id: str
    tenant_id: str
    workspace_id: str | None
    node_type: str
    label: str
    metadata: dict[str, Any] = field(default_factory=dict)
    confidence: Decimal = Decimal("1.000")
    created_at: str | None = None
    updated_at: str | None = None


@dataclass(frozen=True)
class EdgeDTO:
    id: str
    tenant_id: str
    source_id: str
    target_id: str
    relationship_type: str
    direction: str = "directed"
    confidence: Decimal = Decimal("1.000")
    provenance: str = "system"
    evidence_references: list[str] = field(default_factory=list)
    investigation_references: list[str] = field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None


@dataclass(frozen=True)
class TraversalResultDTO:
    visited_nodes: list[NodeDTO]
    visited_edges: list[EdgeDTO]
    depth: int
    statistics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphStatsDTO:
    node_count: int
    edge_count: int
    density: Decimal
    average_degree: Decimal
    isolated_nodes: int
    largest_component_size: int
