from typing import List
from uuid import UUID

from django.db.models import QuerySet

from ..models import (
    ApprovalRequest,
    ApprovalWorkflow,
    ComplianceEvaluation,
    GovernanceAudit,
    GovernancePolicy,
    LegalHold,
    RetentionPolicy,
    TrustAssessment,
)


def get_active_policies_for_tenant(tenant_id: UUID) -> QuerySet[GovernancePolicy]:
    return GovernancePolicy.objects.filter(
        workspace_id=tenant_id,
        status=GovernancePolicy.Status.ACTIVE,
    )


def get_pending_approvals_for_user(user_id: UUID, tenant_id: UUID) -> QuerySet[ApprovalRequest]:
    return ApprovalRequest.objects.filter(
        workspace_id=tenant_id,
        requester_id=user_id,
        status=ApprovalRequest.Status.PENDING,
    )


def get_compliance_evaluations_for_resource(
    resource_type: str, resource_id: UUID, tenant_id: UUID
) -> QuerySet[ComplianceEvaluation]:
    return ComplianceEvaluation.objects.filter(
        workspace_id=tenant_id,
        resource_type=resource_type,
        resource_id=resource_id,
    )


def get_trust_assessment_for_resource(
    resource_type: str, resource_id: UUID, tenant_id: UUID
) -> QuerySet[TrustAssessment]:
    return TrustAssessment.objects.filter(
        workspace_id=tenant_id,
        resource_type=resource_type,
        resource_id=resource_id,
    )


def get_active_legal_holds_for_resource(
    resource_type: str, resource_id: UUID, tenant_id: UUID
) -> QuerySet[LegalHold]:
    return LegalHold.objects.filter(
        workspace_id=tenant_id,
        resource_type=resource_type,
        resource_id=resource_id,
        active=True,
    )


def get_retention_policies_for_resource_type(
    resource_type: str, tenant_id: UUID
) -> QuerySet[RetentionPolicy]:
    return RetentionPolicy.objects.filter(
        workspace_id=tenant_id,
        resource_type=resource_type,
        is_active=True,
    )


def get_audit_trail_for_resource(
    resource_type: str, resource_id: UUID, tenant_id: UUID
) -> QuerySet[GovernanceAudit]:
    return GovernanceAudit.objects.filter(
        workspace_id=tenant_id,
        resource_type=resource_type,
        resource_id=resource_id,
    ).order_by("-timestamp")
