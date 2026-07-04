import logging
from decimal import Decimal
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from backend.apps.common.pipeline.core import PipelineContext, PipelineStage
from backend.apps.audit.models.audit_log import AuditLog
from backend.apps.identity.choices import IdentityType, ReviewStatus, MergeAction
from backend.apps.identity.models import (
    Identity,
    IdentityAttribute,
    IdentityRelationship,
    IdentityMatch,
    IdentityMergeHistory,
)
from backend.apps.identity.services.scoring import calculate_identity_similarity

logger = logging.getLogger(__name__)


# ===========================================================================
# RESOLVE PIPELINE STAGES
# ===========================================================================

class IdentityResolveValidationStage(PipelineStage):
    priority = 100
    name = "IdentityResolveValidationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        payload = ctx.payload
        if not payload.get("label"):
            raise ValidationError("Identity label is required.")
        if not payload.get("entity_type"):
            raise ValidationError("Identity entity_type is required.")
        if payload.get("entity_type") not in IdentityType.values:
            raise ValidationError(f"Invalid entity type: {payload.get('entity_type')}")
        return ctx


class IdentityResolveAuthorizationStage(PipelineStage):
    priority = 200
    name = "IdentityResolveAuthorizationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        user = ctx.performed_by
        tenant = ctx.tenant
        if not tenant:
            raise PermissionDenied("A valid tenant organization context is required.")

        # Tenancy scope validation
        if (
            hasattr(user, "organizations")
            and not user.organizations.filter(id=tenant.id).exists()
            and getattr(user, "organization", None) != tenant
        ):
            raise PermissionDenied("User is not authorized for this tenant organization.")

        return ctx


class IdentityResolveCandidateDiscoveryStage(PipelineStage):
    priority = 300
    name = "IdentityResolveCandidateDiscoveryStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        # Create/resolve the base Identity first, or discover duplicates in database
        tenant_id = ctx.tenant.id
        label = ctx.payload.get("label")
        entity_type = ctx.payload.get("entity_type")
        assert isinstance(label, str)
        assert isinstance(entity_type, str)
        source = ctx.payload.get("source", "manual")
        workspace_id = ctx.payload.get("workspace_id")

        # Create new identity
        identity = Identity.objects.create(
            tenant_id=tenant_id,
            organization_id=tenant_id,
            workspace_id=workspace_id,
            label=label,
            entity_type=entity_type,
            source=source,
            owner=ctx.performed_by,
        )

        # Create initial attributes if provided
        attributes = ctx.payload.get("attributes", [])
        for attr in attributes:
            IdentityAttribute.objects.create(
                identity=identity,
                tenant_id=tenant_id,
                type=attr.get("type", entity_type),
                key=attr.get("key", "value"),
                value=attr.get("value"),
                normalized_value=attr.get("normalized_value") or attr.get("value", "").strip().lower(),
                confidence=Decimal(str(attr.get("confidence", "1.000"))),
                evidence_references=attr.get("evidence_references", []),
                owner=ctx.performed_by,
            )

        # Candidate discovery: Find potential duplicates matching this identity in the same tenant
        candidates = Identity.objects.filter(
            tenant_id=tenant_id,
            entity_type=entity_type,
            is_deleted=False,
        ).exclude(id=identity.id)

        ctx.metadata["identity"] = identity
        ctx.metadata["candidates"] = list(candidates)
        return ctx.with_updates(payload={"identity_id": identity.id})


class IdentityResolveSimilarityScoringStage(PipelineStage):
    priority = 400
    name = "IdentityResolveSimilarityScoringStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        identity = ctx.metadata.get("identity")
        assert isinstance(identity, Identity)
        candidates = ctx.metadata.get("candidates", [])
        matches_found = []

        for candidate in candidates:
            scoring_res = calculate_identity_similarity(identity, candidate)
            score = scoring_res["overall_score"]
            if score >= Decimal("0.500"):
                matches_found.append({
                    "candidate": candidate,
                    "score": score,
                    "details": scoring_res["components"],
                })

        ctx.metadata["matches_found"] = matches_found
        return ctx


class IdentityResolveConfidenceCalculationStage(PipelineStage):
    priority = 500
    name = "IdentityResolveConfidenceCalculationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        # Update the main identity confidence based on internal references/evidence quality
        identity = ctx.metadata.get("identity")
        assert isinstance(identity, Identity)
        # For simplicity, calculate average confidence of attributes
        attrs = identity.attributes.all()
        if attrs.exists():
            avg_confidence = sum(a.confidence for a in attrs) / attrs.count()
            identity.confidence_score = Decimal(str(round(avg_confidence, 3)))
            identity.save()
        return ctx


class IdentityResolveMergeDecisionStage(PipelineStage):
    priority = 600
    name = "IdentityResolveMergeDecisionStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        identity = ctx.metadata.get("identity")
        assert isinstance(identity, Identity)
        matches = ctx.metadata.get("matches_found", [])

        for match in matches:
            candidate = match["candidate"]
            score = match["score"]

            status = ReviewStatus.PENDING
            if Decimal("0.850") <= score < Decimal("0.980"):
                status = ReviewStatus.REQUIRES_REVIEW

            # Save the match candidate record
            IdentityMatch.objects.create(
                tenant_id=ctx.tenant.id,
                candidate_a=identity,
                candidate_b=candidate,
                confidence=score,
                matching_strategy="composite",
                review_status=status,
                owner=ctx.performed_by,
            )

        return ctx


class IdentityResolveEvidenceCorrelationStage(PipelineStage):
    priority = 700
    name = "IdentityResolveEvidenceCorrelationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        # Correlation metadata setup
        return ctx


class IdentityResolveTimelineStage(PipelineStage):
    priority = 800
    name = "IdentityResolveTimelineStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        identity = ctx.metadata.get("identity")
        assert isinstance(identity, Identity)
        workspace_id = identity.workspace_id
        if workspace_id:
            try:
                # Decoupled dynamic import to avoid circular dependency
                from backend.apps.investigations.models import (
                    Investigation,
                    InvestigationTimelineEvent,
                    TimelineEventType,
                )
                # Find investigations in this workspace
                investigations = Investigation.objects.filter(workspace_id=workspace_id)
                for inv in investigations:
                    InvestigationTimelineEvent.objects.create(
                        investigation=inv,
                        event_type="identity_resolved",  # Custom type or general type
                        description=f"Identity '{identity.label}' resolved and linked via engine.",
                    )
            except (ImportError, Exception) as e:
                logger.warning("Could not link identity timeline event: %s", e)
        return ctx


class IdentityResolveAuditStage(PipelineStage):
    priority = 900
    name = "IdentityResolveAuditStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        identity = ctx.metadata.get("identity")
        assert isinstance(identity, Identity)
        AuditLog.objects.create(
            action="identity_resolved",
            performed_by=ctx.performed_by,
            organization=ctx.tenant,
            outcome="success",
            details={
                "identity_id": str(identity.id),
                "label": identity.label,
                "type": identity.entity_type,
            },
        )
        return ctx


# ===========================================================================
# MERGE PIPELINE STAGES
# ===========================================================================

class IdentityMergeValidationStage(PipelineStage):
    priority = 100
    name = "IdentityMergeValidationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        id_a = ctx.payload.get("identity_a_id")
        id_b = ctx.payload.get("identity_b_id")
        if not id_a or not id_b:
            raise ValidationError("Both identity_a_id and identity_b_id are required for merging.")
        if id_a == id_b:
            raise ValidationError("Cannot merge an identity with itself.")
        return ctx


class IdentityMergeBusinessStage(PipelineStage):
    priority = 500
    name = "IdentityMergeBusinessStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        id_a_id = ctx.payload.get("identity_a_id")
        id_b_id = ctx.payload.get("identity_b_id")
        assert id_a_id is not None
        assert id_b_id is not None
        tenant_id = ctx.tenant.id

        # Wrap everything in a single database transaction for consistency
        with transaction.atomic():
            identity_a = Identity.objects.select_for_update().get(id=id_a_id, tenant_id=tenant_id)
            identity_b = Identity.objects.select_for_update().get(id=id_b_id, tenant_id=tenant_id)

            # Determine master and duplicate (keep the one with higher confidence or manual source)
            if identity_a.confidence_score >= identity_b.confidence_score:
                master = identity_a
                duplicate = identity_b
            else:
                master = identity_b
                duplicate = identity_a

            # Snapshot duplicate data for rollback metadata
            dup_attrs = []
            for attr in duplicate.attributes.all():
                dup_attrs.append({
                    "id": str(attr.id),
                    "type": attr.type,
                    "key": attr.key,
                    "value": attr.value,
                    "normalized_value": attr.normalized_value,
                    "confidence": str(attr.confidence),
                    "evidence_references": attr.evidence_references,
                })

            dup_relationships = []
            for rel in duplicate.relationships_from.all():
                dup_relationships.append({
                    "id": str(rel.id),
                    "target_id": str(rel.target_identity_id),
                    "type": rel.type,
                    "confidence": str(rel.confidence),
                    "source": rel.source,
                    "evidence_references": rel.evidence_references,
                })

            snapshot = {
                "label": duplicate.label,
                "entity_type": duplicate.entity_type,
                "confidence_score": str(duplicate.confidence_score),
                "confidence_details": duplicate.confidence_details,
                "source": duplicate.source,
                "attributes": dup_attrs,
                "relationships": dup_relationships,
            }

            # 1. Transfer attributes
            duplicate.attributes.update(identity=master)

            # 2. Transfer relationships
            duplicate.relationships_from.update(source_identity=master)
            duplicate.relationships_to.update(target_identity=master)

            # 3. Create merge history record
            IdentityMergeHistory.objects.create(
                tenant_id=tenant_id,
                source_identity_id=duplicate.id,
                target_identity=master,
                action=MergeAction.MERGE,
                merge_metadata=snapshot,
                reviewer=ctx.performed_by,
                owner=ctx.performed_by,
            )

            # 4. Soft-delete duplicate
            duplicate.is_deleted = True
            duplicate.deleted_at = timezone.now()
            duplicate.deleted_by = ctx.performed_by
            duplicate.save()

            # 5. Clean up IdentityMatch entries involving duplicate
            IdentityMatch.objects.filter(candidate_a=duplicate).delete()
            IdentityMatch.objects.filter(candidate_b=duplicate).delete()

            # 6. Recompute master score
            scoring_res = calculate_identity_similarity(master, master)  # self-recompute
            master.confidence_details = scoring_res.get("components", {})
            master.save()

        return ctx.with_updates(payload=master)


class IdentityMergeAuditStage(PipelineStage):
    priority = 900
    name = "IdentityMergeAuditStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        from typing import cast
        master = cast(Identity, ctx.payload)
        AuditLog.objects.create(
            action="identity_merged",
            performed_by=ctx.performed_by,
            organization=ctx.tenant,
            outcome="success",
            details={
                "master_identity_id": str(master.id),
                "master_label": master.label,
            },
        )
        return ctx


# ===========================================================================
# SPLIT PIPELINE STAGES
# ===========================================================================

class IdentitySplitValidationStage(PipelineStage):
    priority = 100
    name = "IdentitySplitValidationStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        history_id = ctx.payload.get("merge_history_id")
        if not history_id:
            raise ValidationError("merge_history_id is required for splitting.")
        return ctx


class IdentitySplitBusinessStage(PipelineStage):
    priority = 500
    name = "IdentitySplitBusinessStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        history_id = ctx.payload.get("merge_history_id")
        assert history_id is not None
        tenant_id = ctx.tenant.id

        with transaction.atomic():
            history = IdentityMergeHistory.objects.select_for_update().get(id=history_id, tenant_id=tenant_id)
            if history.action != MergeAction.MERGE:
                raise ValidationError("Can only split/rollback a previous MERGE action.")

            master = history.target_identity
            snapshot = history.merge_metadata

            # 1. Restore the merged/deleted identity
            restored = Identity.objects.get(id=history.source_identity_id)
            restored.is_deleted = False
            restored.deleted_at = None
            restored.deleted_by = None
            restored.save()

            # 2. Restore attributes belonging to restored identity
            attr_ids = [attr["id"] for attr in snapshot.get("attributes", [])]
            IdentityAttribute.objects.filter(id__in=attr_ids).update(identity=restored)

            # 3. Restore relationships
            rel_ids = [rel["id"] for rel in snapshot.get("relationships", [])]
            IdentityRelationship.objects.filter(id__in=rel_ids).update(source_identity=restored)

            # 4. Mark history as split
            history.action = MergeAction.SPLIT
            history.save()

        return ctx.with_updates(payload=master)


class IdentitySplitAuditStage(PipelineStage):
    priority = 900
    name = "IdentitySplitAuditStage"

    def execute(self, ctx: PipelineContext) -> PipelineContext:
        from typing import cast
        master = cast(Identity, ctx.payload)
        AuditLog.objects.create(
            action="identity_split",
            performed_by=ctx.performed_by,
            organization=ctx.tenant,
            outcome="success",
            details={
                "master_identity_id": str(master.id),
            },
        )
        return ctx
