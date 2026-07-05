import logging
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction

from backend.apps.common.pipeline.core import PipelineContext, PipelineStage
from backend.apps.audit.models.audit_log import AuditLog
from backend.apps.graph.dtos import EdgeDTO, NodeDTO
from backend.apps.graph.choices import GraphNodeType, GraphRelationshipType
from backend.apps.graph.providers import DjangoORMGraphProvider
from backend.apps.graph.repositories import DjangoGraphRepository

# Source models for graph read-model generation
from backend.apps.identity.models import Identity, IdentityRelationship
from backend.apps.evidence.models.evidence import Evidence
from backend.apps.investigations.models.investigation import Investigation
from backend.apps.osint.models.discovery_result import DiscoveryResult

logger = logging.getLogger(__name__)


def get_repository() -> DjangoGraphRepository:
    return DjangoGraphRepository(DjangoORMGraphProvider())


# ===========================================================================
# BUILD PIPELINE STAGES
# ===========================================================================

class GraphBuildValidationStage(PipelineStage):
    priority = 100
    name = "GraphBuildValidationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        if not ctx.tenant:
            raise ValidationError("Tenant organization isolation context is required.")
        return ctx


class GraphBuildBusinessStage(PipelineStage):
    priority = 500
    name = "GraphBuildBusinessStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        tenant_id = str(ctx.tenant.id)
        workspace_id = str(ctx.payload.get("workspace_id")) if ctx.payload.get("workspace_id") else None
        owner_id = str(ctx.performed_by.id) if getattr(ctx, "performed_by", None) else None

        nodes: list[NodeDTO] = []
        edges: list[EdgeDTO] = []

        # 1. Fetch and convert Identities
        identities_qs = Identity.objects.filter(tenant_id=tenant_id)
        if workspace_id:
            identities_qs = identities_qs.filter(workspace_id=workspace_id)

        for identity in identities_qs:
            nodes.append(
                NodeDTO(
                    id=str(identity.id),
                    tenant_id=tenant_id,
                    workspace_id=str(identity.workspace_id) if identity.workspace_id else None,
                    owner_id=owner_id,
                    node_type=GraphNodeType.IDENTITY,
                    label=identity.label,
                    confidence=identity.confidence_score,
                    metadata={"source": identity.source, "entity_type": identity.entity_type},
                )
            )

        # 2. Fetch and convert Identity Relationships
        rel_qs = IdentityRelationship.objects.filter(tenant_id=tenant_id)
        for rel in rel_qs:
            edges.append(
                EdgeDTO(
                    id=str(rel.id),
                    tenant_id=tenant_id,
                    source_id=str(rel.source_identity_id),
                    target_id=str(rel.target_identity_id),
                    owner_id=owner_id,
                    relationship_type=rel.type,
                    confidence=rel.confidence,
                )
            )

        # 3. Fetch and convert Investigations
        investigations_qs = Investigation.objects.filter(organization_id=tenant_id)
        if workspace_id:
            investigations_qs = investigations_qs.filter(workspace_id=workspace_id)

        for inv in investigations_qs:
            nodes.append(
                NodeDTO(
                    id=str(inv.id),
                    tenant_id=tenant_id,
                    workspace_id=str(inv.workspace_id) if inv.workspace_id else None,
                    owner_id=owner_id,
                    node_type=GraphNodeType.INVESTIGATION,
                    label=inv.title,
                    metadata={"status": inv.status},
                )
            )

        # 4. Fetch and convert Evidence items
        evidence_qs = Evidence.objects.filter(organization_id=tenant_id)
        if workspace_id:
            evidence_qs = evidence_qs.filter(workspace_id=workspace_id)

        for ev in evidence_qs:
            nodes.append(
                NodeDTO(
                    id=str(ev.id),
                    tenant_id=tenant_id,
                    workspace_id=str(ev.workspace_id) if ev.workspace_id else None,
                    owner_id=owner_id,
                    node_type=GraphNodeType.EVIDENCE,
                    label=ev.title,
                    metadata={"status": ev.status},
                )
            )

        # 5. Fetch and convert OSINT Discovery Results
        discovery_qs = DiscoveryResult.objects.filter(job__investigation__organization_id=tenant_id)
        if workspace_id:
            discovery_qs = discovery_qs.filter(job__investigation__workspace_id=workspace_id)

        for dr in discovery_qs:
            workspace_id = None
            if dr.job and dr.job.investigation and dr.job.investigation.workspace_id:
                workspace_id = str(dr.job.investigation.workspace_id)

            nodes.append(
                NodeDTO(
                    id=str(dr.id),
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    owner_id=owner_id,
                    node_type=GraphNodeType.OSINT,
                    label=f"OSINT: {dr.title} ({dr.result_type})",
                    metadata={"result_type": dr.result_type, "title": dr.title},
                )
            )

        # Save all generated elements to repository
        repo = get_repository()
        repo.save_subgraph(tenant_id, workspace_id, nodes, edges)

        return ctx.with_updates(payload={"node_count": len(nodes), "edge_count": len(edges)})


class GraphBuildAuditStage(PipelineStage):
    priority = 900
    name = "GraphBuildAuditStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        AuditLog.objects.create(
            action="graph_built",
            performed_by=ctx.performed_by,
            organization=ctx.tenant,
            outcome="success",
            details={
                "workspace_id": ctx.payload.get("workspace_id"),
                "node_count": ctx.payload.get("node_count"),
                "edge_count": ctx.payload.get("edge_count"),
            },
        )
        return ctx


# ===========================================================================
# SYNC PIPELINE STAGES
# ===========================================================================

class GraphSyncValidationStage(PipelineStage):
    priority = 100
    name = "GraphSyncValidationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        if not ctx.tenant:
            raise ValidationError("Tenant isolation is required.")
        return ctx


class GraphSyncBusinessStage(PipelineStage):
    priority = 500
    name = "GraphSyncBusinessStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        tenant_id = str(ctx.tenant.id)
        workspace_id = str(ctx.payload.get("workspace_id")) if ctx.payload.get("workspace_id") else None
        owner_id = str(ctx.performed_by.id) if getattr(ctx, "performed_by", None) else None

        nodes_data = ctx.payload.get("nodes", [])
        edges_data = ctx.payload.get("edges", [])

        nodes = [
            NodeDTO(
                id=n["id"],
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                owner_id=owner_id,
                node_type=n.get("node_type", GraphNodeType.CUSTOM),
                label=n.get("label", "Node"),
                confidence=Decimal(str(n.get("confidence", "1.000"))),
                metadata=n.get("metadata", {}),
            )
            for n in nodes_data
        ]

        edges = [
            EdgeDTO(
                id=e["id"],
                tenant_id=tenant_id,
                source_id=e["source_id"],
                target_id=e["target_id"],
                owner_id=owner_id,
                relationship_type=e.get("relationship_type", GraphRelationshipType.CUSTOM),
                confidence=Decimal(str(e.get("confidence", "1.000"))),
                evidence_references=e.get("evidence_references", []),
                investigation_references=e.get("investigation_references", []),
            )
            for e in edges_data
        ]

        repo = get_repository()
        repo.save_subgraph(tenant_id, workspace_id, nodes, edges)

        return ctx


class GraphSyncAuditStage(PipelineStage):
    priority = 900
    name = "GraphSyncAuditStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        AuditLog.objects.create(
            action="graph_synced",
            performed_by=ctx.performed_by,
            organization=ctx.tenant,
            outcome="success",
            details={
                "workspace_id": ctx.payload.get("workspace_id"),
                "nodes_count": len(ctx.payload.get("nodes", [])),
                "edges_count": len(ctx.payload.get("edges", [])),
            },
        )
        return ctx


# ===========================================================================
# REBUILD/REFRESH PIPELINE STAGES
# ===========================================================================

class GraphRefreshValidationStage(PipelineStage):
    priority = 100
    name = "GraphRefreshValidationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        if not ctx.tenant:
            raise ValidationError("Tenant context is required.")
        return ctx


class GraphRefreshBusinessStage(PipelineStage):
    priority = 500
    name = "GraphRefreshBusinessStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        tenant_id = str(ctx.tenant.id)
        workspace_id = str(ctx.payload.get("workspace_id")) if ctx.payload.get("workspace_id") else None

        # Clear and build again
        repo = get_repository()
        repo.clear_subgraph(tenant_id, workspace_id)

        # Trigger internal build stage
        builder = GraphBuildBusinessStage()
        return builder.execute(ctx)


class GraphRefreshAuditStage(PipelineStage):
    priority = 900
    name = "GraphRefreshAuditStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        AuditLog.objects.create(
            action="graph_refreshed",
            performed_by=ctx.performed_by,
            organization=ctx.tenant,
            outcome="success",
            details={
                "workspace_id": ctx.payload.get("workspace_id"),
            },
        )
        return ctx
