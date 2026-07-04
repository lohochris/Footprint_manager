from backend.apps.common.pipeline.factory import PipelineFactory
from backend.apps.common.pipeline.registry import PipelineRegistry

from .services.pipeline_stages import (
    IdentityResolveValidationStage,
    IdentityResolveAuthorizationStage,
    IdentityResolveCandidateDiscoveryStage,
    IdentityResolveSimilarityScoringStage,
    IdentityResolveConfidenceCalculationStage,
    IdentityResolveMergeDecisionStage,
    IdentityResolveEvidenceCorrelationStage,
    IdentityResolveTimelineStage,
    IdentityResolveAuditStage,
    IdentityMergeValidationStage,
    IdentityMergeBusinessStage,
    IdentityMergeAuditStage,
    IdentitySplitValidationStage,
    IdentitySplitBusinessStage,
    IdentitySplitAuditStage,
)

# 1. Register Operations with PipelineFactory
PipelineFactory.register_stages("identity.resolve", [
    IdentityResolveValidationStage,
    IdentityResolveAuthorizationStage,
    IdentityResolveCandidateDiscoveryStage,
    IdentityResolveSimilarityScoringStage,
    IdentityResolveConfidenceCalculationStage,
    IdentityResolveMergeDecisionStage,
    IdentityResolveEvidenceCorrelationStage,
    IdentityResolveTimelineStage,
    IdentityResolveAuditStage,
])

PipelineFactory.register_stages("identity.merge", [
    IdentityMergeValidationStage,
    IdentityMergeBusinessStage,
    IdentityMergeAuditStage,
])

PipelineFactory.register_stages("identity.split", [
    IdentitySplitValidationStage,
    IdentitySplitBusinessStage,
    IdentitySplitAuditStage,
])

# 2. Register compatibility with PipelineRegistry
PipelineRegistry.register("identity.resolve", lambda **_payload: None)
PipelineRegistry.register("identity.merge", lambda **_payload: None)
PipelineRegistry.register("identity.split", lambda **_payload: None)
