from typing import Any, Dict, List, Optional
from uuid import UUID

from django.db import transaction

from backend.shared.event_bus import EventBus

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
from ..repositories import (
    ApprovalRepository,
    AuditRepository,
    ComplianceRepository,
    PolicyRepository,
    TrustRepository,
)


class GovernancePolicyService:
    def __init__(self, repository: PolicyRepository, event_bus: EventBus):
        self.repository = repository
        self.event_bus = event_bus

    @transaction.atomic
    def activate_policy(self, policy_id: UUID, tenant_id: UUID, user_id: UUID) -> GovernancePolicy:
        policy = self.repository.get_policy(policy_id, tenant_id)
        if policy:
            policy.status = GovernancePolicy.Status.ACTIVE
            policy.save()
            self.event_bus.publish("PolicyActivated", {"policy_id": str(policy.id)})

            # Audit
            AuditRepository().create_audit(
                action_type=GovernanceAudit.ActionType.POLICY_CHANGE,
                resource_type="GovernancePolicy",
                resource_id=policy.id,
                details={"status": "ACTIVE"},
                tenant_id=tenant_id,
                organization_id=policy.organization_id,
                actor_id=user_id,
            )

        return policy


class ApprovalService:
    def __init__(self, repository: ApprovalRepository, event_bus: EventBus):
        self.repository = repository
        self.event_bus = event_bus

    @transaction.atomic
    def request_approval(
        self,
        workflow_id: UUID,
        requester_id: UUID,
        resource_type: str,
        resource_id: UUID,
        tenant_id: UUID,
        justification: str = "",
    ) -> ApprovalRequest:
        workflow = self.repository.get_workflow(workflow_id, tenant_id)
        if not workflow:
            raise ValueError("Workflow not found")

        request = self.repository.create_request(
            workflow=workflow,
            requester_id=requester_id,
            resource_type=resource_type,
            resource_id=resource_id,
            tenant_id=tenant_id,
            justification=justification,
        )

        self.event_bus.publish(
            "ApprovalRequested",
            {
                "request_id": str(request.id),
                "resource_type": resource_type,
                "resource_id": str(resource_id),
            },
        )

        AuditRepository().create_audit(
            action_type=GovernanceAudit.ActionType.APPROVAL,
            resource_type=resource_type,
            resource_id=resource_id,
            details={"request_id": str(request.id), "status": request.status},
            tenant_id=tenant_id,
            organization_id=workflow.organization_id,
            actor_id=requester_id,
        )

        return request

    @transaction.atomic
    def approve_request(self, request_id: UUID, reviewer_id: UUID, tenant_id: UUID) -> ApprovalRequest:
        request = ApprovalRequest.objects.get(id=request_id, workspace_id=tenant_id)
        request.status = ApprovalRequest.Status.APPROVED
        request.save()

        self.event_bus.publish(
            "ApprovalCompleted",
            {
                "request_id": str(request.id),
                "resource_type": request.resource_type,
                "resource_id": str(request.resource_id),
                "status": "APPROVED",
            },
        )

        AuditRepository().create_audit(
            action_type=GovernanceAudit.ActionType.APPROVAL,
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            details={"request_id": str(request.id), "status": request.status, "reviewer_id": str(reviewer_id)},
            tenant_id=tenant_id,
            organization_id=request.organization_id,
            actor_id=reviewer_id,
        )

        return request


class ComplianceService:
    def __init__(self, repository: ComplianceRepository, event_bus: EventBus):
        self.repository = repository
        self.event_bus = event_bus

    @transaction.atomic
    def evaluate_resource(
        self,
        rule_id: UUID,
        resource_type: str,
        resource_id: UUID,
        tenant_id: UUID,
    ) -> ComplianceEvaluation:
        rule = ComplianceRule.objects.get(id=rule_id, workspace_id=tenant_id)

        # In a real scenario, this would use a ComplianceProvider to do the evaluation.
        # For now, we mock the result.
        status = ComplianceEvaluation.Status.PASSED
        details = {"reason": "Auto-evaluated"}

        evaluation = self.repository.create_evaluation(
            rule=rule,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            details=details,
            tenant_id=tenant_id,
        )

        if status in [ComplianceEvaluation.Status.FAILED, ComplianceEvaluation.Status.WARNING]:
            self.event_bus.publish(
                "ComplianceViolation",
                {
                    "evaluation_id": str(evaluation.id),
                    "resource_type": resource_type,
                    "resource_id": str(resource_id),
                    "status": status,
                },
            )

        AuditRepository().create_audit(
            action_type=GovernanceAudit.ActionType.COMPLIANCE_EVALUATION,
            resource_type=resource_type,
            resource_id=resource_id,
            details={"evaluation_id": str(evaluation.id), "status": status},
            tenant_id=tenant_id,
            organization_id=rule.organization_id,
        )

        return evaluation


class RetentionService:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    @transaction.atomic
    def apply_legal_hold(
        self,
        name: str,
        resource_type: str,
        resource_id: UUID,
        reason: str,
        tenant_id: UUID,
        organization_id: UUID,
        user_id: UUID,
    ) -> LegalHold:
        hold = LegalHold.objects.create(
            name=name,
            resource_type=resource_type,
            resource_id=resource_id,
            reason=reason,
            workspace_id=tenant_id,
            organization_id=organization_id,
        )

        AuditRepository().create_audit(
            action_type=GovernanceAudit.ActionType.LEGAL_HOLD,
            resource_type=resource_type,
            resource_id=resource_id,
            details={"hold_id": str(hold.id), "active": True},
            tenant_id=tenant_id,
            organization_id=organization_id,
            actor_id=user_id,
        )

        return hold

    def run_retention_checks(self):
        # Implementation to scan resources against policies and emit RetentionAction events
        pass


class TrustService:
    def __init__(self, repository: TrustRepository, event_bus: EventBus):
        self.repository = repository
        self.event_bus = event_bus

    @transaction.atomic
    def update_trust(
        self,
        resource_type: str,
        resource_id: UUID,
        tenant_id: UUID,
        organization_id: UUID,
        composite_score: float,
        factors: List[Dict[str, Any]],
    ) -> TrustAssessment:
        assessment, created = TrustAssessment.objects.update_or_create(
            resource_type=resource_type,
            resource_id=resource_id,
            workspace_id=tenant_id,
            defaults={
                "composite_score": composite_score,
                "confidence_level": "HIGH" if composite_score > 80 else "LOW",
                "organization_id": organization_id,
            },
        )
        # Update factors would happen here

        return assessment


class AuditService:
    def __init__(self, repository: AuditRepository):
        self.repository = repository

    def log_action(
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
        return self.repository.create_audit(
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            tenant_id=tenant_id,
            organization_id=organization_id,
            actor_id=actor_id,
            ip_address=ip_address,
        )
