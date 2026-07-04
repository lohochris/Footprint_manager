"""Workspace selectors for tenant‑isolated reads.

All selectors enforce that the requesting user belongs to the organization that
owns the workspace.
"""

import uuid
from typing import Union
from django.core.exceptions import PermissionDenied

from backend.apps.accounts.models.user import User
from ..models.organization_member import OrganizationMember
from ..models.workspace import Workspace
from ..models.workspace_member import WorkspaceMember


def get_user_workspace_membership(user: User, workspace_id):
    """Return the workspace membership for *user*.

    Raises ``PermissionDenied`` if the user is not a member of the workspace.
    """
    try:
        return WorkspaceMember.objects.select_related("workspace").get(
            user=user, workspace_id=workspace_id
        )
    except WorkspaceMember.DoesNotExist:
        raise PermissionDenied("User is not a member of this workspace.")


def get_workspace_by_id(user: User, workspace_id):
    """Retrieve a workspace ensuring tenant isolation.

    The caller must be a member of the workspace's organization.
    """
    # Verify membership via organization membership first.
    workspace = Workspace.objects.select_related("organization").get(pk=workspace_id)
    # Ensure the user is a member of the organization.
    if not OrganizationMember.objects.filter(user=user, organization=workspace.organization).exists():
        raise PermissionDenied("User does not belong to the organization of this workspace.")
    return workspace

def list_workspaces_for_user(user: User):
    """Return a ``QuerySet`` of all workspaces the user belongs to via organization membership.
    """
    return Workspace.objects.filter(organization__members__user=user).distinct()


def list_workspaces_for_organization(user: User, organization_id: uuid.UUID | str):
    """Return a ``QuerySet`` of workspaces for the given organization if the user is a member.

    Raises PermissionDenied if the user does not belong to the organization.
    """
    if not OrganizationMember.objects.filter(user=user, organization_id=organization_id).exists():
        raise PermissionDenied("User does not belong to the specified organization.")
    return Workspace.objects.filter(organization_id=organization_id)


def is_user_workspace_owner(user: User, workspace: Workspace) -> bool:
    """True if *user* is the recorded owner of the workspace's organization.
    """
    # Ownership is tied to organization owner; workspace does not have its own owner field.
    return workspace.organization.owner_id == user.id
