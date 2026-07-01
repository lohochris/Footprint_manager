"""Ownership service layer for the organizations app.

Provides transactional ownership transfer for organizations (and optionally workspaces).
All mutating actions are logged to AuditLog with full request context.
"""

from apps.audit.models.audit_log import AuditLog
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from ..models.organization import Organization
from ..models.organization_member import OrganizationMember
from ..validators import validate_ownership_transfer
from .base import ServiceError
from apps.investigations.services.base_service import BaseService


class OwnershipService:
    """Service encapsulating ownership transfer logic."""

    @staticmethod
    def transfer_organization_ownership(
        organization: Organization,
        current_owner,
        new_owner,
        request_context: dict | None = None,
    ):
        """Transfer ownership of an organization via the service execution pipeline.

        Args:
            organization: Organization instance.
            current_owner: User instance currently owning the org.
            new_owner: User instance to become the new owner.
            request_context: Optional dict with ``request_id``, ``ip_address``, ``user_agent``.
        """
        payload = {
            "organization": organization,
            "current_owner": current_owner,
            "new_owner": new_owner,
            "request_context": request_context,
        }
        return BaseService.execute(
            operation="ownership.transfer",
            performed_by=current_owner,
            tenant=organization,
            payload=payload,
        )

# Private implementation for ownership transfer, preserving transaction and locking.
def _transfer_ownership_impl(organization, current_owner, new_owner, request_context=None):
    """Core ownership transfer logic preserved from original implementation."""
    # Validation – ensure both users are members and prevent removing last owner
    validate_ownership_transfer(current_owner, new_owner, organization)
    try:
        with transaction.atomic():
            # Lock the organization row for update to avoid race conditions
            org_locked = Organization.objects.select_for_update().get(pk=organization.pk)
            # Update owner reference
            org_locked.owner = new_owner
            org_locked.save()
            # Update membership roles
            # Current owner becomes admin
            OrganizationMember.objects.filter(
                organization=org_locked, user=current_owner
            ).update(role="admin")
            # New owner role set to owner (create if missing)
            OrganizationMember.objects.update_or_create(
                organization=org_locked,
                user=new_owner,
                defaults={"role": "owner"},
            )
            # Prepare audit log details
            details = {
                "org_id": str(org_locked.id),
                "new_owner_id": new_owner.id,
                "previous_owner_id": current_owner.id,
            }
            if request_context:
                details.update({
                    "request_id": request_context.get("request_id"),
                    "ip_address": request_context.get("ip_address"),
                    "user_agent": request_context.get("user_agent"),
                })
            AuditLog.objects.create(
                action="organization_ownership_transferred",
                performed_by=current_owner,
                organization=org_locked,
                details=details,
            )
            return org_locked
    except ObjectDoesNotExist:
        raise ServiceError("Organization not found.", 404)

# Pipeline handler wrapper for OwnershipService
def ownership_transfer(**payload):
    """Wrapper for OwnershipService._transfer_ownership_impl."""
    return _transfer_ownership_impl(**payload)
