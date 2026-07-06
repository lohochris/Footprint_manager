import uuid
from typing import Optional
from django.core.exceptions import PermissionDenied, ValidationError

def get_tenant_id_for_user(user) -> Optional[uuid.UUID]:
    """
    Resolve the tenant_id for the given user by looking up their active OrganizationMember association.
    Returns the organization's tenant_id (which is the organization ID itself), or None.
    """
    if not user or not user.is_authenticated:
        return None

    from backend.apps.organizations.models.organization_member import OrganizationMember
    member = OrganizationMember.objects.filter(user=user, status="active").first()
    if not member:
        return None
    return member.organization_id


def resolve_workspace(user, workspace_id_or_slug: str):
    """
    Resolve a workspace given either a UUID or a slug string.
    Verifies that the user has access to the workspace via OrganizationMember.
    Returns the Workspace object or raises an appropriate exception.
    """
    from backend.apps.organizations.models.workspace import Workspace
    from backend.apps.organizations.models.organization_member import OrganizationMember

    if not workspace_id_or_slug:
        raise ValidationError("Workspace identifier must be provided.")

    queryset = Workspace.objects.select_related("organization")

    try:
        # Check if it's a UUID
        workspace_uuid = uuid.UUID(str(workspace_id_or_slug))
        workspace = queryset.get(id=workspace_uuid)
    except ValueError:
        # It's a slug
        try:
            workspace = queryset.get(slug=workspace_id_or_slug)
        except Workspace.DoesNotExist:
            raise ValidationError(f"Workspace with slug '{workspace_id_or_slug}' does not exist.")
    except Workspace.DoesNotExist:
        raise ValidationError(f"Workspace with id '{workspace_id_or_slug}' does not exist.")

    # Check access using the organization
    if not OrganizationMember.objects.filter(user=user, organization=workspace.organization).exists():
        raise PermissionDenied("User does not belong to the organization of this workspace.")

    return workspace
