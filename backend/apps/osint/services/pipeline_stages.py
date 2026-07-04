# backend/apps/osint/services/pipeline_stages.py
"""Pipeline stages for OSINT Discovery domain operations.

Follows the exact Validation → Authorization → Business → Audit stage
pattern established in ``investigations/services/pipeline_stages.py``
and ``evidence/services/pipeline_stages.py``.

Two operation pipelines are defined:

``osint.job.create``
    Validates the DiscoveryRequest DTO, checks authorization, creates the
    DiscoveryJob via DiscoveryJobService, and writes an audit log entry.

``osint.job.run``
    Validates the job is runnable, checks the ENABLE_DISCOVERY feature flag,
    executes the job via DiscoveryJobService, and writes an audit log entry.
"""

from __future__ import annotations

import logging

from django.core.exceptions import PermissionDenied, ValidationError

from backend.apps.audit.models.audit_log import AuditLog
from backend.apps.common.pipeline.core import PipelineContext, PipelineStage
from backend.apps.osint.enums import DiscoveryJobStatus
from backend.apps.osint.models import DiscoveryJob
from backend.apps.osint.services.discovery_job_service import DiscoveryJobService
from backend.shared.constants.feature_flags import ENABLE_DISCOVERY, is_feature_enabled

logger = logging.getLogger(__name__)

_service = DiscoveryJobService()


# ===========================================================================
# osint.job.create — Create a DiscoveryJob
# ===========================================================================

class CreateJobValidationStage(PipelineStage):
    """Validate the DiscoveryRequest DTO before job creation."""

    priority = 100
    name = "CreateJobValidationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        request_dto = ctx.payload.get("request")
        if request_dto is None:
            raise ValidationError(
                "A DiscoveryRequest DTO is required in ctx.payload['request']."
            )
        if not request_dto.provider_name:
            raise ValidationError("DiscoveryRequest.provider_name must not be empty.")
        if not request_dto.triggered_by:
            raise ValidationError("DiscoveryRequest.triggered_by must not be empty.")
        return ctx


class CreateJobAuthorizationStage(PipelineStage):
    """Verify the caller is authenticated within a valid tenant context."""

    priority = 200
    name = "CreateJobAuthorizationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        if not ctx.performed_by:
            raise PermissionDenied("Authentication is required to create a discovery job.")
        if not ctx.tenant:
            raise PermissionDenied(
                "A valid tenant organization context is required."
            )
        return ctx


class CreateJobBusinessStage(PipelineStage):
    """Create the DiscoveryJob via DiscoveryJobService."""

    priority = 300
    name = "CreateJobBusinessStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        request_dto = ctx.payload.get("request")
        if request_dto is None:
            raise ValueError("DiscoveryRequest is required in payload.")
        job = _service.create_job(
            request=request_dto,
            user=ctx.performed_by,
        )
        return ctx.with_updates(payload={"job": job})


class CreateJobAuditStage(PipelineStage):
    """Write an audit log entry for the created job."""

    priority = 400
    name = "CreateJobAuditStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        job: DiscoveryJob | None = ctx.payload.get("job")
        if job:
            AuditLog.objects.create(
                action="discovery_job_created",
                performed_by=ctx.performed_by,
                organization=ctx.tenant,
                outcome="success",
                details={
                    "job_id": str(job.id),
                    "provider": job.provider.name,
                    "triggered_by": job.triggered_by,
                },
            )
        return ctx


# ===========================================================================
# osint.job.run — Execute a DiscoveryJob
# ===========================================================================

class RunJobValidationStage(PipelineStage):
    """Validate the job is in a runnable state."""

    priority = 100
    name = "RunJobValidationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        job: DiscoveryJob | None = ctx.payload.get("job")
        if job is None:
            raise ValidationError(
                "A DiscoveryJob instance is required in ctx.payload['job']."
            )
        if job.is_terminal:
            raise ValidationError(
                f"Job {job.id} is in terminal state '{job.status}' and cannot be run."
            )
        return ctx


class RunJobFeatureFlagStage(PipelineStage):
    """Gate execution on the ENABLE_DISCOVERY feature flag."""

    priority = 150
    name = "RunJobFeatureFlagStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        if not is_feature_enabled(ENABLE_DISCOVERY):
            raise PermissionDenied(
                "The OSINT discovery feature is currently disabled. "
                "Enable FEATURE_ENABLE_DISCOVERY to proceed."
            )
        return ctx


class RunJobBusinessStage(PipelineStage):
    """Execute the discovery job and attach results to the context."""

    priority = 300
    name = "RunJobBusinessStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        job = ctx.payload.get("job")
        if job is None:
            raise ValueError("DiscoveryJob is required in payload.")
        results = _service.run(job)
        return ctx.with_updates(payload={"job": job, "results": results})


class RunJobAuditStage(PipelineStage):
    """Write an audit log entry for the completed / failed execution."""

    priority = 400
    name = "RunJobAuditStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        job: DiscoveryJob | None = ctx.payload.get("job")
        results = ctx.payload.get("results", [])
        if job:
            AuditLog.objects.create(
                action="discovery_job_executed",
                performed_by=ctx.performed_by,
                organization=ctx.tenant,
                outcome="success" if job.status == DiscoveryJobStatus.COMPLETED else "failure",
                details={
                    "job_id": str(job.id),
                    "status": job.status,
                    "result_count": len(results),
                    "duration_ms": job.duration_ms,
                    "failure_reason": job.failure_reason or None,
                },
            )
        return ctx
