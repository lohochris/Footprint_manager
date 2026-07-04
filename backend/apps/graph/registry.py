from backend.apps.common.pipeline.factory import PipelineFactory
from backend.apps.graph.services.pipeline_stages import (
    GraphBuildValidationStage,
    GraphBuildBusinessStage,
    GraphBuildAuditStage,
    GraphSyncValidationStage,
    GraphSyncBusinessStage,
    GraphSyncAuditStage,
    GraphRefreshValidationStage,
    GraphRefreshBusinessStage,
    GraphRefreshAuditStage,
)

# Register operations with PipelineFactory
PipelineFactory.register_stages("graph.build", [
    GraphBuildValidationStage,
    GraphBuildBusinessStage,
    GraphBuildAuditStage,
])

PipelineFactory.register_stages("graph.sync", [
    GraphSyncValidationStage,
    GraphSyncBusinessStage,
    GraphSyncAuditStage,
])

PipelineFactory.register_stages("graph.refresh", [
    GraphRefreshValidationStage,
    GraphRefreshBusinessStage,
    GraphRefreshAuditStage,
])

PipelineFactory.register_stages("graph.rebuild", [
    GraphRefreshValidationStage,
    GraphRefreshBusinessStage,
    GraphRefreshAuditStage,
])
