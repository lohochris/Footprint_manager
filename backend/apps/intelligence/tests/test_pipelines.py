import pytest
from unittest.mock import MagicMock
from backend.apps.common.pipeline.core import PipelineContext
from backend.apps.intelligence.pipelines.stages import FetchGraphStage, ComputeAnalyticsStage

def test_fetch_graph_stage():
    stage = FetchGraphStage(repository=MagicMock())
    ctx = PipelineContext(performed_by="user1", tenant="t1", payload={"workspace_id": "w1"})

    stage.repository.get_subgraph.return_value = (["node1"], ["edge1"])

    ctx = stage.execute(ctx)

    assert ctx.payload.get("nodes") == ["node1"]
    assert ctx.payload.get("edges") == ["edge1"]

def test_compute_analytics_stage():
    stage = ComputeAnalyticsStage(engine=MagicMock())
    ctx = PipelineContext(performed_by="user1", tenant="t1", payload={"workspace_id": "w1", "nodes": ["node1"], "edges": ["edge1"]})

    stage.engine.analytics_service.analyze_graph.return_value = "analytics_result"

    ctx = stage.execute(ctx)

    assert ctx.payload.get("analytics") == "analytics_result"
