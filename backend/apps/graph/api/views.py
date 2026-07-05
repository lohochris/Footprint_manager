from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError

from backend.apps.graph.api.permissions import IsTenantMember
from backend.apps.graph.api.serializers import (
    GraphEdgeSerializer,
    GraphNodeSerializer,
    GraphSnapshotSerializer,
    NodeDTOSerializer,
    EdgeDTOSerializer,
    TraversalResultDTOSerializer,
    GraphStatsDTOSerializer,
)
from backend.apps.graph.models import GraphEdge, GraphNode, GraphSnapshot
from backend.apps.graph.services.graph_service import GraphService


class GraphNodeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GraphNodeSerializer
    permission_classes = [IsTenantMember]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            return GraphNode.objects.none()
        qs = GraphNode.objects.filter(tenant_id=tenant.id)
        workspace_id = self.request.query_params.get("workspace_id")
        if workspace_id:
            qs = qs.filter(workspace_id=workspace_id)
        return qs


class GraphEdgeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GraphEdgeSerializer
    permission_classes = [IsTenantMember]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            return GraphEdge.objects.none()
        qs = GraphEdge.objects.filter(tenant_id=tenant.id)
        workspace_id = self.request.query_params.get("workspace_id")
        if workspace_id:
            # Filter edges where both source and target are in the workspace
            qs = qs.filter(
                source_node__workspace_id=workspace_id,
                target_node__workspace_id=workspace_id,
            )
        return qs


class GraphSnapshotViewSet(viewsets.ModelViewSet):
    serializer_class = GraphSnapshotSerializer
    permission_classes = [IsTenantMember]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            return GraphSnapshot.objects.none()
        qs = GraphSnapshot.objects.filter(tenant_id=tenant.id)
        workspace_id = self.request.query_params.get("workspace_id")
        if workspace_id:
            qs = qs.filter(workspace_id=workspace_id)
        return qs

    def perform_create(self, serializer):
        tenant = getattr(self.request, "tenant", None)
        serializer.save(
            tenant_id=tenant.id,
            organization_id=tenant.id,
            owner=self.request.user,
        )


from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

class GraphTraversalViewSet(viewsets.ViewSet):
    """Endpoints for performing graph traversals, calculations, and sync operations."""
    permission_classes = [IsTenantMember]

    @extend_schema(
        parameters=[
            OpenApiParameter("node_id", OpenApiTypes.UUID, description="Start node ID"),
            OpenApiParameter("workspace_id", OpenApiTypes.UUID, required=False),
            OpenApiParameter("depth", OpenApiTypes.INT, default=1),
        ],
        responses=TraversalResultDTOSerializer
    )
    @action(detail=False, methods=["get"], url_path="expand")
    def expand(self, request):
        tenant = request.tenant
        node_id = request.query_params.get("node_id")
        if not node_id:
            return Response({"error": "node_id query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        workspace_id = request.query_params.get("workspace_id")
        depth = int(request.query_params.get("depth", 1))

        res = GraphService.expand_neighborhood(tenant, workspace_id, node_id, depth)
        serializer = TraversalResultDTOSerializer(res)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter("start_node_id", OpenApiTypes.UUID),
            OpenApiParameter("end_node_id", OpenApiTypes.UUID),
            OpenApiParameter("workspace_id", OpenApiTypes.UUID, required=False),
        ],
        responses=NodeDTOSerializer(many=True)
    )
    @action(detail=False, methods=["get"], url_path="shortest-path")
    def shortest_path(self, request):
        tenant = request.tenant
        start_id = request.query_params.get("start_node_id")
        end_id = request.query_params.get("end_node_id")
        if not start_id or not end_id:
            return Response({"error": "start_node_id and end_node_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        workspace_id = request.query_params.get("workspace_id")

        res = GraphService.get_shortest_path(tenant, workspace_id, start_id, end_id)
        serializer = NodeDTOSerializer(res, many=True)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter("workspace_id", OpenApiTypes.UUID, required=False),
        ],
        responses=GraphStatsDTOSerializer
    )
    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request):
        tenant = request.tenant
        workspace_id = request.query_params.get("workspace_id")

        stats = GraphService.get_statistics(tenant, workspace_id)
        serializer = GraphStatsDTOSerializer(stats)
        return Response(serializer.data)

    @extend_schema(
        request={"application/json": {"type": "object", "properties": {"workspace_id": {"type": "string", "format": "uuid"}}}},
        responses={200: {"type": "object", "properties": {"status": {"type": "string"}, "data": {"type": "object"}}}}
    )
    @action(detail=False, methods=["post"], url_path="rebuild")
    def rebuild(self, request):
        tenant = request.tenant
        workspace_id = request.data.get("workspace_id")

        res = GraphService.refresh_graph(request.user, tenant, workspace_id)
        return Response({"status": "success", "data": res})

    @extend_schema(
        parameters=[
            OpenApiParameter("workspace_id", OpenApiTypes.UUID, required=False),
        ],
        responses={200: {"type": "object", "properties": {"elements": {"type": "object"}}}}
    )
    @action(detail=False, methods=["get"], url_path="visualize/cytoscape")
    def cytoscape(self, request):
        """Format the isolated sub-graph into Cytoscape.js readable format."""
        tenant = request.tenant
        workspace_id = request.query_params.get("workspace_id")

        nodes, edges = GraphService.get_subgraph(tenant, workspace_id)

        cy_nodes = [
            {
                "data": {
                    "id": n.id,
                    "label": n.label,
                    "node_type": n.node_type,
                    "confidence": float(n.confidence),
                    **n.metadata,
                }
            }
            for n in nodes
        ]

        cy_edges = [
            {
                "data": {
                    "id": e.id,
                    "source": e.source_id,
                    "target": e.target_id,
                    "relationship_type": e.relationship_type,
                    "confidence": float(e.confidence),
                }
            }
            for e in edges
        ]

        return Response({"elements": {"nodes": cy_nodes, "edges": cy_edges}})
