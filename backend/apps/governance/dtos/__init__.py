from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from uuid import UUID


@dataclass
class GovernancePolicyDTO:
    id: UUID
    name: str
    description: str
    scope: str
    version: str
    status: str
    applicability_rules: Dict[str, Any]
    owner_id: UUID


@dataclass
class ApprovalWorkflowDTO:
    id: UUID
    name: str
    description: str
    policy_id: Optional[UUID]


@dataclass
class ApprovalStageDTO:
    id: UUID
    workflow_id: UUID
    name: str
    order: int
    stage_type: str
    required_approvals: int
    timeout_hours: Optional[int]


@dataclass
class ApprovalRequestDTO:
    id: UUID
    workflow_id: UUID
    current_stage_id: Optional[UUID]
    requester_id: UUID
    status: str
    resource_type: str
    resource_id: UUID
    justification: str


@dataclass
class ComplianceRuleDTO:
    id: UUID
    policy_id: UUID
    name: str
    description: str
    rule_type: str
    configuration: Dict[str, Any]


@dataclass
class ComplianceEvaluationDTO:
    id: UUID
    rule_id: UUID
    resource_type: str
    resource_id: UUID
    status: str
    details: Dict[str, Any]


@dataclass
class LegalHoldDTO:
    id: UUID
    name: str
    description: str
    resource_type: str
    resource_id: UUID
    active: bool
    reason: str


@dataclass
class RetentionPolicyDTO:
    id: UUID
    policy_id: UUID
    name: str
    description: str
    resource_type: str
    duration_days: int
    action: str
    is_active: bool


@dataclass
class TrustAssessmentDTO:
    id: UUID
    resource_type: str
    resource_id: UUID
    composite_score: float
    confidence_level: str


@dataclass
class TrustFactorDTO:
    id: UUID
    assessment_id: UUID
    name: str
    description: str
    source: str
    score: float
    weight: float


@dataclass
class GovernanceAuditDTO:
    id: UUID
    action_type: str
    resource_type: str
    resource_id: UUID
    actor_id: Optional[UUID]
    details: Dict[str, Any]
    ip_address: Optional[str]
