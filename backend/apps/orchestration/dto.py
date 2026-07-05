import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class PlaybookDTO:
    id: str
    name: str
    description: str
    is_active: bool

@dataclass
class WorkflowExecutionDTO:
    id: str
    playbook_version_id: str
    status: str
    outputs: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PlaybookExecutionParams:
    tenant_id: uuid.UUID
    playbook_version_id: uuid.UUID
    workspace_id: uuid.UUID | None = None
    creator_id: int | None = None
    variables: Dict[str, Any] = field(default_factory=dict)
