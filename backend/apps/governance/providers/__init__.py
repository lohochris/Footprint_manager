import abc
from typing import Any, Dict, List, Optional
from uuid import UUID

from ..dtos import (
    ApprovalRequestDTO,
    ApprovalWorkflowDTO,
    ComplianceEvaluationDTO,
    ComplianceRuleDTO,
    RetentionPolicyDTO,
    TrustAssessmentDTO,
)


class BaseComplianceProvider(abc.ABC):
    @abc.abstractmethod
    def evaluate_rule(
        self,
        rule: ComplianceRuleDTO,
        resource_type: str,
        resource_id: UUID,
        context: Dict[str, Any],
    ) -> ComplianceEvaluationDTO:
        """Evaluate a compliance rule against a resource."""
        pass


class BaseApprovalProvider(abc.ABC):
    @abc.abstractmethod
    def route_approval(
        self,
        workflow: ApprovalWorkflowDTO,
        request: ApprovalRequestDTO,
        context: Dict[str, Any],
    ) -> ApprovalRequestDTO:
        """Route an approval request to the appropriate reviewers."""
        pass


class BaseRetentionProvider(abc.ABC):
    @abc.abstractmethod
    def enforce_policy(
        self,
        policy: RetentionPolicyDTO,
        resource_type: str,
        resource_id: UUID,
    ) -> bool:
        """Enforce a retention policy on a resource."""
        pass


class BaseTrustProvider(abc.ABC):
    @abc.abstractmethod
    def calculate_trust(
        self,
        resource_type: str,
        resource_id: UUID,
        factors: List[Dict[str, Any]],
    ) -> TrustAssessmentDTO:
        """Calculate a trust assessment based on provided factors."""
        pass

__all__ = [
    "BaseComplianceProvider",
    "BaseApprovalProvider",
    "BaseRetentionProvider",
    "BaseTrustProvider",
]
