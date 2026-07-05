import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime

@dataclass
class IntegrationDTO:
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    provider: str
    status: str
    is_enabled: bool
    configuration: Dict[str, Any]

@dataclass
class EndpointDTO:
    id: uuid.UUID
    integration_id: uuid.UUID
    endpoint_type: str
    url: str

@dataclass
class SubscriptionDTO:
    id: uuid.UUID
    integration_id: uuid.UUID
    event_name: str
    is_active: bool

@dataclass
class EventDTO:
    id: uuid.UUID
    direction: str
    event_type: str
    payload: Dict[str, Any]
    status: str
    idempotency_key: str
