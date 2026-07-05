import uuid
from typing import Any

from backend.apps.graph.repositories import GraphRepository
from backend.apps.intelligence.engine.intelligence_engine import IntelligenceEngine
from backend.apps.intelligence.repositories.intelligence_repository import IntelligenceRepository
from backend.apps.common.pipeline.core import PipelineContext, PipelineStage


class IntelligenceValidationStage(PipelineStage):
    """Validates the inputs before intelligence calculations begin."""

    def execute(self, ctx: PipelineContext) -> None:
        tenant_id = ctx.tenant_id
        if not tenant_id:
            ctx.add_error("tenant_id is required for intelligence calculation")
            return


class FetchGraphStage(PipelineStage):
    """Retrieves the subgraph for analytics."""

    def __init__(self, repository: GraphRepository | None = None) -> None:
        self.repository = repository or GraphRepository()

    def execute(self, ctx: PipelineContext) -> None:
        if ctx.has_errors():
            return
            
        nodes, edges = self.repository.get_subgraph(
            tenant_id=ctx.tenant_id,
            workspace_id=ctx.get("workspace_id")
        )
        ctx.set("nodes", nodes)
        ctx.set("edges", edges)


class ComputeAnalyticsStage(PipelineStage):
    """Computes analytics facts."""

    def __init__(self, engine: IntelligenceEngine | None = None) -> None:
        self.engine = engine or IntelligenceEngine()

    def execute(self, ctx: PipelineContext) -> None:
        if ctx.has_errors():
            return

        nodes = ctx.get("nodes", [])
        edges = ctx.get("edges", [])

        analytics = self.engine.analytics_service.analyze_graph(
            tenant_id=ctx.tenant_id,
            workspace_id=ctx.get("workspace_id"),
            nodes=nodes,
            edges=edges,
        )
        ctx.set("analytics", analytics)


class ScoreRiskStage(PipelineStage):
    """Scores risk for entities based on analytics facts."""

    def __init__(self, engine: IntelligenceEngine | None = None) -> None:
        self.engine = engine or IntelligenceEngine()

    def execute(self, ctx: PipelineContext) -> None:
        if ctx.has_errors():
            return

        nodes = ctx.get("nodes", [])
        analytics = ctx.get("analytics")
        context_data = {"watchlists": ctx.get("watchlists", [])}

        risk = self.engine.risk_service.assess_risk(
            tenant_id=ctx.tenant_id,
            workspace_id=ctx.get("workspace_id"),
            nodes=nodes,
            analytics=analytics,
            context=context_data,
        )
        ctx.set("risk", risk)


class RecommendationStage(PipelineStage):
    """Generates recommendations based on risk and analytics."""

    def __init__(self, engine: IntelligenceEngine | None = None) -> None:
        self.engine = engine or IntelligenceEngine()

    def execute(self, ctx: PipelineContext) -> None:
        if ctx.has_errors():
            return

        nodes = ctx.get("nodes", [])
        edges = ctx.get("edges", [])
        analytics = ctx.get("analytics")
        risk = ctx.get("risk")
        context_data = {"watchlists": ctx.get("watchlists", [])}

        recommendations = self.engine.recommendation_service.generate_recommendations(
            tenant_id=ctx.tenant_id,
            workspace_id=ctx.get("workspace_id"),
            nodes=nodes,
            edges=edges,
            analytics=analytics,
            risk=risk,
            context=context_data,
        )
        ctx.set("recommendations", recommendations)


class PersistenceStage(PipelineStage):
    """Saves the intelligence results back to the database."""

    def __init__(self, repository: IntelligenceRepository | None = None) -> None:
        # Avoid direct import if repository isn't written yet
        self.repository = repository

    def execute(self, ctx: PipelineContext) -> None:
        if ctx.has_errors():
            return

        if not self.repository:
            # lazy load to avoid circular imports during setup
            from backend.apps.intelligence.repositories.intelligence_repository import IntelligenceRepository
            self.repository = IntelligenceRepository()

        analytics = ctx.get("analytics")
        risk = ctx.get("risk")
        recommendations = ctx.get("recommendations")

        owner_id = ctx.performed_by

        if risk:
            self.repository.save_risk_assessment(risk, owner_id)
        if recommendations:
            self.repository.save_recommendations(recommendations, owner_id)
