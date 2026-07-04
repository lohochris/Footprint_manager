from django.core.exceptions import PermissionDenied, ValidationError
from backend.apps.common.pipeline.core import PipelineContext, PipelineStage
from backend.apps.audit.models.audit_log import AuditLog
from backend.apps.investigations.models import (
    Investigation,
    InvestigationMember,
    InvestigationTimelineEvent,
    TimelineEventType,
    InvestigationMemberRole,
    PermissionLevel,
)
from backend.apps.investigations.validators.investigation_validator import (
    validate_status_transition,
    validate_priority,
    validate_tags,
    validate_investigation_tenancy,
    validate_ownership_transfer,
)
from backend.apps.investigations.validators.metadata import validate_investigation_metadata


# --- Helper Authorization Functions ---

def _enforce_member_access(investigation, user):
    """Raise PermissionDenied if the user is not associated with the investigation."""
    if investigation.owner == user or investigation.lead_investigator == user:
        return
    exists = InvestigationMember.objects.filter(
        investigation=investigation,
        user=user,
        active=True
    ).exists()
    if not exists:
        raise PermissionDenied("User is not an authorized member of this investigation.")


def _enforce_role_access(investigation, user, allowed_roles):
    """Enforce that the user has one of the allowed roles (or is the owner/lead)."""
    if investigation.owner == user or investigation.lead_investigator == user:
        return
    try:
        member = InvestigationMember.objects.get(
            investigation=investigation,
            user=user,
            active=True
        )
        if member.role not in allowed_roles:
            raise PermissionDenied(f"User role '{member.role}' is not authorized for this operation.")
    except InvestigationMember.DoesNotExist:
        raise PermissionDenied("User is not authorized for this operation.")


# ===========================================================================
# 1. CREATE OPERATION STAGES
# ===========================================================================

class CreateInvestigationValidationStage(PipelineStage):
    priority = 100
    name = "ValidationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        data = ctx.payload.get("data", {})
        validate_investigation_tenancy(ctx.tenant, ctx.performed_by, ctx.payload.get("workspace"))

        if "priority" in data:
            validate_priority(data["priority"])
        if "tags" in data:
            validate_tags(data["tags"])
        if "metadata" in data:
            validate_investigation_metadata(data["metadata"])

        return ctx


class CreateInvestigationAuthorizationStage(PipelineStage):
    priority = 200
    name = "AuthorizationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        # Tenancy validation already verifies membership in organization.
        # Any authenticated organization member is permitted to create an investigation.
        return ctx


class CreateInvestigationBusinessStage(PipelineStage):
    priority = 300
    name = "BusinessStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        from .investigation_service import _create_investigation_impl
        result = _create_investigation_impl(
            user=ctx.performed_by,
            organization=ctx.tenant,
            workspace=ctx.payload.get("workspace"),
            data=ctx.payload.get("data", {}),
        )
        return ctx.with_updates(payload=result)


class CreateInvestigationAuditStage(PipelineStage):
    priority = 400
    name = "AuditStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload
        AuditLog.objects.create(
            action="investigation_created",
            performed_by=ctx.performed_by,
            organization=ctx.tenant,
            outcome="success",
            details={
                "investigation_id": str(investigation.id),
                "case_number": investigation.case_number,
            },
        )
        return ctx


class CreateInvestigationTimelineStage(PipelineStage):
    priority = 500
    name = "TimelineStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload
        InvestigationTimelineEvent.objects.create(
            investigation=investigation,
            event_type=TimelineEventType.CREATED,
            description=f"Investigation created by {ctx.performed_by.username}.",
        )
        return ctx


# ===========================================================================
# 2. UPDATE OPERATION STAGES
# ===========================================================================

class UpdateInvestigationValidationStage(PipelineStage):
    priority = 100
    name = "ValidationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload.get("investigation")
        data = ctx.payload.get("data", {})

        if "status" in data:
            validate_status_transition(investigation.status, data["status"])
        if "priority" in data:
            validate_priority(data["priority"])
        if "tags" in data:
            validate_tags(data["tags"])
        if "metadata" in data:
            validate_investigation_metadata(data["metadata"])

        return ctx


class UpdateInvestigationAuthorizationStage(PipelineStage):
    priority = 200
    name = "AuthorizationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload.get("investigation")
        # Leads and Owners can update details
        _enforce_role_access(
            investigation,
            ctx.performed_by,
            [InvestigationMemberRole.OWNER, InvestigationMemberRole.LEAD],
        )
        return ctx


class UpdateInvestigationBusinessStage(PipelineStage):
    priority = 300
    name = "BusinessStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        from .investigation_service import _update_investigation_impl
        result = _update_investigation_impl(
            user=ctx.performed_by,
            investigation=ctx.payload.get("investigation"),
            data=ctx.payload.get("data", {}),
        )
        return ctx.with_updates(payload=result)


class UpdateInvestigationAuditStage(PipelineStage):
    priority = 400
    name = "AuditStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload
        AuditLog.objects.create(
            action="investigation_updated",
            performed_by=ctx.performed_by,
            organization=ctx.tenant,
            outcome="success",
            details={
                "investigation_id": str(investigation.id),
                "case_number": investigation.case_number,
            },
        )
        return ctx


# ===========================================================================
# 3. ASSIGN MEMBERS OPERATION STAGES
# ===========================================================================

class AssignMembersValidationStage(PipelineStage):
    priority = 100
    name = "ValidationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        # Tenancy checks
        investigation = ctx.payload.get("investigation")
        from django.contrib.auth import get_user_model
        User = get_user_model()
        investigators = User.objects.filter(pk__in=ctx.payload.get("investigator_ids", []))

        for inv in investigators:
            validate_investigation_tenancy(investigation.organization, inv)

        return ctx


class AssignMembersAuthorizationStage(PipelineStage):
    priority = 200
    name = "AuthorizationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload.get("investigation")
        _enforce_role_access(
            investigation,
            ctx.performed_by,
            [InvestigationMemberRole.OWNER, InvestigationMemberRole.LEAD],
        )
        return ctx


class AssignMembersBusinessStage(PipelineStage):
    priority = 300
    name = "BusinessStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        from .investigation_service import _assign_investigators_impl
        result = _assign_investigators_impl(
            user=ctx.performed_by,
            investigation=ctx.payload.get("investigation"),
            investigator_ids=ctx.payload.get("investigator_ids", []),
        )
        return ctx.with_updates(payload=result)


class AssignMembersAuditStage(PipelineStage):
    priority = 400
    name = "AuditStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload
        AuditLog.objects.create(
            action="investigators_assigned",
            performed_by=ctx.performed_by,
            organization=ctx.tenant,
            outcome="success",
            details={
                "investigation_id": str(investigation.id),
                "case_number": investigation.case_number,
            },
        )
        return ctx


class AssignMembersTimelineStage(PipelineStage):
    priority = 500
    name = "TimelineStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload
        # Log to timeline
        InvestigationTimelineEvent.objects.create(
            investigation=investigation,
            event_type=TimelineEventType.MEMBER_ADDED,
            description="New investigators assigned to the investigation.",
        )
        return ctx


# ===========================================================================
# 4. CHANGE STATUS OPERATION STAGES
# ===========================================================================

class ChangeStatusValidationStage(PipelineStage):
    priority = 100
    name = "ValidationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload.get("investigation")
        new_status = ctx.payload.get("new_status")
        validate_status_transition(investigation.status, new_status)
        return ctx


class ChangeStatusAuthorizationStage(PipelineStage):
    priority = 200
    name = "AuthorizationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload.get("investigation")
        # Owner, lead, or active analyst can change status
        _enforce_role_access(
            investigation,
            ctx.performed_by,
            [InvestigationMemberRole.OWNER, InvestigationMemberRole.LEAD, InvestigationMemberRole.INVESTIGATOR],
        )
        return ctx


class ChangeStatusBusinessStage(PipelineStage):
    priority = 300
    name = "BusinessStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        from .investigation_service import _change_status_impl
        result = _change_status_impl(
            user=ctx.performed_by,
            investigation=ctx.payload.get("investigation"),
            new_status=ctx.payload.get("new_status"),
        )
        return ctx.with_updates(payload=result)


class ChangeStatusAuditStage(PipelineStage):
    priority = 400
    name = "AuditStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload
        AuditLog.objects.create(
            action="investigation_status_changed",
            performed_by=ctx.performed_by,
            organization=ctx.tenant,
            outcome="success",
            details={
                "investigation_id": str(investigation.id),
                "case_number": investigation.case_number,
                "status": investigation.status,
            },
        )
        return ctx


class ChangeStatusTimelineStage(PipelineStage):
    priority = 500
    name = "TimelineStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload
        InvestigationTimelineEvent.objects.create(
            investigation=investigation,
            event_type=TimelineEventType.STATUS_CHANGED,
            description=f"Investigation status changed to '{investigation.status}' by {ctx.performed_by.username}.",
        )
        return ctx


# ===========================================================================
# 5. ARCHIVE OPERATION STAGES
# ===========================================================================

class ArchiveValidationStage(PipelineStage):
    priority = 100
    name = "ValidationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        return ctx


class ArchiveAuthorizationStage(PipelineStage):
    priority = 200
    name = "AuthorizationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload.get("investigation")
        _enforce_role_access(
            investigation,
            ctx.performed_by,
            [InvestigationMemberRole.OWNER, InvestigationMemberRole.LEAD],
        )
        return ctx


class ArchiveBusinessStage(PipelineStage):
    priority = 300
    name = "BusinessStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        from .investigation_service import _archive_impl
        result = _archive_impl(
            user=ctx.performed_by,
            investigation=ctx.payload.get("investigation"),
        )
        return ctx.with_updates(payload=result)


class ArchiveAuditStage(PipelineStage):
    priority = 400
    name = "AuditStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload
        AuditLog.objects.create(
            action="investigation_archived",
            performed_by=ctx.performed_by,
            organization=ctx.tenant,
            outcome="success",
            details={
                "investigation_id": str(investigation.id),
                "case_number": investigation.case_number,
            },
        )
        return ctx


# ===========================================================================
# 6. RESTORE OPERATION STAGES
# ===========================================================================

class RestoreValidationStage(PipelineStage):
    priority = 100
    name = "ValidationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload.get("investigation")
        if not investigation.is_archived:
            raise ValidationError("Investigation is not archived.")
        return ctx


class RestoreAuthorizationStage(PipelineStage):
    priority = 200
    name = "AuthorizationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload.get("investigation")
        _enforce_role_access(
            investigation,
            ctx.performed_by,
            [InvestigationMemberRole.OWNER, InvestigationMemberRole.LEAD],
        )
        return ctx


class RestoreBusinessStage(PipelineStage):
    priority = 300
    name = "BusinessStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        from .investigation_service import _restore_impl
        result = _restore_impl(
            user=ctx.performed_by,
            investigation=ctx.payload.get("investigation"),
        )
        return ctx.with_updates(payload=result)


class RestoreAuditStage(PipelineStage):
    priority = 400
    name = "AuditStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload
        AuditLog.objects.create(
            action="investigation_restored",
            performed_by=ctx.performed_by,
            organization=ctx.tenant,
            outcome="success",
            details={
                "investigation_id": str(investigation.id),
                "case_number": investigation.case_number,
            },
        )
        return ctx


# ===========================================================================
# 7. SOFT DELETE OPERATION STAGES
# ===========================================================================

class SoftDeleteValidationStage(PipelineStage):
    priority = 100
    name = "ValidationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        return ctx


class SoftDeleteAuthorizationStage(PipelineStage):
    priority = 200
    name = "AuthorizationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload.get("investigation")
        _enforce_role_access(
            investigation,
            ctx.performed_by,
            [InvestigationMemberRole.OWNER, InvestigationMemberRole.LEAD],
        )
        return ctx


class SoftDeleteBusinessStage(PipelineStage):
    priority = 300
    name = "BusinessStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        from .investigation_service import _soft_delete_impl
        result = _soft_delete_impl(
            user=ctx.performed_by,
            investigation=ctx.payload.get("investigation"),
        )
        return ctx.with_updates(payload=result)


class SoftDeleteAuditStage(PipelineStage):
    priority = 400
    name = "AuditStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload
        AuditLog.objects.create(
            action="investigation_deleted",
            performed_by=ctx.performed_by,
            organization=ctx.tenant,
            outcome="success",
            details={
                "investigation_id": str(investigation.id),
                "case_number": investigation.case_number,
            },
        )
        return ctx


# ===========================================================================
# 8. TRANSFER OWNERSHIP OPERATION STAGES
# ===========================================================================

class TransferOwnershipValidationStage(PipelineStage):
    priority = 100
    name = "ValidationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload.get("investigation")
        new_owner = ctx.payload.get("new_owner")
        validate_ownership_transfer(investigation, investigation.owner, new_owner)
        return ctx


class TransferOwnershipAuthorizationStage(PipelineStage):
    priority = 200
    name = "AuthorizationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload.get("investigation")
        if investigation.owner != ctx.performed_by:
            raise PermissionDenied("Only the current owner can transfer ownership of this investigation.")
        return ctx


class TransferOwnershipBusinessStage(PipelineStage):
    priority = 300
    name = "BusinessStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        from .investigation_service import _transfer_ownership_impl
        result = _transfer_ownership_impl(
            user=ctx.performed_by,
            investigation=ctx.payload.get("investigation"),
            new_owner=ctx.payload.get("new_owner"),
        )
        return ctx.with_updates(payload=result)


class TransferOwnershipAuditStage(PipelineStage):
    priority = 400
    name = "AuditStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        investigation = ctx.payload
        AuditLog.objects.create(
            action="investigation_ownership_transferred",
            performed_by=ctx.performed_by,
            organization=ctx.tenant,
            outcome="success",
            details={
                "investigation_id": str(investigation.id),
                "case_number": investigation.case_number,
            },
        )
        return ctx
