"""Permissions for workspace level access control."""

from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from backend.shared.constants.roles import ROLE_OWNER, ROLE_ADMIN
from backend.apps.organizations.selectors import workspace as workspace_selector


class IsWorkspaceMember(BasePermission):
    """Allow access only to users that are members of the workspace."""

    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        if not hasattr(obj, "id"):
            return False
        try:
            workspace_selector.get_user_workspace_membership(request.user, obj.id)
            return True
        except PermissionDenied:
            return False


class IsWorkspaceOwner(BasePermission):
    """Allow only the owner of the workspace's organization."""

    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        if not hasattr(obj, "id"):
            return False
        return workspace_selector.is_user_workspace_owner(request.user, obj)
