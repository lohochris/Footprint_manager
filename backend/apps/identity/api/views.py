from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from backend.apps.organizations.api.pagination import StandardResultsSetPagination
from backend.apps.identity.api.permissions import (
    CanManageIdentity,
    CanViewIdentity,
    get_user_tenant,
)
from backend.apps.identity.api.serializers import (
    IdentitySerializer,
    IdentityCreateSerializer,
    IdentityAttributeSerializer,
    IdentityRelationshipSerializer,
    IdentityMatchSerializer,
    IdentityMergeHistorySerializer,
)
from backend.apps.identity.models import (
    Identity,
    IdentityAttribute,
    IdentityRelationship,
    IdentityMatch,
    IdentityMergeHistory,
)
from backend.apps.identity.services.identity_service import IdentityService
from backend.apps.identity.services.graph import DjangoModelGraphExporter


class IdentityViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Identities."""

    queryset = Identity.objects.all()
    serializer_class = IdentitySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["label"]
    filterset_fields = ["entity_type", "workspace"]
    permission_classes = [CanViewIdentity]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset.filter(is_deleted=False)
        tenant = get_user_tenant(user)
        if not tenant:
            return self.queryset.none()
        return self.queryset.filter(tenant_id=tenant.id, is_deleted=False)

    def get_serializer_class(self):
        if self.action == "create":
            return IdentityCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        tenant = get_user_tenant(self.request.user)
        attributes = serializer.validated_data.pop("attributes", [])
        identity = IdentityService.resolve_identity(
            user=self.request.user,
            tenant=tenant,
            label=serializer.validated_data["label"],
            entity_type=serializer.validated_data["entity_type"],
            source=serializer.validated_data.get("source", "manual"),
            workspace_id=serializer.validated_data.get("workspace"),
            attributes=attributes,
        )
        serializer.instance = identity

    @action(detail=True, methods=["get"])
    def graph(self, request, pk=None):
        """Export identity and its surrounding local relationships in JSON format."""
        self.get_object()
        tenant = get_user_tenant(request.user)
        # Fetch related identities
        neighbors = Identity.objects.filter(
            tenant_id=tenant.id,
            is_deleted=False,
        )
        exporter = DjangoModelGraphExporter()
        data = exporter.export_json_nodes_edges(neighbors)
        return Response(data)


class IdentityAttributeViewSet(viewsets.ModelViewSet):
    queryset = IdentityAttribute.objects.all()
    serializer_class = IdentityAttributeSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [CanViewIdentity]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        tenant = get_user_tenant(user)
        if not tenant:
            return self.queryset.none()
        return self.queryset.filter(tenant_id=tenant.id)

    def perform_create(self, serializer):
        tenant = get_user_tenant(self.request.user)
        serializer.save(
            tenant_id=tenant.id,
            owner=self.request.user,
        )


class IdentityRelationshipViewSet(viewsets.ModelViewSet):
    queryset = IdentityRelationship.objects.all()
    serializer_class = IdentityRelationshipSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [CanViewIdentity]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        tenant = get_user_tenant(user)
        if not tenant:
            return self.queryset.none()
        return self.queryset.filter(tenant_id=tenant.id)

    def perform_create(self, serializer):
        tenant = get_user_tenant(self.request.user)
        serializer.save(
            tenant_id=tenant.id,
            owner=self.request.user,
        )


class IdentityMatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IdentityMatch.objects.all()
    serializer_class = IdentityMatchSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["review_status"]
    permission_classes = [CanViewIdentity]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        tenant = get_user_tenant(user)
        if not tenant:
            return self.queryset.none()
        return self.queryset.filter(tenant_id=tenant.id)

    @action(detail=True, methods=["post"], permission_classes=[CanManageIdentity])
    def merge(self, request, pk=None):
        """Action endpoint to manually approve duplicate match and merge candidates."""
        match = self.get_object()
        tenant = get_user_tenant(request.user)
        master = IdentityService.merge_identities(
            user=request.user,
            tenant=tenant,
            identity_a_id=match.candidate_a.id,
            identity_b_id=match.candidate_b.id,
        )
        return Response(IdentitySerializer(master).data, status=status.HTTP_200_OK)


class IdentityMergeHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IdentityMergeHistory.objects.all()
    serializer_class = IdentityMergeHistorySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [CanViewIdentity]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        tenant = get_user_tenant(user)
        if not tenant:
            return self.queryset.none()
        return self.queryset.filter(tenant_id=tenant.id)

    @action(detail=True, methods=["post"], permission_classes=[CanManageIdentity])
    def split(self, request, pk=None):
        """Action endpoint to roll back a previous merge operation and restore target state."""
        history = self.get_object()
        tenant = get_user_tenant(request.user)
        master = IdentityService.split_identity(
            user=request.user,
            tenant=tenant,
            merge_history_id=history.id,
        )
        return Response(IdentitySerializer(master).data, status=status.HTTP_200_OK)
