"""Membership service layer for the organizations app.

Handles adding, removing, and changing roles of members for both organizations and workspaces.
All mutating actions are logged via AuditLog and respect rate limits.
"""

import time

# Simple in‑memory rate‑limit counters (per process) for demonstration.
# In production a distributed solution like Redis would be used.
from collections import defaultdict

from apps.audit.models.audit_log import AuditLog
from django.db import transaction

from ..models.organization_member import OrganizationMember
from ..models.workspace_member import WorkspaceMember
from ..validators import (
    validate_no_duplicate_membership,
    validate_no_duplicate_workspace_membership,
    validate_role,
)
from .base import ServiceError

_RATE_LIMITS = {
    "membership_change": {
        "limit": 10,  # per minute
        "window": 60,
        "counters": defaultdict(list),
    }
}

def _check_rate_limit(user_id, action):
    cfg = _RATE_LIMITS[action]
    now = time.time()
    timestamps = cfg["counters"][user_id]
    # Remove timestamps older than window
    cfg["counters"][user_id] = [t for t in timestamps if now - t < cfg["window"]]
    if len(cfg["counters"][user_id]) >= cfg["limit"]:
        raise ServiceError("Rate limit exceeded for membership changes.", 429)
    cfg["counters"][user_id].append(now)

class MembershipService:
    """Service for organization and workspace membership management."""

    @staticmethod
    def add_organization_member(organization, user, role: str, performed_by):
        """Add a user to an organization.

        Args:
            organization: Organization instance.
            user: User instance to add.
            role: Role string (must be one of the fixed choices).
            performed_by: User performing the action (for audit log).
        """
        _check_rate_limit(performed_by.id, "membership_change")
        validate_role(role)
        validate_no_duplicate_membership(organization, user)
        with transaction.atomic():
            member = OrganizationMember.objects.create(
                organization=organization, user=user, role=role
            )
            AuditLog.objects.create(
                action="organization_member_added",
                performed_by=performed_by,
                details={
                    "org_id": str(organization.id),
                    "user_id": user.id,
                    "role": role,
                },
            )
        return member

    @staticmethod
    def remove_organization_member(organization, user, performed_by):
        """Remove a user from an organization."""
        _check_rate_limit(performed_by.id, "membership_change")
        try:
            member = OrganizationMember.objects.get(organization=organization, user=user)
        except OrganizationMember.DoesNotExist:
            raise ServiceError("Membership not found.", 404)
        if member.role == "owner":
            raise ServiceError("Cannot remove the organization owner.", 400)
        with transaction.atomic():
            member.delete()
            AuditLog.objects.create(
                action="organization_member_removed",
                performed_by=performed_by,
                details={"org_id": str(organization.id), "user_id": user.id},
            )
        return None

    @staticmethod
    def change_organization_role(organization, user, new_role: str, performed_by):
        """Change a member's role within an organization."""
        _check_rate_limit(performed_by.id, "membership_change")
        validate_role(new_role)
        try:
            member = OrganizationMember.objects.get(organization=organization, user=user)
        except OrganizationMember.DoesNotExist:
            raise ServiceError("Membership not found.", 404)
        # Owner role changes are handled via ownership transfer service
        if member.role == "owner":
            raise ServiceError("Use ownership transfer to change the owner role.", 400)
        with transaction.atomic():
            member.role = new_role
            member.save()
            AuditLog.objects.create(
                action="organization_member_role_changed",
                performed_by=performed_by,
                details={
                    "org_id": str(organization.id),
                    "user_id": user.id,
                    "new_role": new_role,
                },
            )
        return member

    @staticmethod
    def add_workspace_member(workspace, user, role: str, performed_by):
        """Add a user to a workspace (must already belong to the parent organization)."""
        _check_rate_limit(performed_by.id, "membership_change")
        validate_role(role)
        validate_no_duplicate_workspace_membership(workspace, user)
        # Ensure user is a member of the organization
        if not OrganizationMember.objects.filter(organization=workspace.organization, user=user).exists():
            raise ServiceError("User must be a member of the organization to join the workspace.", 403)
        with transaction.atomic():
            member = WorkspaceMember.objects.create(
                workspace=workspace, user=user, role=role
            )
            AuditLog.objects.create(
                action="workspace_member_added",
                performed_by=performed_by,
                details={
                    "workspace_id": str(workspace.id),
                    "user_id": user.id,
                    "role": role,
                },
            )
        return member

    @staticmethod
    def remove_workspace_member(workspace, user, performed_by):
        """Remove a user from a workspace."""
        _check_rate_limit(performed_by.id, "membership_change")
        try:
            member = WorkspaceMember.objects.get(workspace=workspace, user=user)
        except WorkspaceMember.DoesNotExist as err:
            raise ServiceError("Workspace membership not found.", 404) from err
        with transaction.atomic():
            member.delete()
            AuditLog.objects.create(
                action="workspace_member_removed",
                performed_by=performed_by,
                details={"workspace_id": str(workspace.id), "user_id": user.id},
            )
        return None

    @staticmethod
    def change_workspace_role(workspace, user, new_role: str, performed_by):
        """Change a member's role within a workspace."""
        _check_rate_limit(performed_by.id, "membership_change")
        validate_role(new_role)
        try:
            member = WorkspaceMember.objects.get(workspace=workspace, user=user)
        except WorkspaceMember.DoesNotExist:
            raise ServiceError("Workspace membership not found.", 404)
        with transaction.atomic():
            member.role = new_role
            member.save()
            AuditLog.objects.create(
                action="workspace_member_role_changed",
                performed_by=performed_by,
                details={
                    "workspace_id": str(workspace.id),
                    "user_id": user.id,
                    "new_role": new_role,
                },
            )
        return member
