from backend.apps.common.pipeline.factory import PipelineFactory
from backend.apps.common.pipeline.registry import PipelineRegistry

from .services.pipeline_stages import (
    ArchiveAuditStage,
    ArchiveAuthorizationStage,
    ArchiveBusinessStage,
    ArchiveValidationStage,
    AssignMembersAuditStage,
    AssignMembersAuthorizationStage,
    AssignMembersBusinessStage,
    AssignMembersTimelineStage,
    AssignMembersValidationStage,
    ChangeStatusAuditStage,
    ChangeStatusAuthorizationStage,
    ChangeStatusBusinessStage,
    ChangeStatusTimelineStage,
    ChangeStatusValidationStage,
    CreateInvestigationAuditStage,
    CreateInvestigationAuthorizationStage,
    CreateInvestigationBusinessStage,
    CreateInvestigationTimelineStage,
    CreateInvestigationValidationStage,
    RestoreAuditStage,
    RestoreAuthorizationStage,
    RestoreBusinessStage,
    RestoreValidationStage,
    SoftDeleteAuditStage,
    SoftDeleteAuthorizationStage,
    SoftDeleteBusinessStage,
    SoftDeleteValidationStage,
    TransferOwnershipAuditStage,
    TransferOwnershipAuthorizationStage,
    TransferOwnershipBusinessStage,
    TransferOwnershipValidationStage,
    UpdateInvestigationAuditStage,
    UpdateInvestigationAuthorizationStage,
    UpdateInvestigationBusinessStage,
    UpdateInvestigationValidationStage,
)

# 1. Register with PipelineFactory (provides execution flow with explicit stages)
PipelineFactory.register_stages("investigation.create", [
    CreateInvestigationValidationStage,
    CreateInvestigationAuthorizationStage,
    CreateInvestigationBusinessStage,
    CreateInvestigationAuditStage,
    CreateInvestigationTimelineStage,
])

PipelineFactory.register_stages("investigation.update", [
    UpdateInvestigationValidationStage,
    UpdateInvestigationAuthorizationStage,
    UpdateInvestigationBusinessStage,
    UpdateInvestigationAuditStage,
])

PipelineFactory.register_stages("investigation.assign_members", [
    AssignMembersValidationStage,
    AssignMembersAuthorizationStage,
    AssignMembersBusinessStage,
    AssignMembersAuditStage,
    AssignMembersTimelineStage,
])

PipelineFactory.register_stages("investigation.change_status", [
    ChangeStatusValidationStage,
    ChangeStatusAuthorizationStage,
    ChangeStatusBusinessStage,
    ChangeStatusAuditStage,
    ChangeStatusTimelineStage,
])

PipelineFactory.register_stages("investigation.archive", [
    ArchiveValidationStage,
    ArchiveAuthorizationStage,
    ArchiveBusinessStage,
    ArchiveAuditStage,
])

PipelineFactory.register_stages("investigation.restore", [
    RestoreValidationStage,
    RestoreAuthorizationStage,
    RestoreBusinessStage,
    RestoreAuditStage,
])

PipelineFactory.register_stages("investigation.soft_delete", [
    SoftDeleteValidationStage,
    SoftDeleteAuthorizationStage,
    SoftDeleteBusinessStage,
    SoftDeleteAuditStage,
])

PipelineFactory.register_stages("investigation.transfer_ownership", [
    TransferOwnershipValidationStage,
    TransferOwnershipAuthorizationStage,
    TransferOwnershipBusinessStage,
    TransferOwnershipAuditStage,
])

# 2. Compatibility registrations with PipelineRegistry (stub mappings)
PipelineRegistry.register("investigation.create", lambda **_payload: None)
PipelineRegistry.register("investigation.update", lambda **_payload: None)
PipelineRegistry.register("investigation.assign_members", lambda **_payload: None)
PipelineRegistry.register("investigation.change_status", lambda **_payload: None)
PipelineRegistry.register("investigation.archive", lambda **_payload: None)
PipelineRegistry.register("investigation.restore", lambda **_payload: None)
PipelineRegistry.register("investigation.soft_delete", lambda **_payload: None)
PipelineRegistry.register("investigation.transfer_ownership", lambda **_payload: None)
