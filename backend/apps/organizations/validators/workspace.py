"""Validators for Workspace operations.

The functions raise :class:`ServiceError` with appropriate HTTP status
codes when validation fails. They are used exclusively by
``WorkspaceService`` to keep business logic in the service layer.
"""

from ..models.workspace import Workspace
from ..services.base import ServiceError  # Import ServiceError from backend.shared services base


def validate_workspace_slug_unique(name: str, slug: str, organization) -> None:
    """Ensure the workspace slug is unique within the given organization.

    Args:
        name: Human readable workspace name (unused but kept for API parity).
        slug: Desired slug.
        organization: Organization instance the workspace will belong to.
    Raises:
        ServiceError: If a workspace with the same slug already exists in the
            organization (HTTP 409 Conflict).
    """
    if Workspace.objects.filter(organization=organization, slug=slug).exists():
        raise ServiceError("Workspace slug already exists in this organization", 409)


def validate_workspace_settings(settings: dict) -> None:
    """Validate ``settings`` against the JSON schema.

    The schema lives at ``backend/apps/organizations/validators/workspace_settings_schema.json``.
    ``jsonschema`` is used for validation.
    """
    import json
    import os

    from jsonschema import ValidationError as JsonSchemaError
    from jsonschema import validate as json_validate

    schema_path = os.path.join(os.path.dirname(__file__), "workspace_settings_schema.json")
    try:
        with open(schema_path, encoding="utf-8") as f:
            schema = json.load(f)
    except FileNotFoundError as exc:
        raise ServiceError("Workspace settings schema not found", 500) from exc

    try:
        json_validate(instance=settings, schema=schema)
    except JsonSchemaError as exc:
        raise ServiceError(f"Invalid workspace settings: {exc.message}", 400)
