from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from backend.apps.organizations.permissions.workspace import IsWorkspaceMember, IsWorkspaceOwner
from backend.shared.utils.tenant_resolver import resolve_workspace
from backend.apps.organizations.serializers.workspace import (
    WorkspaceCreateSerializer,
    WorkspaceSerializer,
    WorkspaceUpdateSerializer,
)
from backend.apps.organizations.services.workspace_service import WorkspaceService
from backend.apps.organizations.api.pagination import StandardResultsSetPagination
from backend.apps.organizations.api.throttling import SensitiveActionThrottle


class WorkspaceViewSet(viewsets.GenericViewSet):
    """API endpoints for Workspace CRUD and archive/restore.

    * ``list`` – list workspaces belonging to an organization the user can access.
    * ``retrieve`` – retrieve a single workspace.
    * ``create`` – create a new workspace (owner must be request user).
    * ``update``/``partial_update`` – modify workspace details (owner/admin/manager).
    * ``archive`` – soft‑delete a workspace (owner/admin/manager).
    * ``restore`` – restore an archived workspace (owner/admin/manager).
    """

    pagination_class = StandardResultsSetPagination
    throttle_classes = []
    permission_classes = [IsWorkspaceMember]
    serializer_class = WorkspaceSerializer

    def get_queryset(self):
        user = self.request.user
        # Expect an ``organization_id`` query param for listing workspaces.
        org_id = self.request.query_params.get("organization_id")
        if org_id:
            return WorkspaceService.list_organization_workspaces(user, int(org_id))
        return []  # Empty list when not filtered – client must provide org.

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = WorkspaceSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = WorkspaceSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        workspace = resolve_workspace(request.user, pk)
        self.check_object_permissions(request, workspace)
        serializer = WorkspaceSerializer(workspace)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = WorkspaceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        organization = serializer.validated_data["organization"]
        owner = request.user
        workspace = WorkspaceService.create_workspace(
            name=serializer.validated_data["name"],
            slug=serializer.validated_data["slug"],
            organization=organization,
            owner=owner,
        )
        out_serializer = WorkspaceSerializer(workspace)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        workspace = resolve_workspace(request.user, pk)
        self.check_object_permissions(request, workspace)
        serializer = WorkspaceUpdateSerializer(data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        updated = WorkspaceService.update_workspace(workspace, request.user, **serializer.validated_data)
        out_serializer = WorkspaceSerializer(updated)
        return Response(out_serializer.data)

    def partial_update(self, request, pk=None, *args, **kwargs):
        workspace = resolve_workspace(request.user, pk)
        self.check_object_permissions(request, workspace)
        serializer = WorkspaceUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = WorkspaceService.update_workspace(workspace, request.user, **serializer.validated_data)
        out_serializer = WorkspaceSerializer(updated)
        return Response(out_serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsWorkspaceOwner], throttle_classes=[SensitiveActionThrottle])
    def archive(self, request, pk=None):
        workspace = resolve_workspace(request.user, pk)
        WorkspaceService.archive_workspace(workspace, request.user)
        return Response({"detail": "Workspace archived"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsWorkspaceOwner], throttle_classes=[SensitiveActionThrottle])
    def restore(self, request, pk=None):
        workspace = resolve_workspace(request.user, pk)
        WorkspaceService.restore_workspace(workspace, request.user)
        return Response({"detail": "Workspace restored"}, status=status.HTTP_200_OK)
