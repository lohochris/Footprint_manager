from backend.shared.utils.tenant_resolver import get_tenant_id_for_user
from rest_framework import permissions

class IsWorkspaceMember(permissions.BasePermission):
    """
    Custom permission to only allow members of a workspace to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # In a real app, this would check the user's role in the workspace.
        # For now, we just ensure they belong to the same tenant.
        return obj.tenant_id == get_tenant_id_for_user(request.user)
