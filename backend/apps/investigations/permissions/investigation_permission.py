from rest_framework import permissions

from backend.apps.rbac.models import Role


class IsInvestigationOwnerOrLeadOrAdmin(permissions.BasePermission):
    """Grant access to owners, lead investigators, and admins within the tenant.

    Checks:
    * The request user is the investigation owner.
    * The user is the lead investigator.
    * The user has a role with sufficient privileges (admin/manager) in the organization.
    * Superusers have full access.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        # Superuser shortcut
        if user.is_superuser:
            return True
        # Owner or lead investigator
        if obj.owner_id == user.id or getattr(obj, "lead_investigator_id", None) == user.id:
            return True
        # Role-based check within the organization (tenant)
        organization = obj.organization
        try:
            role = Role.objects.get(user=user, organization=organization)
        except Role.DoesNotExist:
            return False
        # Define privileged role names in a constant (adjust as needed)
        privileged_roles = {"admin", "manager", "investigation_admin"}
        return role.name in privileged_roles

class CanArchiveRestore(permissions.BasePermission):
    """Only owners or organization admins may archive/restore investigations."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if obj.owner_id == user.id:
            return True
        # Organization admin check
        try:
            role = Role.objects.get(user=user, organization=obj.organization)
        except Role.DoesNotExist:
            return False
        return role.name == "admin"
