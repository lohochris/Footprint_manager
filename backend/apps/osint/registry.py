# backend/apps/osint/registry.py
"""Pipeline registry for the OSINT Discovery domain.

Registers all discovery operation pipelines with ``PipelineFactory``
(stage-based execution) and ``PipelineRegistry`` (compatibility stubs),
mirroring the pattern established in ``investigations/registry.py`` and
``evidence/registry.py``.

This module is imported once inside ``OsintConfig.ready()``.
"""

from backend.apps.common.pipeline.factory import PipelineFactory
from backend.apps.common.pipeline.registry import PipelineRegistry

from .services.pipeline_stages import (
    CreateJobAuditStage,
    CreateJobAuthorizationStage,
    CreateJobBusinessStage,
    CreateJobValidationStage,
    RunJobAuditStage,
    RunJobBusinessStage,
    RunJobFeatureFlagStage,
    RunJobValidationStage,
)

# ---------------------------------------------------------------------------
# 1. PipelineFactory registrations (provide execution flow with explicit stages)
# ---------------------------------------------------------------------------

PipelineFactory.register_stages("osint.job.create", [
    CreateJobValidationStage,
    CreateJobAuthorizationStage,
    CreateJobBusinessStage,
    CreateJobAuditStage,
])

PipelineFactory.register_stages("osint.job.run", [
    RunJobValidationStage,
    RunJobFeatureFlagStage,
    RunJobBusinessStage,
    RunJobAuditStage,
])

# ---------------------------------------------------------------------------
# 2. PipelineRegistry compatibility stubs
# ---------------------------------------------------------------------------

PipelineRegistry.register("osint.job.create", lambda **_payload: None)
PipelineRegistry.register("osint.job.run", lambda **_payload: None)
