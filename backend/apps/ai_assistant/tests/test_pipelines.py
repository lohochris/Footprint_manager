import pytest
from backend.apps.ai_assistant.pipelines.registry import register_ai_pipelines
from backend.apps.common.pipeline.registry import PipelineRegistry

def test_pipeline_registration():
    # Clear registry first to test isolation if needed, or just register
    register_ai_pipelines()
    
    # Verify stages are registered
    assert "ai.summarize_investigation" in PipelineRegistry._registry
    assert "ai.explain_graph" in PipelineRegistry._registry
    
    # Verify we can execute them without crashing (using our mocked lambda)
    PipelineRegistry.execute("ai.summarize_investigation")
    PipelineRegistry.execute("ai.explain_graph")
