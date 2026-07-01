"""Organization service layer for the organizations app.

Provides business logic for creating, updating, deleting, restoring, and transferring
ownership of organizations. All mutating operations are logged to the
`AuditLog` model.
"""


from apps.audit.models.audit_log import AuditLog
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from ..models.organization import Organization
from ..models.organization_member import OrganizationMember
from ..selectors.organization import (
    get_organization_by_id,
    list_organizations_for_user,
)
from ..validators import (
    validate_organization_slug_unique,
    validate_ownership_transfer,
)
from .base import ServiceError


class OrganizationService:
    """Service class encapsulating organization‑related business rules."""

    @staticmethod
    def _log_action(action: str, performed_by, organization: Organization | None = None, outcome: str = "success", details: dict | None = None, **extra):
        """Helper to create an AuditLog entry.

        ``details`` is merged with ``extra`` and stored in the JSON ``details`` field.
        """
        if details is None:
            details = {}
        AuditLog.objects.create(
            action=action,
            performed_by=performed_by,
            organization=organization,
            outcome=outcome,
            details={**details, **extra},
        )

    @staticmethod
    def create_organization(name: str, slug: str, owner, **extra):
        """Create a new organization.

        Parameters
        ----------
        name: str
            Human‑readable organization name.
        slug: str
            Unique, immutable identifier.
        owner: User
            User instance that will own the organization.
        extra: dict
            Additional fields passed to the model (e.g., description, settings).
        """
        validate_organization_slug_unique(slug)
        with transaction.atomic():
            organization = Organization.objects.create(
                name=name, slug=slug, owner=owner, **extra
            )
            # Create owner membership with role "owner"
            OrganizationMember.objects.create(
                organization=organization, user=owner, role="owner"
            )
            OrganizationService._log_action(
                action="organization_created",
                performed_by=owner,
                organization=organization,
                details={"org_id": str(organization.id), "slug": slug},
            )
        return organization

    @staticmethod
    def get_organization(user, org_id: int) -> Organization:
        """Retrieve an organization for a user, enforcing tenant isolation."""
        return get_organization_by_id(user, org_id)

    @staticmethod
    def list_user_organizations(user):
        """Return all organizations the user belongs to."""
        return list_organizations_for_user(user)

    @staticmethod
    def update_organization(organization: Organization, user, **updates):
        """Update mutable fields of an organization.

        The `slug` field is immutable and cannot be changed.
        Only the organization owner can perform updates.
        """
        if organization.owner.id != user.id:
            raise ServiceError("Only the organization owner may update the organization.", 403)
        if "slug" in updates and updates["slug"] != organization.slug:
            raise ServiceError("Organization slug is immutable and cannot be changed.", 400)
        for attr, value in updates.items():
            setattr(organization, attr, value)
        organization.save()
        OrganizationService._log_action(
            action="organization_updated",
            performed_by=user,
            organization=organization,
            details={"org_id": str(organization.id), "updates": updates},
        )
        return organization

    @staticmethod
    def archive_organization(organization: Organization, user):
        """Soft‑delete (archive) an organization by setting its status to ``inactive``.
        Only the owner can perform this action.
        """
        if organization.owner.id != user.id:
            raise ServiceError("Only the organization owner may archive the organization.", 403)
        organization.status = "inactive"
        organization.save()
        OrganizationService._log_action(
            action="organization_archived",
            performed_by=user,
            organization=organization,
            details={"org_id": str(organization.id)},
        )
        return organization

    @staticmethod
    def restore_organization(organization: Organization, user):
        """Restore an archived organization by setting its status back to ``active``.
        Only the owner may restore.
        """
        if organization.owner.id != user.id:
            raise ServiceError("Only the organization owner may restore the organization.", 403)
        if organization.status != "inactive":
            raise ServiceError("Organization is not archived.", 400)
        organization.status = "active"
        organization.save()
        OrganizationService._log_action(
            action="organization_restored",
            performed_by=user,
            organization=organization,
            details={"org_id": str(organization.id)},
        )
        return organization

    @staticmethod
    def update_organization_settings(organization: Organization, user, settings: dict):
        """Validate and update the JSON ``settings`` field.
        Validation should be performed against the approved JSON schema (not shown here).
        """
        if organization.owner.id != user.id:
            raise ServiceError("Only the organization owner may update settings.", 403)
        # Placeholder for JSON schema validation
        organization.settings = settings
        organization.save()
        OrganizationService._log_action(
            action="organization_settings_updated",
            performed_by=user,
            organization=organization,
            details={"org_id": str(organization.id), "settings": settings},
        )
        return organization

    @staticmethod
    def change_subscription_tier(organization: Organization, user, tier: str):
        """Change the subscription tier for an organization.
        Only the owner may change the tier.
        """
        if organization.owner.id != user.id:
            raise ServiceError("Only the organization owner may change subscription tier.", 403)
        organization.subscription_tier = tier
        organization.save()
        OrganizationService._log_action(
            action="organization_subscription_changed",
            performed_by=user,
            organization=organization,
            details={"org_id": str(organization.id), "new_tier": tier},
        )
        return organization

    @staticmethod
    def change_organization_status(organization: Organization, user, status: str):
        """Change the status (active/inactive/suspended) of an organization.
        Only the owner may change status.
        """
        if organization.owner.id != user.id:
            raise ServiceError("Only the organization owner may change status.", 403)
        if status not in {"active", "inactive", "suspended"}:
            raise ServiceError("Invalid organization status.", 400)
        organization.status = status
        organization.save()
        OrganizationService._log_action(
            action="organization_status_changed",
            performed_by=user,
            organization=organization,
            details={"org_id": str(organization.id), "new_status": status},
        )
        return organization

    @staticmethod
    def transfer_ownership(organization: Organization, current_owner, new_owner):
        """Transfer organization ownership atomically.

        Both users must be members of the organization. The operation is wrapped
        in a database transaction and uses ``SELECT ... FOR UPDATE`` to avoid
        race conditions.
        """
        validate_ownership_transfer(current_owner, new_owner, organization)
        try:
            with transaction.atomic():
                # Lock the organization row for update
                org_locked = Organization.objects.select_for_update().get(pk=organization.pk)
                # Update owner reference
                org_locked.owner = new_owner
                org_locked.save()
                # Update membership roles
                OrganizationMember.objects.filter(
                    organization=org_locked, user=current_owner
                ).update(role="admin")
                OrganizationMember.objects.update_or_create(
                    organization=org_locked,
                    user=new_owner,
                    defaults={"role": "owner"},
                )
                OrganizationService._log_action(
                    action="organization_ownership_transferred",
                    performed_by=current_owner,
                    organization=org_locked,
                    details={
                        "org_id": str(org_locked.id),
                        "new_owner_id": new_owner.id,
                        "previous_owner_id": current_owner.id,
                    },
                )
                return org_locked
        except ObjectDoesNotExist:
            raise ServiceError("Organization not found.", 404)
