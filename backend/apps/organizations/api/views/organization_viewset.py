from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from backend.apps.organizations.permissions.organization import IsOrganizationMember, IsOrganizationOwner
from backend.apps.organizations.selectors.organization import get_organization_by_id, get_user_organization_membership
from backend.apps.organizations.serializers.organization import (
    OrganizationCreateSerializer,
    OrganizationSerializer,
    OrganizationUpdateSerializer,
)
from backend.apps.organizations.services import OrganizationService
from backend.apps.organizations.api.pagination import StandardResultsSetPagination
from backend.apps.organizations.api.throttling import SensitiveActionThrottle


class OrganizationViewSet(viewsets.GenericViewSet):
    """API endpoints for Organization CRUD and archive/restore.

    * ``list`` – list organizations the user is a member of.
    * ``retrieve`` – retrieve a single organization.
    * ``create`` – create a new organization (owner must be the request user).
    * ``update``/``partial_update`` – update organization details (owner only).
    * ``archive`` – archive (soft‑delete) an organization (owner only).
    * ``restore`` – restore a previously archived organization (owner only).
    """

    pagination_class = StandardResultsSetPagination
    throttle_classes = []  # normal read endpoints are not throttled
    permission_classes = [IsOrganizationMember]
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        # Use selector to fetch organizations the user belongs to.
        user = self.request.user
        return OrganizationService.list_user_organizations(user.id)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OrganizationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = OrganizationSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        org = get_organization_by_id(pk)
        # Permission check – member already enforced by class, but ensure tenant isolation.
        get_user_organization_membership(request.user.id, org.id)
        serializer = OrganizationSerializer(org)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = OrganizationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Service expects validated_data dict.
        organization = OrganizationService.create_organization(**serializer.validated_data)
        out_serializer = OrganizationSerializer(organization)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        org = get_organization_by_id(pk)
        # Only owners can update.
        self.check_object_permissions(request, org)
        serializer = OrganizationUpdateSerializer(data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        updated = OrganizationService.update_organization(org, **serializer.validated_data)
        out_serializer = OrganizationSerializer(updated)
        return Response(out_serializer.data)

    def partial_update(self, request, pk=None, *args, **kwargs):
        org = get_organization_by_id(pk)
        self.check_object_permissions(request, org)
        serializer = OrganizationUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = OrganizationService.update_organization(org, **serializer.validated_data)
        out_serializer = OrganizationSerializer(updated)
        return Response(out_serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsOrganizationOwner], throttle_classes=[SensitiveActionThrottle])
    def archive(self, request, pk=None):
        org = get_organization_by_id(pk)
        OrganizationService.archive_organization(org)
        return Response({"detail": "Organization archived"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsOrganizationOwner], throttle_classes=[SensitiveActionThrottle])
    def restore(self, request, pk=None):
        org = get_organization_by_id(pk)
        OrganizationService.restore_organization(org)
        return Response({"detail": "Organization restored"}, status=status.HTTP_200_OK)
