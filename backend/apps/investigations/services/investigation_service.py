from django.conf import settings
from django.db import transaction
from django.utils import timezone

from backend.apps.common.pipeline.core import BaseService
from backend.apps.investigations.models import (
    Investigation,
    InvestigationMember,
    InvestigationMemberRole,
    InvestigationStatus,
    PermissionLevel,
)


class InvestigationService:
    """Business logic for Investigation lifecycle management.

    Delegates authorization, validation, auditing, and timeline triggers
    to the Pipeline framework execution stages.
    """

    @staticmethod
    def create_investigation(user, organization, workspace, data):
        """Create a new Investigation via the pipeline."""
        payload = {
            "workspace": workspace,
            "data": data,
        }
        result = BaseService.execute(
            operation="investigation.create",
            performed_by=user,
            tenant=organization,
            payload=payload,
        )
        if not result.success:
            raise result.error
        return result.data

    @staticmethod
    def update_investigation(user, investigation, data):
        """Update mutable fields of an Investigation via the pipeline."""
        payload = {
            "investigation": investigation,
            "data": data,
        }
        result = BaseService.execute(
            operation="investigation.update",
            performed_by=user,
            tenant=investigation.organization,
            payload=payload,
        )
        if not result.success:
            raise result.error
        return result.data

    @staticmethod
    def assign_investigators(user, investigation, investigator_ids):
        """Assign additional investigators to the investigation via the pipeline."""
        payload = {
            "investigation": investigation,
            "investigator_ids": investigator_ids,
        }
        result = BaseService.execute(
            operation="investigation.assign_members",
            performed_by=user,
            tenant=investigation.organization,
            payload=payload,
        )
        if not result.success:
            raise result.error
        return result.data

    @staticmethod
    def change_status(user, investigation, new_status):
        """Change the status of an investigation via the pipeline."""
        payload = {
            "investigation": investigation,
            "new_status": new_status,
        }
        result = BaseService.execute(
            operation="investigation.change_status",
            performed_by=user,
            tenant=investigation.organization,
            payload=payload,
        )
        if not result.success:
            raise result.error
        return result.data

    @staticmethod
    def archive(user, investigation):
        """Archive an investigation via the pipeline."""
        payload = {
            "investigation": investigation,
        }
        result = BaseService.execute(
            operation="investigation.archive",
            performed_by=user,
            tenant=investigation.organization,
            payload=payload,
        )
        if not result.success:
            raise result.error
        return result.data

    @staticmethod
    def restore_investigation(user, investigation):
        """Restore a previously archived investigation via the pipeline."""
        payload = {
            "investigation": investigation,
        }
        result = BaseService.execute(
            operation="investigation.restore",
            performed_by=user,
            tenant=investigation.organization,
            payload=payload,
        )
        if not result.success:
            raise result.error
        return result.data

    @staticmethod
    def soft_delete(user, investigation):
        """Soft-delete an investigation via the pipeline."""
        payload = {
            "investigation": investigation,
        }
        result = BaseService.execute(
            operation="investigation.soft_delete",
            performed_by=user,
            tenant=investigation.organization,
            payload=payload,
        )
        if not result.success:
            raise result.error
        return result.data

    @staticmethod
    def transfer_ownership(user, investigation, new_owner):
        """Transfer investigation ownership via the pipeline."""
        payload = {
            "investigation": investigation,
            "new_owner": new_owner,
        }
        result = BaseService.execute(
            operation="investigation.transfer_ownership",
            performed_by=user,
            tenant=investigation.organization,
            payload=payload,
        )
        if not result.success:
            raise result.error
        return result.data


# ===========================================================================
# Core Private Service Implementations (Atomic Operations)
# ===========================================================================

def _generate_case_number(organization):
    """Generate a unique case number scoped to the organization."""
    date_str = timezone.now().strftime("%Y%m%d")
    prefix = f"{organization.slug.upper()}-{date_str}"
    existing = Investigation.objects.filter(
        organization=organization,
        case_number__startswith=prefix,
    ).count()
    seq = existing + 1
    return f"{prefix}-{seq:04d}"


def _create_investigation_impl(user, organization, workspace, data):
    with transaction.atomic():
        case_number = _generate_case_number(organization)
        investigation = Investigation.objects.create(
            case_number=case_number,
            organization=organization,
            workspace=workspace,
            owner=user,
            created_by=user,
            **data,
        )
        # Automatically register creator as Owner
        InvestigationMember.objects.create(
            investigation=investigation,
            user=user,
            role=InvestigationMemberRole.OWNER,
            permission_level=PermissionLevel.ADMIN,
            created_by=user,
        )
        return investigation


def _update_investigation_impl(user, investigation, data):
    with transaction.atomic():
        for attr, value in data.items():
            setattr(investigation, attr, value)
        investigation.updated_by = user
        investigation.save()
        return investigation


def _assign_investigators_impl(user, investigation, investigator_ids):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    investigators = User.objects.filter(pk__in=investigator_ids)

    with transaction.atomic():
        for inv in investigators:
            InvestigationMember.objects.get_or_create(
                investigation=investigation,
                user=inv,
                defaults={
                    "role": InvestigationMemberRole.INVESTIGATOR,
                    "permission_level": PermissionLevel.WRITE,
                    "created_by": user,
                },
            )
        return investigation


def _change_status_impl(user, investigation, new_status):
    with transaction.atomic():
        investigation.status = new_status
        investigation.updated_by = user
        if new_status == InvestigationStatus.COMPLETED:
            investigation.closed_at = timezone.now()
        investigation.save()
        return investigation


def _archive_impl(user, investigation):
    with transaction.atomic():
        investigation.is_archived = True
        investigation.status = InvestigationStatus.ARCHIVED
        investigation.archived_at = timezone.now()
        investigation.updated_by = user
        investigation.save()
        return investigation


def _restore_impl(user, investigation):
    with transaction.atomic():
        investigation.is_archived = False
        investigation.status = InvestigationStatus.ACTIVE
        investigation.archived_at = None
        investigation.updated_by = user
        investigation.save()
        return investigation


def _soft_delete_impl(user, investigation):
    with transaction.atomic():
        investigation.soft_delete()
        investigation.updated_by = user
        investigation.save(update_fields=["updated_by"])
        return investigation


def _transfer_ownership_impl(user, investigation, new_owner):
    with transaction.atomic():
        old_owner = investigation.owner
        investigation.owner = new_owner
        investigation.updated_by = user
        investigation.save()

        # Demote current owner to Investigator role
        InvestigationMember.objects.filter(
            investigation=investigation,
            user=old_owner,
        ).update(
            role=InvestigationMemberRole.INVESTIGATOR,
            permission_level=PermissionLevel.WRITE,
        )

        # Elevate new owner to Owner role
        InvestigationMember.objects.update_or_create(
            investigation=investigation,
            user=new_owner,
            defaults={
                "role": InvestigationMemberRole.OWNER,
                "permission_level": PermissionLevel.ADMIN,
                "created_by": user,
            },
        )
        return investigation


# ===========================================================================
# Pipeline Wrappers (Interface adapters for registry)
# ===========================================================================

def investigation_create(**payload):
    return _create_investigation_impl(**payload)


def investigation_update(**payload):
    return _update_investigation_impl(**payload)


def investigation_assign_members(**payload):
    return _assign_investigators_impl(**payload)


def investigation_change_status(**payload):
    return _change_status_impl(**payload)


def investigation_archive(**payload):
    return _archive_impl(**payload)


def investigation_restore(**payload):
    return _restore_impl(**payload)


def investigation_soft_delete(**payload):
    return _soft_delete_impl(**payload)


def investigation_transfer_ownership(**payload):
    return _transfer_ownership_impl(**payload)
