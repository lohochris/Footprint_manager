from django.core.exceptions import ValidationError
from backend.apps.organizations.models import OrganizationMember


STATUS_TRANSITIONS = {
    "draft": ["active", "archived"],
    "active": ["suspended", "completed", "archived"],
    "suspended": ["active", "archived"],
    "completed": ["archived"],
    "archived": [],  # Restoring from archived is a dedicated restore operation
}


def validate_status_transition(current: str, target: str) -> None:
    """Validate that ``target`` is an allowed next status from ``current``.

    Raises:
        ValidationError: If the transition is not permitted.
    """
    allowed = STATUS_TRANSITIONS.get(current, [])
    if target not in allowed:
        raise ValidationError(
            f"Invalid status transition from '{current}' to '{target}'. Allowed: {allowed}"
        )


ALLOWED_PRIORITIES = {"critical", "high", "medium", "low"}


def validate_priority(value: str) -> None:
    if value not in ALLOWED_PRIORITIES:
        raise ValidationError(f"Invalid priority '{value}'. Must be one of {ALLOWED_PRIORITIES}.")


def validate_tags(tags: list[str]) -> None:
    if not isinstance(tags, list):
        raise ValidationError("Tags must be a list of strings.")
    for tag in tags:
        if not isinstance(tag, str) or not tag.strip():
            raise ValidationError("Each tag must be a non‑empty string.")
        if len(tag) > 50:
            raise ValidationError("Tag length must not exceed 50 characters.")


def validate_investigation_tenancy(organization, user, workspace=None) -> None:
    """Ensure the user belongs to the organization and the workspace aligns with it."""
    is_member = OrganizationMember.objects.filter(
        organization=organization,
        user=user,
        status="active"
    ).exists()

    if not is_member:
        raise ValidationError(f"User is not an active member of organization '{organization.name}'.")

    if workspace and workspace.organization != organization:
        raise ValidationError(f"Workspace '{workspace.name}' does not belong to organization '{organization.name}'.")


def validate_ownership_transfer(investigation, current_owner, new_owner) -> None:
    """Validate ownership transfer rules."""
    if new_owner == current_owner:
        raise ValidationError("Cannot transfer ownership to the current owner.")

    new_owner_is_member = OrganizationMember.objects.filter(
        organization=investigation.organization,
        user=new_owner,
        status="active"
    ).exists()

    if not new_owner_is_member:
        raise ValidationError("New owner must be an active member of the organization.")
