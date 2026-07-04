import abc
from backend.apps.graph.dtos import EdgeDTO, NodeDTO
from backend.apps.graph.providers import GraphProvider


class GraphRepository(abc.ABC):
    """Architectural Repository Pattern managing isolated graph operations."""

    @abc.abstractmethod
    def get_subgraph(
        self,
        tenant_id: str,
        workspace_id: str | None = None,
    ) -> tuple[list[NodeDTO], list[EdgeDTO]]:
        """Retrieve isolated DTO lists of nodes and edges."""
        pass

    @abc.abstractmethod
    def save_subgraph(
        self,
        tenant_id: str,
        workspace_id: str | None,
        nodes: list[NodeDTO],
        edges: list[EdgeDTO],
    ) -> None:
        """Persist DTO nodes and edges to the database/provider."""
        pass

    @abc.abstractmethod
    def clear_subgraph(self, tenant_id: str, workspace_id: str | None) -> None:
        """Delete all node/edge components in this workspace."""
        pass


class DjangoGraphRepository(GraphRepository):
    """Concrete GraphRepository leveraging a pluggable GraphProvider."""

    def __init__(self, provider: GraphProvider) -> None:
        self.provider = provider

    def get_subgraph(
        self,
        tenant_id: str,
        workspace_id: str | None = None,
    ) -> tuple[list[NodeDTO], list[EdgeDTO]]:
        return self.provider.fetch_isolated_subgraph(tenant_id, workspace_id)

    def save_subgraph(
        self,
        tenant_id: str,
        workspace_id: str | None,
        nodes: list[NodeDTO],
        edges: list[EdgeDTO],
    ) -> None:
        self.provider.batch_write(tenant_id, workspace_id, nodes, edges)

    def clear_subgraph(self, tenant_id: str, workspace_id: str | None) -> None:
        self.provider.delete_workspace_graph(tenant_id, workspace_id)
