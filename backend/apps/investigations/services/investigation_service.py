from backend.apps.audit.models import AuditLog
from django.db import transaction
from django.utils import timezone

from ..models.activity import InvestigationActivity
from ..models.investigation import Investigation


class InvestigationService:
    """Business logic for Investigation lifecycle management.

    All state‑changing operations are wrapped in atomic transactions and emit
    audit log entries. Validation of input is delegated to validators where appropriate.
    """

    @staticmethod
    def _log_action(user, action, instance, details=None):
        AuditLog.objects.create(
            user=user,
            action=action,
            object_id=instance.pk,
            object_repr=str(instance),
            details=details or {},
            timestamp=timezone.now(),
        )

    @staticmethod
    def generate_case_number(organization):
        """Generate a unique case number scoped to the organization.
        Format: ``ORG-{YYYY}{MM}{DD}-{seq}`` where ``seq`` is a zero‑padded counter.
        """
        date_str = timezone.now().strftime("%Y%m%d")
        prefix = f"{organization.slug.upper()}-{date_str}"
        existing = Investigation.objects.filter(case_number__startswith=prefix).count()
        seq = existing + 1
        return f"{prefix}-{seq:04d}"

    @staticmethod
    def create_investigation(user, organization, workspace, data):
        """Create a new Investigation.
        ``data`` is a dict containing the fields accepted by the serializer.
        """
        with transaction.atomic():
            case_number = InvestigationService.generate_case_number(organization)
            investigation = Investigation.objects.create(
                case_number=case_number,
                organization=organization,
                workspace=workspace,
                owner=user,
                created_by=user,
                **data,
            )
            investigation.assigned_investigators.add(user)
            InvestigationService._log_action(user, "create_investigation", investigation)
            return investigation

    @staticmethod
    def update_investigation(user, investigation, data):
        """Update mutable fields of an Investigation.
        ``data`` should be validated beforehand.
        """
        with transaction.atomic():
            for attr, value in data.items():
                setattr(investigation, attr, value)
            investigation.updated_by = user
            investigation.save()
            InvestigationService._log_action(user, "update_investigation", investigation, details=data)
            return investigation

    @staticmethod
    def assign_investigators(user, investigation, investigator_ids):
        """Assign additional investigators to the investigation.
        ``investigator_ids`` is an iterable of user PKs.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        investigators = User.objects.filter(pk__in=investigator_ids)
        with transaction.atomic():
            investigation.assigned_investigators.add(*investigators)
            InvestigationService._log_action(user, "assign_investigators", investigation, details={"ids": list(investigator_ids)})
            return investigation

    @staticmethod
    def change_status(user, investigation, new_status):
        """Change the status of an investigation, respecting allowed transitions.
        Validation of transition rules is assumed to be performed by validators.
        """
        with transaction.atomic():
            old_status = investigation.status
            investigation.status = new_status
            investigation.updated_by = user
            investigation.save()
            InvestigationService._log_action(
                user,
                "change_status",
                investigation,
                details={"from": old_status, "to": new_status},
            )
            InvestigationActivity.objects.create(
                investigation=investigation,
                actor=user,
                type="status_change",
                payload={"from": old_status, "to": new_status},
            )
            return investigation

    @staticmethod
    def archive(user, investigation):
        with transaction.atomic():
            investigation.is_archived = True
            investigation.updated_by = user
            investigation.save()
            InvestigationService._log_action(user, "archive_investigation", investigation)
            return investigation

    @staticmethod
    def restore(user, investigation):
        with transaction.atomic():
            investigation.is_archived = False
            investigation.updated_by = user
            investigation.save()
            InvestigationService._log_action(user, "restore_investigation", investigation)
            return investigation

    @staticmethod
    def soft_delete(user, investigation):
        with transaction.atomic():
            investigation.is_deleted = True
            investigation.deleted_at = timezone.now()
            investigation.updated_by = user
            investigation.save()
            InvestigationService._log_action(user, "delete_investigation", investigation)
            return investigation

    @staticmethod
    def transfer_ownership(user, investigation, new_owner):
        """Transfer ownership to another user within the same organization.
        The previous owner remains an assigned investigator.
        """
        with transaction.atomic():
            old_owner = investigation.owner
            investigation.owner = new_owner
            investigation.updated_by = user
            investigation.save()
            investigation.assigned_investigators.add(old_owner)
            InvestigationService._log_action(
                user,
                "transfer_ownership",
                investigation,
                details={"from": old_owner.pk, "to": new_owner.pk},
            )
            InvestigationActivity.objects.create(
                investigation=investigation,
                actor=user,
                type="ownership_transfer",
                payload={"from": old_owner.pk, "to": new_owner.pk},
            )
            return investigation

    @staticmethod
    def add_activity(user, investigation, activity_type, payload=None):
        payload = payload or {}
        with transaction.atomic():
            activity = InvestigationActivity.objects.create(
                investigation=investigation,
                actor=user,
                type=activity_type,
                payload=payload,
            )
            InvestigationService._log_action(user, f"add_activity_{activity_type}", investigation, details=payload)
            return activity
