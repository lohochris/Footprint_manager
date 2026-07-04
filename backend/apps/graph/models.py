from django.db import models
from backend.apps.evidence.models.mixins import (
    AuditFieldsMixin,
    OwnershipMixin,
    SoftDeleteMixin,
    TenantIsolationMixin,
    UUIDPrimaryKeyMixin,
)
from backend.apps.graph.choices import GraphNodeType, GraphRelationshipType


class GraphNode(
    UUIDPrimaryKeyMixin,
    AuditFieldsMixin,
    SoftDeleteMixin,
    OwnershipMixin,
    TenantIsolationMixin,
):
    """Represents a cached read-model node in the platform relationship graph."""

    node_type = models.CharField(
        max_length=50,
        choices=GraphNodeType.choices,
        default=GraphNodeType.CUSTOM,
    )
    label = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict, blank=True)
    confidence = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        default="1.000",
    )
    workspace = models.ForeignKey(
        "organizations.Workspace",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="graph_nodes",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="graph_nodes",
    )

    class Meta:
        indexes = [
            models.Index(fields=["tenant_id", "node_type"]),
            models.Index(fields=["tenant_id", "workspace_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.label} ({self.node_type})"


class GraphEdge(
    UUIDPrimaryKeyMixin,
    AuditFieldsMixin,
    SoftDeleteMixin,
    OwnershipMixin,
    TenantIsolationMixin,
):
    """Represents a relationship/edge between two GraphNodes."""

    source_node = models.ForeignKey(
        GraphNode,
        on_delete=models.CASCADE,
        related_name="outgoing_edges",
    )
    target_node = models.ForeignKey(
        GraphNode,
        on_delete=models.CASCADE,
        related_name="incoming_edges",
    )
    relationship_type = models.CharField(
        max_length=50,
        choices=GraphRelationshipType.choices,
        default=GraphRelationshipType.CUSTOM,
    )
    direction = models.CharField(max_length=20, default="directed")
    confidence = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        default="1.000",
    )
    provenance = models.CharField(max_length=255, default="system")
    evidence_references = models.JSONField(default=list, blank=True)
    investigation_references = models.JSONField(default=list, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["tenant_id", "source_node_id"]),
            models.Index(fields=["tenant_id", "target_node_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.source_node.label} -> {self.target_node.label} ({self.relationship_type})"


class GraphSnapshot(
    UUIDPrimaryKeyMixin,
    AuditFieldsMixin,
    SoftDeleteMixin,
    OwnershipMixin,
    TenantIsolationMixin,
):
    """Represents a versioned snapshot of the workspace graph state."""

    workspace = models.ForeignKey(
        "organizations.Workspace",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="graph_snapshots",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="graph_snapshots",
    )
    label = models.CharField(max_length=255)
    graph_data = models.JSONField(default=dict)

    def __str__(self) -> str:
        return f"Snapshot: {self.label} ({self.created_at})"
