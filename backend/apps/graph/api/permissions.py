from rest_framework import permissions
from backend.apps.identity.api.permissions import get_user_tenant


class IsTenantMember(permissions.BasePermission):
    """Restricts access to requests matching the user's active tenant membership."""

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        tenant = get_user_tenant(request.user)
        request.tenant = tenant  # Cache on request
        return tenant is not None

    def has_object_permission(self, request, view, obj) -> bool:
        if request.user.is_superuser:
            return True
        tenant = getattr(request, "tenant", None) or get_user_tenant(request.user)
        return bool(tenant and obj.tenant_id == tenant.id)
