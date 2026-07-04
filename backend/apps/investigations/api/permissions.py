from rest_framework import permissions

from backend.apps.organizations.models import OrganizationMember, Organization
from backend.apps.investigations.models import InvestigationMember, PermissionLevel


def get_user_role(user, organization):
    """Resolve the user's role within the given organization using OrganizationMember."""
    if not user.is_authenticated or not organization:
        return None
    try:
        member = OrganizationMember.objects.get(user=user, organization=organization)
        return member.role
    except OrganizationMember.DoesNotExist:
        return None


def get_user_tenant(user):
    """Derive the tenant (Organization) for a user from their active memberships."""
    if not user.is_authenticated:
        return None
    member = OrganizationMember.objects.filter(user=user, status="active").first()
    return member.organization if member else None


class AuthenticatedPermission(permissions.BasePermission):
    """Base permission that enforces authentication for all actions."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class CanCreateInvestigation(AuthenticatedPermission):
    """Permission to create an investigation."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        user = request.user
        if user.is_superuser:
            return True
        # Must belong to an active organization
        return get_user_tenant(user) is not None


class CanViewInvestigation(AuthenticatedPermission):
    """Permission to view an investigation (Tenant Isolation)."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        # Tenant isolation
        user_org = get_user_tenant(user)
        if not user_org or obj.organization_id != user_org.id:
            return False

        # Superuser, owner, lead investigator, or organization owner/admin/manager can always view
        if obj.owner_id == user.id or getattr(obj, "lead_investigator_id", None) == user.id:
            return True

        role = get_user_role(user, obj.organization)
        if role in {"owner", "admin", "manager"}:
            return True

        # Or must be a registered active member of the investigation
        return InvestigationMember.objects.filter(
            investigation=obj,
            user=user,
            active=True
        ).exists()


class CanUpdateInvestigation(AuthenticatedPermission):
    """Permission to update an investigation."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        # Tenant isolation
        user_org = get_user_tenant(user)
        if not user_org or obj.organization_id != user_org.id:
            return False

        # Owner, lead investigator, or organization owner/admin/manager can update
        if obj.owner_id == user.id or getattr(obj, "lead_investigator_id", None) == user.id:
            return True

        role = get_user_role(user, obj.organization)
        return role in {"owner", "admin", "manager"}


class CanAssignMembers(AuthenticatedPermission):
    """Permission to assign members to an investigation."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        # Tenant isolation
        user_org = get_user_tenant(user)
        if not user_org or obj.organization_id != user_org.id:
            return False

        # Owner, lead investigator, or organization owner/admin/manager can assign members
        if obj.owner_id == user.id or getattr(obj, "lead_investigator_id", None) == user.id:
            return True

        role = get_user_role(user, obj.organization)
        return role in {"owner", "admin", "manager"}


class CanChangeStatus(AuthenticatedPermission):
    """Permission to change status of an investigation."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        # Tenant isolation
        user_org = get_user_tenant(user)
        if not user_org or obj.organization_id != user_org.id:
            return False

        # Owner, lead investigator, or organization owner/admin/manager can change status
        if obj.owner_id == user.id or getattr(obj, "lead_investigator_id", None) == user.id:
            return True

        role = get_user_role(user, obj.organization)
        return role in {"owner", "admin", "manager"}


class CanArchiveInvestigation(AuthenticatedPermission):
    """Permission to archive an investigation."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        # Tenant isolation
        user_org = get_user_tenant(user)
        if not user_org or obj.organization_id != user_org.id:
            return False

        # Owner or organization owner/admin can archive
        if obj.owner_id == user.id:
            return True

        role = get_user_role(user, obj.organization)
        return role in {"owner", "admin"}


class CanRestoreInvestigation(AuthenticatedPermission):
    """Permission to restore an investigation."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        # Tenant isolation
        user_org = get_user_tenant(user)
        if not user_org or obj.organization_id != user_org.id:
            return False

        # Owner or organization owner/admin can restore
        if obj.owner_id == user.id:
            return True

        role = get_user_role(user, obj.organization)
        return role in {"owner", "admin"}


class CanManageEvidence(AuthenticatedPermission):
    """Permission to link or manage evidence references."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        # Tenant isolation
        user_org = get_user_tenant(user)
        if not user_org or obj.organization_id != user_org.id:
            return False

        # Owner, lead investigator, or owner/admin/manager can manage evidence
        if obj.owner_id == user.id or getattr(obj, "lead_investigator_id", None) == user.id:
            return True

        role = get_user_role(user, obj.organization)
        if role in {"owner", "admin", "manager"}:
            return True

        # Or must be a registered active member of the investigation with write/admin privileges
        return InvestigationMember.objects.filter(
            investigation=obj,
            user=user,
            active=True,
            permission_level__in=[PermissionLevel.WRITE, PermissionLevel.ADMIN]
        ).exists()


class CanComment(AuthenticatedPermission):
    """Permission to comment on an investigation."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True

        # Tenant isolation
        user_org = get_user_tenant(user)
        if not user_org or obj.organization_id != user_org.id:
            return False

        # Owner, lead investigator, or owner/admin/manager can comment
        if obj.owner_id == user.id or getattr(obj, "lead_investigator_id", None) == user.id:
            return True

        role = get_user_role(user, obj.organization)
        if role in {"owner", "admin", "manager"}:
            return True

        # Or must be a registered active member of the investigation
        return InvestigationMember.objects.filter(
            investigation=obj,
            user=user,
            active=True
        ).exists()
