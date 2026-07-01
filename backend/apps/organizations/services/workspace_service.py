"""Workspace service layer for the organizations app.

Handles creation, update, archive/restore, and mutation of workspaces with
audit logging. All mutating actions run inside a transaction and enforce
tenant isolation, role based authorization, and business rules.
"""


from apps.audit.models.audit_log import AuditLog
from django.db import transaction

from backend.shared.constants.roles import (
    ROLE_ADMIN,
    ROLE_MANAGER,
    ROLE_OWNER,
)

from ..models.organization import Organization
from ..models.organization_member import OrganizationMember
from ..models.workspace import Workspace
from ..models.workspace_member import WorkspaceMember
from ..selectors.workspace import (
    get_workspace_by_id,
    list_workspaces_for_organization,
)
from ..validators.workspace import (
    validate_workspace_settings,
    validate_workspace_slug_unique,
)
from .base import ServiceError
from apps.common.pipeline.core import BaseService


class WorkspaceService:
    """Service class encapsulating workspace‑related business rules."""

    @staticmethod
    def _log_action(
        action: str,
        performed_by,
        organization: Organization | None = None,
        workspace: Workspace | None = None,
        outcome: str = "success",
        details: dict | None = None,
        **extra,
    ):
        """Create an :class:`AuditLog` entry.

        ``details`` is merged with ``extra`` and stored in the JSON ``details`` field.
        """
        if details is None:
            details = {}
        AuditLog.objects.create(
            action=action,
            performed_by=performed_by,
            organization=organization,
            workspace=workspace,
            outcome=outcome,
            details={**details, **extra},
        )

    # ---------------------------------------------------------------------
    # Creation
    # ---------------------------------------------------------------------
    @staticmethod
    def create_workspace(
        name: str,
        slug: str,
        organization: Organization,
        owner,
        **extra,
    ) -> Workspace:
        """Create a new workspace within an organization.

        * Validates that the organization is not archived.
        * Enforces slug uniqueness per organization.
        * Creates a ``WorkspaceMember`` entry with the *owner* role.
        * Emits an audit‑log entry.
        """
        payload = {
            "name": name,
            "slug": slug,
            "organization": organization,
            "owner": owner,
            **extra,
        }
        result = BaseService.execute(
            operation="workspace.create",
            performed_by=owner,
            tenant=organization,
            payload=payload,
        )
        return result.payload

    # ---------------------------------------------------------------------
    # Retrieval
    # ---------------------------------------------------------------------
    @staticmethod
    def get_workspace(user, workspace_id: int) -> Workspace:
        """Retrieve a workspace ensuring tenant isolation."""
        return get_workspace_by_id(user, workspace_id)

    @staticmethod
    def list_organization_workspaces(user, organization_id: int):
        """Return all workspaces belonging to an organization the user can access."""
        return list_workspaces_for_organization(user, organization_id)

    # ---------------------------------------------------------------------
    # Update
    # ---------------------------------------------------------------------
    @staticmethod
    def update_workspace(workspace: Workspace, user, **updates) -> Workspace:
        """Update mutable fields of a workspace.

        * The ``slug`` field is immutable after creation.
        * Only owners, admins or managers may update.
        """
        payload = {"workspace": workspace, "user": user, **updates}
        result = BaseService.execute(
            operation="workspace.update",
            performed_by=user,
            tenant=workspace.organization,
            payload=payload,
        )
        return result.payload

    # ---------------------------------------------------------------------
    # Archive / Restore
    # ---------------------------------------------------------------------
    @staticmethod
    def archive_workspace(workspace: Workspace, user) -> Workspace:
        """Soft‑delete a workspace.

        Only owners, admins or managers may archive.
        """
        payload = {"workspace": workspace, "user": user}
        result = BaseService.execute(
            operation="workspace.archive",
            performed_by=user,
            tenant=workspace.organization,
            payload=payload,
        )
        return result.payload

    @staticmethod
    def restore_workspace(workspace: Workspace, user) -> Workspace:
        """Restore a previously archived workspace.

        Only owners, admins or managers may restore.
        """
        payload = {"workspace": workspace, "user": user}
        result = BaseService.execute(
            operation="workspace.restore",
            performed_by=user,
            tenant=workspace.organization,
            payload=payload,
        )
        return result.payload

    # ---------------------------------------------------------------------
    # Settings
    # ---------------------------------------------------------------------
    @staticmethod
    def update_workspace_settings(workspace: Workspace, user, settings: dict) -> Workspace:
        """Validate and persist the JSON ``settings`` field.

        Only owners, admins or managers may modify settings.
        """
        payload = {"workspace": workspace, "user": user, "settings": settings}
        result = BaseService.execute(
            operation="workspace.update_settings",
            performed_by=user,
            tenant=workspace.organization,
            payload=payload,
        )
        return result.payload

    # ---------------------------------------------------------------------
    # Visibility / Status
    # ---------------------------------------------------------------------
    @staticmethod
    def change_workspace_visibility(workspace: Workspace, user, visibility: str) -> Workspace:
        """Change the ``visibility`` field.

        Valid values are the choices defined on the model.
        """
        payload = {"workspace": workspace, "user": user, "visibility": visibility}
        result = BaseService.execute(
            operation="workspace.change_visibility",
            performed_by=user,
            tenant=workspace.organization,
            payload=payload,
        )
        return result.payload

    @staticmethod
    def change_workspace_status(workspace: Workspace, user, status: str) -> Workspace:
        """Change the ``status`` field (active / inactive / suspended)."""
        payload = {"workspace": workspace, "user": user, "status": status}
        result = BaseService.execute(
            operation="workspace.change_status",
            performed_by=user,
            tenant=workspace.organization,
            payload=payload,
        )
        return result.payload
