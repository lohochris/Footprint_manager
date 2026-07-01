from rest_framework import permissions

from backend.apps.rbac.models import Role


class TenantScopedPermission(permissions.BasePermission):
    """Ensure the requesting user belongs to the same tenant (organization) as the object.

    Objects in the investigations domain are expected to have an ``organization`` attribute
    referencing the ``Organization`` model (the tenant).  ``has_object_permission`` returns
    ``True`` when the user's organization matches the object's organization.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not getattr(user, "is_authenticated", False):
            return False
        # Superusers bypass tenant checks
        if getattr(user, "is_superuser", False):
            return True
        # Objects are expected to expose an ``organization`` attribute
        obj_org = getattr(obj, "organization", None)
        user_org = getattr(user, "organization", None)
        return obj_org is not None and user_org is not None and obj_org.id == user_org.id


class RoleBasedPermission(permissions.BasePermission):
    """Grant access based on the user's role within the object's organization.

    Subclasses should define a ``allowed_roles`` (set of role name strings) attribute.
    """

    allowed_roles: set = set()

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not getattr(user, "is_authenticated", False):
            return False
        if getattr(user, "is_superuser", False):
            return True
        # Resolve organization from object (fallback to request.user.organization)
        organization = getattr(obj, "organization", None) or getattr(user, "organization", None)
        if not organization:
            return False
        try:
            role = Role.objects.get(user=user, organization=organization)
        except Role.DoesNotExist:
            return False
        return role.name in self.allowed_roles


class OwnerOrAdminPermission(permissions.BasePermission):
    """Allow access to the object owner, organization admin, or superuser.

    Subclasses may override ``admin_role_name`` if a custom admin role name is used.
    """

    admin_role_name = "admin"

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not getattr(user, "is_authenticated", False):
            return False
        if getattr(user, "is_superuser", False):
            return True
        # Owner check – objects are expected to have an ``owner_id`` field
        if getattr(obj, "owner_id", None) == getattr(user, "id", None):
            return True
        # Organization admin check
        organization = getattr(obj, "organization", None)
        if not organization:
            return False
        try:
            role = Role.objects.get(user=user, organization=organization)
        except Role.DoesNotExist:
            return False
        return role.name == self.admin_role_name


class ReadOnlyPermission(permissions.BasePermission):
    """Allow safe read‑only methods (GET, HEAD, OPTIONS) for any authenticated user.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.method in permissions.SAFE_METHODS
