import hashlib
import logging
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

logger = logging.getLogger(__name__)

from backend.apps.common.pipeline.core import PipelineContext, PipelineStage
from backend.apps.audit.models.audit_log import AuditLog
from backend.apps.evidence.models import (
    Evidence,
    EvidenceFile,
    EvidenceVersion,
    EvidenceCustodyEvent,
)
from backend.apps.evidence.storage.local import LocalStorageProvider
from backend.apps.evidence.scanners.noop import NoOpMalwareScanner


# Initialize default providers/scanners
storage_provider = LocalStorageProvider()
malware_scanner = NoOpMalwareScanner()


# ===========================================================================
# 1. UPLOAD EVIDENCE STAGES
# ===========================================================================

class UploadEvidenceValidationStage(PipelineStage):
    priority = 100
    name = "UploadValidationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        file_obj = ctx.payload.get("file")
        if not file_obj:
            raise ValidationError("File is required for evidence upload.")

        # Check file size (e.g., 5GB limit)
        max_size = 5 * 1024 * 1024 * 1024  # 5GB
        if file_obj.size > max_size:
            raise ValidationError("File size exceeds the 5GB limit.")

        # Scan for malware
        is_malicious, scan_details = malware_scanner.scan(file_obj)
        if is_malicious:
            raise ValidationError(f"Malware detected: {scan_details.get('reason', 'Unknown threat')}")

        ctx.metadata["scan_details"] = scan_details
        return ctx


class UploadEvidenceAuthorizationStage(PipelineStage):
    priority = 200
    name = "UploadAuthorizationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        # Tenancy isolation checks:
        # The organization/tenant must be resolved from the authenticated context
        user = ctx.performed_by
        tenant = ctx.tenant
        if not tenant:
            raise PermissionDenied("A valid tenant organization context is required.")

        # Ensure user belongs to the tenant
        if (
            hasattr(user, "organizations")
            and not user.organizations.filter(id=tenant.id).exists()
            and getattr(user, "organization", None) != tenant
        ):
            raise PermissionDenied("User is not authorized for this tenant organization.")

        return ctx


class UploadEvidenceStorageStage(PipelineStage):
    priority = 300
    name = "UploadStorageStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        file_obj = ctx.payload.get("file")
        if file_obj is None:
            raise ValidationError("File is required in payload.")
        # Save to storage provider
        # Create a unique path key
        filename = file_obj.name
        safe_path = f"evidence/{ctx.tenant.id}/{ctx.execution_id}/{filename}"
        storage_key = storage_provider.save(file_obj, safe_path)

        ctx.metadata["storage_key"] = storage_key
        ctx.metadata["original_filename"] = filename
        ctx.metadata["file_size"] = file_obj.size
        # Simple mime detection
        ctx.metadata["mime_type"] = getattr(file_obj, "content_type", "application/octet-stream")
        return ctx


class UploadEvidenceHashStage(PipelineStage):
    priority = 400
    name = "UploadHashStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        storage_key = ctx.metadata.get("storage_key")
        if storage_key is None:
            raise ValidationError("Storage key is missing in metadata.")
        # Compute SHA-256 hash of stored file
        file_bytes = storage_provider.read(storage_key)
        sha256_hash = hashlib.sha256(file_bytes).hexdigest()

        ctx.metadata["checksum_sha256"] = sha256_hash
        return ctx


class UploadEvidenceBusinessStage(PipelineStage):
    priority = 500
    name = "UploadBusinessStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        # Persist models in atomic transaction
        evidence = Evidence.objects.create(
            organization_id=ctx.tenant.id,
            tenant_id=ctx.tenant.id,
            workspace_id=ctx.payload.get("workspace_id"),
            title=ctx.payload.get("title", "Untitled Evidence"),
            description=ctx.payload.get("description", ""),
            classification=ctx.payload.get("classification", "restricted"),
            current_custodian=ctx.performed_by,
            owner=ctx.performed_by,
        )

        evidence_file = EvidenceFile.objects.create(
            evidence=evidence,
            file=ctx.metadata["storage_key"],
            checksum_sha256=ctx.metadata["checksum_sha256"],
            original_filename=ctx.metadata["original_filename"],
            stored_filename=ctx.metadata["storage_key"],
            mime_type=ctx.metadata["mime_type"],
            file_size=ctx.metadata["file_size"],
            owner=ctx.performed_by,
            tenant_id=ctx.tenant.id,
        )

        EvidenceVersion.objects.create(
            evidence=evidence,
            file=evidence_file,
            version_number=1,
            notes="Initial upload",
            owner=ctx.performed_by,
            tenant_id=ctx.tenant.id,
        )

        EvidenceCustodyEvent.objects.create(
            evidence=evidence,
            holder=ctx.performed_by,
            event_type="taken",
            taken_at=timezone.now(),
            notes="Initial acquisition upon upload.",
            owner=ctx.performed_by,
            tenant_id=ctx.tenant.id,
        )

        # Set output in payload
        return ctx.with_updates(payload=evidence)


class UploadEvidenceAuditStage(PipelineStage):
    priority = 600
    name = "UploadAuditStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        from typing import cast
        from backend.apps.evidence.models import Evidence
        evidence = cast(Evidence, ctx.payload)
        AuditLog.objects.create(
            action="evidence_uploaded",
            performed_by=ctx.performed_by,
            organization=ctx.tenant,
            outcome="success",
            details={
                "evidence_id": str(evidence.id),
                "title": evidence.title,
                "sha256": ctx.metadata.get("checksum_sha256"),
            },
        )
        return ctx


class UploadEvidenceTimelineStage(PipelineStage):
    priority = 700
    name = "UploadTimelineStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        from typing import cast
        from backend.apps.evidence.models import Evidence
        evidence = cast(Evidence, ctx.payload)
        investigation_id = ctx.metadata.get("investigation_id")
        if investigation_id:
            try:
                # Decoupled dynamic import to avoid circular dependency
                from backend.apps.investigations.models import (
                    Investigation,
                    InvestigationTimelineEvent,
                    TimelineEventType,
                )
                investigation = Investigation.objects.get(id=investigation_id)
                InvestigationTimelineEvent.objects.create(
                    investigation=investigation,
                    event_type=TimelineEventType.EVIDENCE_LINKED,
                    description=f"Evidence '{evidence.title}' uploaded and linked to investigation by {ctx.performed_by.email}.",
                )
            except (ImportError, Exception) as e:
                logger.warning("Could not link evidence timeline event: %s", e)
        return ctx


# ===========================================================================
# 2. TRANSFER CUSTODY STAGES
# ===========================================================================

class TransferCustodyValidationStage(PipelineStage):
    priority = 100
    name = "TransferValidationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        evidence = ctx.payload.get("evidence")
        new_custodian = ctx.payload.get("new_custodian")

        if not evidence:
            raise ValidationError("Evidence is required for transfer.")
        if not new_custodian:
            raise ValidationError("New custodian is required for transfer.")

        # Custodian lock check: Only the active custodian can transfer
        if evidence.current_custodian != ctx.performed_by:
            raise PermissionDenied("Only the active custodian can transfer this evidence.")

        # Check if new custodian belongs to same tenant
        from backend.apps.organizations.models import OrganizationMember
        is_member = OrganizationMember.objects.filter(
            organization=ctx.tenant,
            user=new_custodian,
            status="active"
        ).exists()
        if not is_member:
            raise ValidationError("New custodian does not belong to the same tenant organization.")

        return ctx


class TransferCustodyAuthorizationStage(PipelineStage):
    priority = 200
    name = "TransferAuthorizationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        # Base check already validates active custodian lock.
        return ctx


class TransferCustodyBusinessStage(PipelineStage):
    priority = 300
    name = "TransferBusinessStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        from typing import cast
        from backend.apps.accounts.models import User
        from backend.apps.evidence.models import Evidence

        evidence = ctx.payload.get("evidence")
        new_custodian = ctx.payload.get("new_custodian")
        if evidence is None:
            raise ValidationError("Evidence is required in payload.")
        if new_custodian is None:
            raise ValidationError("New custodian is required in payload.")

        evidence = cast(Evidence, evidence)
        new_custodian = cast(User, new_custodian)
        notes = ctx.payload.get("notes", "")

        now = timezone.now()

        # Update last event
        last_event = EvidenceCustodyEvent.objects.filter(
            evidence=evidence,
            holder=ctx.performed_by,
            event_type="taken",
            released_at__isnull=True
        ).first()

        if last_event:
            last_event.released_at = now
            last_event.save()

        # Create release event
        EvidenceCustodyEvent.objects.create(
            evidence=evidence,
            holder=ctx.performed_by,
            event_type="released",
            taken_at=last_event.taken_at if last_event else now,
            released_at=now,
            notes=f"Released to {new_custodian.email}. {notes}",
            owner=ctx.performed_by,
            tenant_id=ctx.tenant.id,
        )

        # Create acquisition event for new custodian
        EvidenceCustodyEvent.objects.create(
            evidence=evidence,
            holder=new_custodian,
            event_type="taken",
            taken_at=now,
            notes=f"Transferred from {ctx.performed_by.email}. {notes}",
            owner=ctx.performed_by,
            tenant_id=ctx.tenant.id,
        )

        # Update evidence model custodian
        evidence.current_custodian = new_custodian
        evidence.save()

        return ctx.with_updates(payload=evidence)


class TransferCustodyAuditStage(PipelineStage):
    priority = 400
    name = "TransferAuditStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        from typing import cast
        from backend.apps.evidence.models import Evidence
        evidence = cast(Evidence, ctx.payload)
        new_custodian = ctx.metadata.get("new_custodian")
        AuditLog.objects.create(
            action="evidence_custody_transferred",
            performed_by=ctx.performed_by,
            organization=ctx.tenant,
            outcome="success",
            details={
                "evidence_id": str(evidence.id),
                "from_user": ctx.performed_by.email,
                "to_user": new_custodian.email if new_custodian else "unknown",
            },
        )
        return ctx


class TransferCustodyTimelineStage(PipelineStage):
    priority = 500
    name = "TransferTimelineStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        from typing import cast
        from backend.apps.evidence.models import Evidence
        evidence = cast(Evidence, ctx.payload)
        new_custodian = ctx.metadata.get("new_custodian")
        # Add to timeline of all linked investigations
        try:
            from backend.apps.investigations.models import (
                InvestigationTimelineEvent,
                TimelineEventType,
            )
            references = evidence.references.filter(investigation__is_deleted=False)
            for ref in references:
                InvestigationTimelineEvent.objects.create(
                    investigation=ref.investigation,
                    event_type=TimelineEventType.OTHER,
                    description=f"Evidence '{evidence.title}' custody transferred from {ctx.performed_by.email} to {new_custodian.email if new_custodian else 'unknown'}.",
                )
        except (ImportError, Exception) as e:
            logger.warning("Could not create custody transfer timeline event: %s", e)
        return ctx


# ===========================================================================
# 3. VERIFY INTEGRITY STAGES
# ===========================================================================

class VerifyIntegrityValidationStage(PipelineStage):
    priority = 100
    name = "VerifyValidationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        evidence = ctx.payload.get("evidence")
        if not evidence:
            raise ValidationError("Evidence is required for integrity verification.")

        # Ensure there is a file registered
        if not hasattr(evidence, "file_meta") or not evidence.file_meta:
            raise ValidationError("No file metadata found for the evidence.")

        return ctx


class VerifyIntegrityStorageStage(PipelineStage):
    priority = 200
    name = "VerifyStorageStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        from typing import cast
        from backend.apps.evidence.models import Evidence
        evidence = ctx.payload.get("evidence")
        if evidence is None:
            raise ValidationError("Evidence is required in payload.")
        evidence = cast(Evidence, evidence)
        storage_key = evidence.file_meta.file.name
        if not storage_key:
            raise ValidationError("Storage key is missing on evidence file.")
        # Read the file
        file_bytes = storage_provider.read(storage_key)
        ctx.metadata["file_bytes"] = file_bytes
        return ctx


class VerifyIntegrityHashStage(PipelineStage):
    priority = 300
    name = "VerifyHashStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        file_bytes = ctx.metadata.get("file_bytes")
        if file_bytes is None:
            raise ValidationError("File bytes are required in metadata.")
        # Compute SHA-256
        sha256_hash = hashlib.sha256(file_bytes).hexdigest()
        ctx.metadata["computed_sha256"] = sha256_hash
        return ctx


class VerifyIntegrityBusinessStage(PipelineStage):
    priority = 400
    name = "VerifyBusinessStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        from typing import cast
        from backend.apps.evidence.models import Evidence
        evidence = ctx.payload.get("evidence")
        if evidence is None:
            raise ValidationError("Evidence is required in payload.")
        evidence = cast(Evidence, evidence)
        computed_hash = ctx.metadata.get("computed_sha256")
        expected_hash = evidence.file_meta.checksum_sha256

        is_verified = (computed_hash == expected_hash)
        evidence.status = "verified" if is_verified else "rejected"
        evidence.save()

        # Log custody verification event
        EvidenceCustodyEvent.objects.create(
            evidence=evidence,
            holder=ctx.performed_by,
            event_type="taken",
            taken_at=timezone.now(),
            notes=f"Integrity check. Expected: {expected_hash}, Computed: {computed_hash}. Match: {is_verified}",
            owner=ctx.performed_by,
            tenant_id=ctx.tenant.id,
        )

        ctx.metadata["integrity_passed"] = is_verified
        return ctx.with_updates(payload=evidence)


class VerifyIntegrityAuditStage(PipelineStage):
    priority = 500
    name = "VerifyAuditStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        from typing import cast
        from backend.apps.evidence.models import Evidence
        evidence = cast(Evidence, ctx.payload)
        passed = ctx.metadata.get("integrity_passed", False)
        AuditLog.objects.create(
            action="evidence_verified",
            performed_by=ctx.performed_by,
            organization=ctx.tenant,
            outcome="success" if passed else "failure",
            details={
                "evidence_id": str(evidence.id),
                "expected_hash": evidence.file_meta.checksum_sha256,
                "computed_hash": ctx.metadata.get("computed_sha256"),
                "passed": passed,
            },
        )
        return ctx


class VerifyIntegrityTimelineStage(PipelineStage):
    priority = 600
    name = "VerifyTimelineStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        from typing import cast
        from backend.apps.evidence.models import Evidence
        evidence = cast(Evidence, ctx.payload)
        passed = ctx.metadata.get("integrity_passed", False)
        try:
            from backend.apps.investigations.models import (
                InvestigationTimelineEvent,
                TimelineEventType,
            )
            references = evidence.references.filter(investigation__is_deleted=False)
            for ref in references:
                status_desc = "passed verification" if passed else "FAILED verification"
                InvestigationTimelineEvent.objects.create(
                    investigation=ref.investigation,
                    event_type=TimelineEventType.OTHER,
                    description=f"Evidence '{evidence.title}' integrity check: {status_desc}.",
                )
        except (ImportError, Exception) as e:
            logger.warning("Could not create integrity check timeline event: %s", e)
        return ctx
