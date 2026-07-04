from backend.apps.common.pipeline.factory import PipelineFactory
from backend.apps.common.pipeline.registry import PipelineRegistry

from .services.pipeline_stages import (
    UploadEvidenceValidationStage,
    UploadEvidenceAuthorizationStage,
    UploadEvidenceStorageStage,
    UploadEvidenceHashStage,
    UploadEvidenceBusinessStage,
    UploadEvidenceAuditStage,
    UploadEvidenceTimelineStage,
    TransferCustodyValidationStage,
    TransferCustodyAuthorizationStage,
    TransferCustodyBusinessStage,
    TransferCustodyAuditStage,
    TransferCustodyTimelineStage,
    VerifyIntegrityValidationStage,
    VerifyIntegrityStorageStage,
    VerifyIntegrityHashStage,
    VerifyIntegrityBusinessStage,
    VerifyIntegrityAuditStage,
    VerifyIntegrityTimelineStage,
)

# 1. Register Upload Evidence Operation
PipelineFactory.register_stages("evidence.upload", [
    UploadEvidenceValidationStage,
    UploadEvidenceAuthorizationStage,
    UploadEvidenceStorageStage,
    UploadEvidenceHashStage,
    UploadEvidenceBusinessStage,
    UploadEvidenceAuditStage,
    UploadEvidenceTimelineStage,
])

# 2. Register Transfer Custody Operation
PipelineFactory.register_stages("evidence.transfer_custody", [
    TransferCustodyValidationStage,
    TransferCustodyAuthorizationStage,
    TransferCustodyBusinessStage,
    TransferCustodyAuditStage,
    TransferCustodyTimelineStage,
])

# 3. Register Verify Integrity Operation
PipelineFactory.register_stages("evidence.verify_integrity", [
    VerifyIntegrityValidationStage,
    VerifyIntegrityStorageStage,
    VerifyIntegrityHashStage,
    VerifyIntegrityBusinessStage,
    VerifyIntegrityAuditStage,
    VerifyIntegrityTimelineStage,
])

# 4. Register compatibility with PipelineRegistry
PipelineRegistry.register("evidence.upload", lambda **_payload: None)
PipelineRegistry.register("evidence.transfer_custody", lambda **_payload: None)
PipelineRegistry.register("evidence.verify_integrity", lambda **_payload: None)
