"""Permissions for organization level access control."""

from __future__ import annotations

from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

# Role constants
from backend.shared.constants.roles import (
    ROLE_ADMIN,
    ROLE_OWNER,
)

# Selectors
from ..selectors import organization as org_selector


class IsOrganizationMember(BasePermission):
    """Allow access only to users that are members of the organization.

    The check is performed against the organization instance passed to the view
    via ``has_object_permission``. ``has_permission`` simply ensures the user is
    authenticated.
    """

    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        # ``obj`` is expected to be an ``Organization`` instance.
        if not hasattr(obj, "id"):
            return False
        try:
            org_selector.get_user_organization_membership(request.user, obj.id)
            return True
        except PermissionDenied:
            return False


class IsOrganizationOwner(BasePermission):
    """Allow only the owner of the organization.

    The owner role is defined by ``ROLE_OWNER`` in the shared constants.
    """

    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        if not hasattr(obj, "id"):
            return False
        try:
            membership = org_selector.get_user_organization_membership(request.user, obj.id)
            return membership.role == ROLE_OWNER
        except PermissionDenied:
            return False


class IsOrganizationAdminOrOwner(BasePermission):
    """Allow owners and admins of an organization.

    Role must be either ``ROLE_OWNER`` or ``ROLE_ADMIN``.
    """

    allowed_roles = {ROLE_OWNER, ROLE_ADMIN}

    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        if not hasattr(obj, "id"):
            return False
        try:
            membership = org_selector.get_user_organization_membership(request.user, obj.id)
            return membership.role in self.allowed_roles
        except PermissionDenied:
            return False
