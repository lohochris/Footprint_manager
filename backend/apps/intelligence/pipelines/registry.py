from backend.apps.common.pipeline.factory import PipelineFactory
from backend.apps.intelligence.pipelines.stages import (
    IntelligenceValidationStage,
    FetchGraphStage,
    ComputeAnalyticsStage,
    ScoreRiskStage,
    RecommendationStage,
    PersistenceStage,
)

# Register operations with PipelineFactory
PipelineFactory.register_stages("intelligence.calculate", [
    IntelligenceValidationStage,
    FetchGraphStage,
    ComputeAnalyticsStage,
    ScoreRiskStage,
    RecommendationStage,
    PersistenceStage,
])

PipelineFactory.register_stages("intelligence.refresh", [
    IntelligenceValidationStage,
    # Here we would normally add an eviction stage first
    FetchGraphStage,
    ComputeAnalyticsStage,
    ScoreRiskStage,
    RecommendationStage,
    PersistenceStage,
])
