"""Package for organization validators.

Provides all validator functions for organizations and workspaces.
"""

import hashlib
import secrets

from django.core.exceptions import ValidationError
from .workspace import validate_workspace_settings, validate_workspace_slug_unique


from ..models.invitation import Invitation
from ..models.organization import Organization
from ..models.organization_member import OrganizationMember
from ..models.workspace import Workspace
from ..models.workspace_member import WorkspaceMember

# Fixed role choices (must match model definitions)
ROLE_CHOICES = {"owner", "admin", "manager", "analyst", "member", "viewer"}


def validate_organization_slug_unique(slug: str):
    """Ensure the organization slug does not already exist.

    Slugs are globally unique and immutable.
    """
    if Organization.objects.filter(slug=slug).exists():
        raise ValidationError(f"Organization slug '{slug}' is already in use.")





def validate_no_duplicate_membership(organization: Organization, user):
    """Prevent adding the same user twice to an organization.
    """
    if OrganizationMember.objects.filter(organization=organization, user=user).exists():
        raise ValidationError("User is already a member of this organization.")


def validate_no_duplicate_workspace_membership(workspace: Workspace, user):
    """Prevent duplicate workspace membership.
    """
    if WorkspaceMember.objects.filter(workspace=workspace, user=user).exists():
        raise ValidationError("User is already a member of this workspace.")


def validate_no_active_invitation(organization: Organization, email: str):
    """Only a single pending invitation per email per organization.
    """
    if Invitation.objects.filter(
        organization=organization, email=email, status="pending"
    ).exists():
        raise ValidationError("An active invitation already exists for this email.")


def validate_invitation_not_expired(invitation: Invitation):
    """Raise if the invitation has passed its expiry date.
    """
    if invitation.is_expired():
        raise ValidationError("Invitation token has expired.")


def validate_role(value: str):
    """Ensure a role is one of the fixed choices.
    """
    if value not in ROLE_CHOICES:
        raise ValidationError(f"Invalid role '{value}'. Must be one of {sorted(ROLE_CHOICES)}.")


def validate_ownership_transfer(current_owner, new_owner, organization: Organization):
    """Validate that ownership transfer is allowed.

    * ``new_owner`` must be a member of the organization.
    * ``new_owner`` cannot be the same as ``current_owner``.
    """
    if current_owner == new_owner:
        raise ValidationError("New owner must be different from the current owner.")
    if not OrganizationMember.objects.filter(organization=organization, user=new_owner).exists():
        raise ValidationError("New owner must be a member of the organization.")


def generate_invitation_token() -> str:
    """Generate a secure random token for invitations.
    """
    return secrets.token_urlsafe(32)


def hash_invitation_token(token: str) -> str:
    """Return the SHA‑256 hash of the invitation token.
    """
    return hashlib.sha256(token.encode()).hexdigest()

# Workspace‑specific validators imported from sibling module


__all__ = [
    "validate_organization_slug_unique",
    "validate_workspace_slug_unique",
    "validate_no_duplicate_membership",
    "validate_no_duplicate_workspace_membership",
    "validate_no_active_invitation",
    "validate_invitation_not_expired",
    "validate_role",
    "validate_ownership_transfer",
    "generate_invitation_token",
    "hash_invitation_token",
    "validate_workspace_settings",
]
