from typing import Any, Dict, List, Optional
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist

from ..models import (
    ApprovalRequest,
    ApprovalWorkflow,
    ComplianceEvaluation,
    ComplianceRule,
    GovernanceAudit,
    GovernancePolicy,
    LegalHold,
    RetentionPolicy,
    TrustAssessment,
)


class PolicyRepository:
    def get_policy(self, policy_id: UUID, tenant_id: UUID) -> Optional[GovernancePolicy]:
        try:
            return GovernancePolicy.objects.get(id=policy_id, workspace_id=tenant_id)
        except ObjectDoesNotExist:
            return None

    def list_policies(self, tenant_id: UUID) -> List[GovernancePolicy]:
        return list(GovernancePolicy.objects.filter(workspace_id=tenant_id))


class ApprovalRepository:
    def get_workflow(self, workflow_id: UUID, tenant_id: UUID) -> Optional[ApprovalWorkflow]:
        try:
            return ApprovalWorkflow.objects.get(id=workflow_id, workspace_id=tenant_id)
        except ObjectDoesNotExist:
            return None

    def create_request(
        self,
        workflow: ApprovalWorkflow,
        requester_id: UUID,
        resource_type: str,
        resource_id: UUID,
        tenant_id: UUID,
        justification: str = "",
    ) -> ApprovalRequest:
        return ApprovalRequest.objects.create(
            workflow=workflow,
            requester_id=requester_id,
            resource_type=resource_type,
            resource_id=resource_id,
            justification=justification,
            workspace_id=tenant_id,
            organization_id=workflow.organization_id,
        )


class ComplianceRepository:
    def list_rules(self, tenant_id: UUID) -> List[ComplianceRule]:
        return list(ComplianceRule.objects.filter(workspace_id=tenant_id))

    def create_evaluation(
        self,
        rule: ComplianceRule,
        resource_type: str,
        resource_id: UUID,
        status: str,
        details: Dict[str, Any],
        tenant_id: UUID,
    ) -> ComplianceEvaluation:
        return ComplianceEvaluation.objects.create(
            rule=rule,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            details=details,
            workspace_id=tenant_id,
            organization_id=rule.organization_id,
        )


class TrustRepository:
    def get_assessment(
        self, resource_type: str, resource_id: UUID, tenant_id: UUID
    ) -> Optional[TrustAssessment]:
        try:
            return TrustAssessment.objects.get(
                resource_type=resource_type,
                resource_id=resource_id,
                workspace_id=tenant_id,
            )
        except ObjectDoesNotExist:
            return None


class AuditRepository:
    def create_audit(
        self,
        action_type: str,
        resource_type: str,
        resource_id: UUID,
        details: Dict[str, Any],
        tenant_id: UUID,
        organization_id: UUID,
        actor_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
    ) -> GovernanceAudit:
        return GovernanceAudit.objects.create(
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            workspace_id=tenant_id,
            organization_id=organization_id,
            actor_id=actor_id,
            ip_address=ip_address,
        )

__all__ = [
    "PolicyRepository",
    "ApprovalRepository",
    "ComplianceRepository",
    "TrustRepository",
    "AuditRepository",
]
