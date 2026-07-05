from typing import Any
from django.core.exceptions import ValidationError
from backend.apps.common.pipeline.core import BaseService, ExecutionResult
from backend.apps.graph.dtos import EdgeDTO, GraphStatsDTO, NodeDTO, TraversalResultDTO
from backend.apps.graph.repositories import DjangoGraphRepository
from backend.apps.graph.providers import DjangoORMGraphProvider
from backend.apps.graph.algorithms.traversals import find_neighborhood, find_shortest_path
from backend.apps.graph.statistics.metrics import calculate_graph_stats


def get_repository() -> DjangoGraphRepository:
    return DjangoGraphRepository(DjangoORMGraphProvider())


class GraphService:
    """Domain service interface for the Graph Intelligence and Relationship Analysis context."""

    @staticmethod
    def build_graph(
        user: Any,
        tenant: Any,
        workspace_id: Any = None,
    ) -> dict[str, Any]:
        """Triggers the graph.build pipeline to create graph representations from all contexts."""
        payload = {"workspace_id": str(workspace_id) if workspace_id else None}
        result: ExecutionResult = BaseService.execute(
            operation="graph.build",
            performed_by=user,
            tenant=tenant,
            payload=payload,
        )
        if not result.success:
            raise result.error or ValidationError("Build pipeline failed.")
        return result.data or {}

    @staticmethod
    def sync_graph(
        user: Any,
        tenant: Any,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        workspace_id: Any = None,
    ) -> None:
        """Triggers the graph.sync pipeline to incrementally append nodes/edges to the graph."""
        payload = {
            "workspace_id": str(workspace_id) if workspace_id else None,
            "nodes": nodes,
            "edges": edges,
        }
        result: ExecutionResult = BaseService.execute(
            operation="graph.sync",
            performed_by=user,
            tenant=tenant,
            payload=payload,
        )
        if not result.success:
            raise result.error or ValidationError("Sync pipeline failed.")

    @staticmethod
    def refresh_graph(
        user: Any,
        tenant: Any,
        workspace_id: Any = None,
    ) -> dict[str, Any]:
        """Clears and fully rebuilds the workspace graph cache."""
        payload = {"workspace_id": str(workspace_id) if workspace_id else None}
        result: ExecutionResult = BaseService.execute(
            operation="graph.refresh",
            performed_by=user,
            tenant=tenant,
            payload=payload,
        )
        if not result.success:
            raise result.error or ValidationError("Refresh pipeline failed.")
        return result.data or {}

    @staticmethod
    def get_subgraph(
        tenant: Any,
        workspace_id: Any = None,
    ) -> tuple[list[NodeDTO], list[EdgeDTO]]:
        """Retrieve isolated sub-graph from repository."""
        repo = get_repository()
        return repo.get_subgraph(str(tenant.id), str(workspace_id) if workspace_id else None)

    @staticmethod
    def expand_neighborhood(
        tenant: Any,
        workspace_id: Any,
        node_id: str,
        depth: int = 1,
        max_nodes: int = 5000,
    ) -> TraversalResultDTO:
        """Retrieve neighboring entities from repository and execute traversal algorithm."""
        tenant_id = str(tenant.id)
        w_id = str(workspace_id) if workspace_id else None

        repo = get_repository()
        nodes, edges = repo.get_subgraph(tenant_id, w_id)

        return find_neighborhood(nodes, edges, node_id, max_depth=depth, max_nodes=max_nodes)

    @staticmethod
    def get_shortest_path(
        tenant: Any,
        workspace_id: Any,
        start_node_id: str,
        end_node_id: str,
    ) -> list[NodeDTO]:
        """Determine shortest path between two nodes using BFS."""
        tenant_id = str(tenant.id)
        w_id = str(workspace_id) if workspace_id else None

        repo = get_repository()
        nodes, edges = repo.get_subgraph(tenant_id, w_id)

        return find_shortest_path(nodes, edges, start_node_id, end_node_id)

    @staticmethod
    def get_statistics(
        tenant: Any,
        workspace_id: Any = None,
    ) -> GraphStatsDTO:
        """Calculate network-wide metrics (density, degree averages, component sizes)."""
        tenant_id = str(tenant.id)
        w_id = str(workspace_id) if workspace_id else None

        repo = get_repository()
        nodes, edges = repo.get_subgraph(tenant_id, w_id)

        return calculate_graph_stats(nodes, edges)
