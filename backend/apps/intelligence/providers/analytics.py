import abc
from decimal import Decimal
from typing import Dict, List, Tuple
import networkx as nx

from backend.apps.graph.dtos import EdgeDTO, NodeDTO
from backend.apps.intelligence.dto.analytics import (
    AnalyticsResultDTO,
    ComponentDTO,
    NodeCentralityDTO,
)

class IAnalyticsCalculator(abc.ABC):
    """Defines signatures for calculating specific topology facts."""

    @abc.abstractmethod
    def calculate(
        self,
        tenant_id: str,
        workspace_id: str | None,
        nodes: list[NodeDTO],
        edges: list[EdgeDTO],
    ) -> AnalyticsResultDTO:
        pass


class AnalyticsProvider(IAnalyticsCalculator):
    """Executes topology calculations independently of risk interpretation."""

    def calculate(
        self,
        tenant_id: str,
        workspace_id: str | None,
        nodes: list[NodeDTO],
        edges: list[EdgeDTO],
    ) -> AnalyticsResultDTO:
        if not nodes:
            return AnalyticsResultDTO(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                statistics={"node_count": 0, "edge_count": 0},
            )

        G = nx.Graph()
        for node in nodes:
            G.add_node(node.id)
        for edge in edges:
            G.add_edge(edge.source_id, edge.target_id)

        node_metrics: Dict[str, NodeCentralityDTO] = {}

        degree_cent = nx.degree_centrality(G)
        betweenness_cent = nx.betweenness_centrality(G)
        closeness_cent = nx.closeness_centrality(G)

        for node in nodes:
            nid = node.id
            node_metrics[nid] = NodeCentralityDTO(
                node_id=nid,
                degree=Decimal(str(degree_cent.get(nid, 0.0))),
                betweenness=Decimal(str(betweenness_cent.get(nid, 0.0))),
                closeness=Decimal(str(closeness_cent.get(nid, 0.0))),
            )

        components: List[ComponentDTO] = []
        for idx, comp in enumerate(nx.connected_components(G)):
            components.append(ComponentDTO(
                component_id=f"comp_{idx}",
                node_ids=list(comp)
            ))

        statistics = {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "component_count": len(components),
            "density": nx.density(G) if len(nodes) > 1 else 0.0,
        }

        return AnalyticsResultDTO(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            node_metrics=node_metrics,
            components=components,
            statistics=statistics,
        )
