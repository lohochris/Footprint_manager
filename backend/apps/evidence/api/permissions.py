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


class CanUploadEvidence(AuthenticatedPermission):
    """Permission to upload/register new evidence."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.user.is_superuser:
            return True
        return get_user_tenant(request.user) is not None


class CanViewEvidence(AuthenticatedPermission):
    """Permission to view/retrieve evidence details."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        # Tenant isolation
        user_org = get_user_tenant(user)
        return bool(user_org and obj.tenant_id == user_org.id)


class CanManageEvidence(AuthenticatedPermission):
    """Permission to modify, delete, or perform custody operations on evidence.

    Enforces that only the current custodian can perform custody operations/updates.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        # Tenant isolation
        user_org = get_user_tenant(user)
        if not user_org or obj.tenant_id != user_org.id:
            return False

        # Custodian active lock: only active custodian can transfer or mutate
        return obj.current_custodian_id == user.id
