from backend.shared.utils.tenant_resolver import get_tenant_id_for_user
from rest_framework import permissions

class IsRealtimeUser(permissions.IsAuthenticated):
    """
    Base permission for realtime endpoints.
    Requires authentication and a valid tenant context.
    """
    def has_permission(self, request, view):
        is_auth = super().has_permission(request, view)
        has_tenant = hasattr(request.user, "tenant_id") and get_tenant_id_for_user(request.user) is not None
        return is_auth and has_tenant
