from rest_framework import serializers
from backend.apps.graph.models import GraphEdge, GraphNode, GraphSnapshot


class GraphNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GraphNode
        fields = [
            "id",
            "node_type",
            "label",
            "metadata",
            "confidence",
            "workspace",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class GraphEdgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GraphEdge
        fields = [
            "id",
            "source_node",
            "target_node",
            "relationship_type",
            "direction",
            "confidence",
            "provenance",
            "evidence_references",
            "investigation_references",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class GraphSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = GraphSnapshot
        fields = [
            "id",
            "workspace",
            "label",
            "graph_data",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ===========================================================================
# DTO SERIALIZERS (Pure Python boundaries)
# ===========================================================================

class NodeDTOSerializer(serializers.Serializer):
    id = serializers.CharField()
    tenant_id = serializers.CharField()
    workspace_id = serializers.CharField(allow_null=True)
    node_type = serializers.CharField()
    label = serializers.CharField()
    metadata = serializers.DictField(child=serializers.JSONField())
    confidence = serializers.DecimalField(max_digits=4, decimal_places=3)
    created_at = serializers.CharField(allow_null=True, required=False)
    updated_at = serializers.CharField(allow_null=True, required=False)


class EdgeDTOSerializer(serializers.Serializer):
    id = serializers.CharField()
    tenant_id = serializers.CharField()
    source_id = serializers.CharField()
    target_id = serializers.CharField()
    relationship_type = serializers.CharField()
    direction = serializers.CharField()
    confidence = serializers.DecimalField(max_digits=4, decimal_places=3)
    provenance = serializers.CharField()
    evidence_references = serializers.ListField(child=serializers.CharField())
    investigation_references = serializers.ListField(child=serializers.CharField())
    created_at = serializers.CharField(allow_null=True, required=False)
    updated_at = serializers.CharField(allow_null=True, required=False)


class TraversalResultDTOSerializer(serializers.Serializer):
    visited_nodes = NodeDTOSerializer(many=True)
    visited_edges = EdgeDTOSerializer(many=True)
    depth = serializers.IntegerField()
    statistics = serializers.DictField(child=serializers.JSONField())


class GraphStatsDTOSerializer(serializers.Serializer):
    node_count = serializers.IntegerField()
    edge_count = serializers.IntegerField()
    density = serializers.DecimalField(max_digits=4, decimal_places=3)
    average_degree = serializers.DecimalField(max_digits=4, decimal_places=3)
    isolated_nodes = serializers.IntegerField()
    largest_component_size = serializers.IntegerField()
