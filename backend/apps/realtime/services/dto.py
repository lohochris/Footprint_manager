import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime

@dataclass
class ChannelDTO:
    id: uuid.UUID
    tenant_id: uuid.UUID
    channel_type: str
    resource_identifier: str
    permissions_required: List[str]

@dataclass
class ConnectionDTO:
    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    protocol: str
    session_id: str
    state: str

@dataclass
class SubscriptionDTO:
    id: uuid.UUID
    tenant_id: uuid.UUID
    channel_id: uuid.UUID
    connection_id: uuid.UUID
    status: str

@dataclass
class StreamEventDTO:
    sequence_number: int
    channel_id: uuid.UUID
    event_type: str
    payload: Dict[str, Any]
    status: str

@dataclass
class PresenceDTO:
    user_id: uuid.UUID
    status: str
    last_heartbeat_at: Optional[datetime]
