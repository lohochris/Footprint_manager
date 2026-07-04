import abc
from decimal import Decimal
from typing import Any
from django.db import transaction
from backend.apps.graph.dtos import EdgeDTO, NodeDTO
from backend.apps.graph.models import GraphEdge, GraphNode


class GraphProvider(abc.ABC):
    """Abstract Interface for Graph Database and Storage Providers."""

    @abc.abstractmethod
    def batch_write(
        self,
        tenant_id: str,
        workspace_id: str | None,
        nodes: list[NodeDTO],
        edges: list[EdgeDTO],
    ) -> None:
        """Write nodes and edges transactionally in batch."""
        pass

    @abc.abstractmethod
    def fetch_isolated_subgraph(
        self,
        tenant_id: str,
        workspace_id: str | None,
    ) -> tuple[list[NodeDTO], list[EdgeDTO]]:
        """Retrieve all nodes and edges isolated by tenant and workspace."""
        pass

    @abc.abstractmethod
    def delete_workspace_graph(self, tenant_id: str, workspace_id: str | None) -> None:
        """Delete all graph nodes and edges for a tenant workspace."""
        pass


class DjangoORMGraphProvider(GraphProvider):
    """Concrete GraphProvider implementation using the Django ORM."""

    def batch_write(
        self,
        tenant_id: str,
        workspace_id: str | None,
        nodes: list[NodeDTO],
        edges: list[EdgeDTO],
    ) -> None:
        with transaction.atomic():
            # 1. Bulk insert/update nodes
            node_map = {}
            for node_dto in nodes:
                # Use update_or_create to allow idempotent sync
                node, _ = GraphNode.objects.update_or_create(
                    id=node_dto.id,
                    tenant_id=tenant_id,
                    defaults={
                        "organization_id": tenant_id,
                        "workspace_id": workspace_id,
                        "node_type": node_dto.node_type,
                        "label": node_dto.label,
                        "metadata": node_dto.metadata,
                        "confidence": node_dto.confidence,
                    },
                )
                node_map[node_dto.id] = node

            # 2. Bulk insert/update edges
            for edge_dto in edges:
                source = node_map.get(edge_dto.source_id) or GraphNode.objects.filter(id=edge_dto.source_id).first()
                target = node_map.get(edge_dto.target_id) or GraphNode.objects.filter(id=edge_dto.target_id).first()
                if not source or not target:
                    continue  # Orphan edges skipped

                GraphEdge.objects.update_or_create(
                    id=edge_dto.id,
                    tenant_id=tenant_id,
                    defaults={
                        "source_node": source,
                        "target_node": target,
                        "relationship_type": edge_dto.relationship_type,
                        "direction": edge_dto.direction,
                        "confidence": edge_dto.confidence,
                        "provenance": edge_dto.provenance,
                        "evidence_references": edge_dto.evidence_references,
                        "investigation_references": edge_dto.investigation_references,
                    },
                )

    def fetch_isolated_subgraph(
        self,
        tenant_id: str,
        workspace_id: str | None,
    ) -> tuple[list[NodeDTO], list[EdgeDTO]]:
        # Filter nodes and edges by tenant and workspace
        nodes_qs = GraphNode.objects.filter(tenant_id=tenant_id)
        if workspace_id:
            nodes_qs = nodes_qs.filter(workspace_id=workspace_id)

        node_ids = nodes_qs.values_list("id", flat=True)
        edges_qs = GraphEdge.objects.filter(
            tenant_id=tenant_id,
            source_node_id__in=node_ids,
            target_node_id__in=node_ids,
        )

        nodes_dto = [
            NodeDTO(
                id=str(n.id),
                tenant_id=str(n.tenant_id),
                workspace_id=str(n.workspace_id) if n.workspace_id else None,
                node_type=n.node_type,
                label=n.label,
                metadata=n.metadata or {},
                confidence=n.confidence,
                created_at=n.created_at.isoformat() if n.created_at else None,
                updated_at=n.updated_at.isoformat() if n.updated_at else None,
            )
            for n in nodes_qs
        ]

        edges_dto = [
            EdgeDTO(
                id=str(e.id),
                tenant_id=str(e.tenant_id),
                source_id=str(e.source_node_id),
                target_id=str(e.target_node_id),
                relationship_type=e.relationship_type,
                direction=e.direction,
                confidence=e.confidence,
                provenance=e.provenance,
                evidence_references=e.evidence_references or [],
                investigation_references=e.investigation_references or [],
                created_at=e.created_at.isoformat() if e.created_at else None,
                updated_at=e.updated_at.isoformat() if e.updated_at else None,
            )
            for e in edges_qs
        ]

        return nodes_dto, edges_dto

    def delete_workspace_graph(self, tenant_id: str, workspace_id: str | None) -> None:
        with transaction.atomic():
            nodes_qs = GraphNode.objects.filter(tenant_id=tenant_id)
            if workspace_id:
                nodes_qs = nodes_qs.filter(workspace_id=workspace_id)
            # Cascade deletes edges automatically
            nodes_qs.delete()
