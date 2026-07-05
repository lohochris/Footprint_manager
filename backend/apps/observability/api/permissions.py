from rest_framework.permissions import BasePermission

class IsObservabilityAdmin(BasePermission):
    """
    Requires the user to have observability admin privileges.
    For Sprint 15, we'll enforce that the user must be a superuser or staff.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))
