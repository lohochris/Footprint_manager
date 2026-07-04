from rest_framework import permissions
from backend.apps.organizations.models import OrganizationMember


def get_user_tenant(user):
    """Derive the tenant (Organization) for a user from their active memberships."""
    if not user.is_authenticated:
        return None
    member = OrganizationMember.objects.filter(user=user, status="active").first()
    return member.organization if member else None


class AuthenticatedPermission(permissions.BasePermission):
    """Base permission enforcing user authentication."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class CanViewIdentity(AuthenticatedPermission):
    """Permission to view/retrieve identity details."""

    def has_permission(self, request, view):
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        user_org = get_user_tenant(user)
        return bool(user_org and obj.tenant_id == user_org.id)


class CanManageIdentity(AuthenticatedPermission):
    """Permission to create, modify, or delete identity details."""

    def has_permission(self, request, view):
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        user_org = get_user_tenant(user)
        return bool(user_org and obj.tenant_id == user_org.id)
