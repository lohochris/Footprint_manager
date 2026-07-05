from backend.apps.common.pipeline.registry import PipelineRegistry
from backend.apps.ai_assistant.pipelines.stages import (
    AIPromptAssemblyStage,
    AIProviderExecutionStage,
    AIValidationStage,
    AIPersistenceStage,
)

def register_ai_pipelines() -> None:
    """Register AI-related pipeline actions."""
    # Pipeline stages will be implemented in Phase 6
    PipelineRegistry.register(
        "ai.summarize_investigation",
        lambda **_payload: None
    )

    PipelineRegistry.register(
        "ai.explain_graph",
        lambda **_payload: None
    )
