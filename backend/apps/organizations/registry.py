from apps.common.pipeline.registry import PipelineRegistry

# Import the original service implementation
from .services import organization_service as org_srv
from .services.invitation_service import (
    invitation_create,
    invitation_accept,
    invitation_reject,
    invitation_cancel,
    invitation_resend,
    invitation_expire,
)
from .services.ownership_service import ownership_transfer


def _register_organization_operations():
    """Register organization operations with the PipelineRegistry.

    Each operation is mapped to a thin wrapper that forwards the payload to the
    original static methods on ``OrganizationService``.
    """

    def create(**payload):
        # Payload contains name, slug, owner, and any extra fields.
        return org_srv.OrganizationService.create_organization(**payload)

    def update(**payload):
        # Expected payload keys: organization, user, plus update fields.
        organization = payload.pop("organization")
        user = payload.pop("user")
        return org_srv.OrganizationService.update_organization(organization, user, **payload)

    def archive(**payload):
        organization = payload["organization"]
        user = payload["user"]
        return org_srv.OrganizationService.archive_organization(organization, user)

    def restore(**payload):
        organization = payload["organization"]
        user = payload["user"]
        return org_srv.OrganizationService.restore_organization(organization, user)

    # Register each operation under a dotted name.
    PipelineRegistry.register("organization.create", create)
    PipelineRegistry.register("organization.update", update)
    PipelineRegistry.register("organization.archive", archive)
    PipelineRegistry.register("organization.restore", restore)

# Register InvitationService operations
PipelineRegistry.register('invitation.create', invitation_create)
PipelineRegistry.register('invitation.accept', invitation_accept)
PipelineRegistry.register('invitation.reject', invitation_reject)
PipelineRegistry.register('invitation.cancel', invitation_cancel)
PipelineRegistry.register('invitation.resend', invitation_resend)
PipelineRegistry.register('ownership.transfer', ownership_transfer)

# Trigger registration at import time.
_register_organization_operations()
