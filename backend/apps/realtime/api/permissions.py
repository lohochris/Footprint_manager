from rest_framework import permissions

class IsRealtimeUser(permissions.IsAuthenticated):
    """
    Base permission for realtime endpoints.
    Requires authentication and a valid tenant context.
    """
    def has_permission(self, request, view):
        is_auth = super().has_permission(request, view)
        has_tenant = hasattr(request.user, "tenant_id") and request.user.tenant_id is not None
        return is_auth and has_tenant
