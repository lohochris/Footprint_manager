"""Compatibility layer allowing existing callers to continue using
`OrganizationService` static methods while internally routing through the
Service Execution Pipeline.
"""

from typing import Any

from backend.apps.common.pipeline.core import BaseService

from .organization_service import OrganizationService as _OriginalService


class OrganizationServiceCompat:
    @staticmethod
    def create_organization(name: str, slug: str, owner, **extra):
        payload = {"name": name, "slug": slug, "owner": owner, **extra}
        return BaseService.execute(
            operation="organization.create",
            performed_by=owner,
            tenant=owner,
            payload=payload,
        )

    @staticmethod
    def get_organization(user, org_id: int):
        # Direct call, no pipeline needed for read‑only operation
        return _OriginalService.get_organization(user, org_id)

    @staticmethod
    def list_user_organizations(user):
        return _OriginalService.list_user_organizations(user)

    @staticmethod
    def update_organization(organization: Any, user, **updates):
        payload = {"organization": organization, "user": user, **updates}
        return BaseService.execute(
            operation="organization.update",
            performed_by=user,
            tenant=user,
            payload=payload,
        )

    @staticmethod
    def archive_organization(organization: Any, user):
        return BaseService.execute(
            operation="organization.archive",
            performed_by=user,
            tenant=user,
            payload={"organization": organization, "user": user},
        )

    @staticmethod
    def restore_organization(organization: Any, user):
        return BaseService.execute(
            operation="organization.restore",
            performed_by=user,
            tenant=user,
            payload={"organization": organization, "user": user},
        )

    @staticmethod
    def update_organization_settings(organization, user, settings: dict):
        return _OriginalService.update_organization_settings(organization, user, settings)

    @staticmethod
    def change_subscription_tier(organization, user, tier: str):
        return _OriginalService.change_subscription_tier(organization, user, tier)

    @staticmethod
    def change_organization_status(organization, user, status: str):
        return _OriginalService.change_organization_status(organization, user, status)

    @staticmethod
    def transfer_ownership(organization, current_owner, new_owner):
        return _OriginalService.transfer_ownership(organization, current_owner, new_owner)

    @staticmethod
    def _log_action(*args, **kwargs):
        # Preserve legacy logging for any direct calls
        return _OriginalService._log_action(*args, **kwargs)

    # Preserve any other static helpers if needed

# Alias for backward compatibility
OrganizationService = OrganizationServiceCompat
