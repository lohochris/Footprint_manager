from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import uuid

@dataclass(frozen=True)
class TaskDTO:
    id: uuid.UUID
    case_workspace_id: uuid.UUID
    title: str
    description: str
    status: str
    priority: str
    assignee_id: Optional[uuid.UUID]
    creator_id: Optional[uuid.UUID]
    due_date: Optional[str]

@dataclass(frozen=True)
class NotificationDTO:
    id: uuid.UUID
    user_id: uuid.UUID
    category: str
    priority: str
    title: str
    body: str
    is_read: bool

@dataclass(frozen=True)
class ActivityEventDTO:
    id: uuid.UUID
    case_workspace_id: uuid.UUID
    event_type: str
    actor_id: Optional[uuid.UUID]
    resource_type: str
    resource_id: Optional[uuid.UUID]
    payload: Dict[str, Any]
