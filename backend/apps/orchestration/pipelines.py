from backend.apps.common.pipeline.registry import PipelineRegistry
from backend.apps.orchestration.services import WorkflowService
from backend.apps.orchestration.dto import PlaybookExecutionParams

def register_orchestration_pipelines():
    """
    Registers orchestration workflow triggers to the PipelineRegistry.
    This ensures bounded contexts can trigger workflows purely via events/pipelines.
    """
    PipelineRegistry.register(
        "workflow.start",
        lambda **payload: WorkflowService.start_execution(PlaybookExecutionParams(**payload))
    )

    # Placeholders for additional lifecycle events
    PipelineRegistry.register("workflow.resume", lambda **payload: None)
    PipelineRegistry.register("workflow.retry", lambda **payload: None)
    PipelineRegistry.register("workflow.cancel", lambda **payload: None)
    PipelineRegistry.register("workflow.approve", lambda **payload: None)
