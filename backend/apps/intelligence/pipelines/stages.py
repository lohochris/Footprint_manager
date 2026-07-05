import uuid
from typing import Any
from backend.apps.intelligence.engine.intelligence_engine import IntelligenceEngine
from backend.apps.intelligence.repositories.intelligence_repository import IntelligenceRepository
from backend.apps.common.pipeline.core import PipelineContext, PipelineStage
from backend.apps.intelligence.dto.analytics import AnalyticsResultDTO
from backend.apps.intelligence.dto.risk import RiskAssessmentDTO
from typing import cast


class IntelligenceValidationStage(PipelineStage):
    """Validates the inputs before intelligence calculations begin."""

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        tenant_id = getattr(ctx.tenant, "id", ctx.tenant)
        if not tenant_id:
            return ctx.with_updates(errors=ctx.errors + [ValueError("tenant_id is required for intelligence calculation")])
        return ctx


class FetchGraphStage(PipelineStage):
    """Retrieves the subgraph for analytics."""

    def __init__(self, repository: Any | None = None) -> None:
        if repository is None:
            from backend.apps.graph.repositories import DjangoGraphRepository
            from backend.apps.graph.providers.neo4j import Neo4jProvider
            self.repository = DjangoGraphRepository(provider=Neo4jProvider())
        else:
            self.repository = repository

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        if ctx.errors:
            return ctx

        tenant_id = getattr(ctx.tenant, "id", ctx.tenant)
        nodes, edges = self.repository.get_subgraph(
            tenant_id=tenant_id,
            workspace_id=ctx.payload.get("workspace_id")
        )
        return ctx.with_updates(payload={**ctx.payload, "nodes": nodes, "edges": edges})


class ComputeAnalyticsStage(PipelineStage):
    """Computes analytics facts."""

    def __init__(self, engine: IntelligenceEngine | None = None) -> None:
        self.engine = engine or IntelligenceEngine()

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        if ctx.errors:
            return ctx

        tenant_id = getattr(ctx.tenant, "id", ctx.tenant)
        nodes = ctx.payload.get("nodes", [])
        edges = ctx.payload.get("edges", [])

        analytics = self.engine.analytics_service.analyze_graph(
            tenant_id=tenant_id,
            workspace_id=ctx.payload.get("workspace_id"),
            nodes=nodes,
            edges=edges,
        )
        return ctx.with_updates(payload={**ctx.payload, "analytics": analytics})


class ScoreRiskStage(PipelineStage):
    """Scores risk for entities based on analytics facts."""

    def __init__(self, engine: IntelligenceEngine | None = None) -> None:
        self.engine = engine or IntelligenceEngine()

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        if ctx.errors:
            return ctx

        tenant_id = getattr(ctx.tenant, "id", ctx.tenant)
        nodes = ctx.payload.get("nodes", [])
        analytics = cast(AnalyticsResultDTO, ctx.payload.get("analytics"))
        context_data = {"watchlists": ctx.payload.get("watchlists", [])}

        risk = self.engine.risk_service.assess_risk(
            tenant_id=tenant_id,
            workspace_id=ctx.payload.get("workspace_id"),
            nodes=nodes,
            analytics=analytics,
            context=context_data,
        )
        return ctx.with_updates(payload={**ctx.payload, "risk": risk})


class RecommendationStage(PipelineStage):
    """Generates recommendations based on risk and analytics."""

    def __init__(self, engine: IntelligenceEngine | None = None) -> None:
        self.engine = engine or IntelligenceEngine()

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        if ctx.errors:
            return ctx

        tenant_id = getattr(ctx.tenant, "id", ctx.tenant)
        nodes = ctx.payload.get("nodes", [])
        edges = ctx.payload.get("edges", [])
        analytics = cast(AnalyticsResultDTO, ctx.payload.get("analytics"))
        risk = cast(RiskAssessmentDTO, ctx.payload.get("risk"))
        context_data = {"watchlists": ctx.payload.get("watchlists", [])}

        recommendations = self.engine.recommendation_service.generate_recommendations(
            tenant_id=tenant_id,
            workspace_id=ctx.payload.get("workspace_id"),
            nodes=nodes,
            edges=edges,
            analytics=analytics,
            risk=risk,
            context=context_data,
        )
        return ctx.with_updates(payload={**ctx.payload, "recommendations": recommendations})


class PersistenceStage(PipelineStage):
    """Saves the intelligence results back to the database."""

    def __init__(self, repository: IntelligenceRepository | None = None) -> None:
        # Avoid direct import if repository isn't written yet
        self.repository = repository

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        if ctx.errors:
            return ctx

        if not self.repository:
            # lazy load to avoid circular imports during setup
            from backend.apps.intelligence.repositories.intelligence_repository import IntelligenceRepository
            self.repository = IntelligenceRepository()

        # Optional analytics persistence if needed later
        # analytics = ctx.payload.get("analytics")
        risk = ctx.payload.get("risk")
        recommendations = ctx.payload.get("recommendations")

        owner_id = ctx.performed_by

        if risk:
            self.repository.save_risk_assessment(risk, owner_id)
        if recommendations:
            self.repository.save_recommendations(recommendations, owner_id)

        return ctx
