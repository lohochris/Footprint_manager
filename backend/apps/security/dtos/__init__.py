from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID


@dataclass
class APIKeyDTO:
    id: UUID
    name: str
    owner_id: UUID
    key_hash: str
    scopes: List[str]
    expiration: Optional[datetime]
    last_used: Optional[datetime]
    status: str


@dataclass
class TrustedDeviceDTO:
    id: UUID
    owner_id: UUID
    fingerprint: str
    platform: str
    browser: str
    is_trusted: bool
    last_activity: Optional[datetime]


@dataclass
class SecuritySessionDTO:
    id: UUID
    user_id: UUID
    device_id: Optional[UUID]
    ip_address: str
    user_agent: str
    login_time: datetime
    logout_time: Optional[datetime]
    last_activity: datetime
    risk_score: float
    is_active: bool


@dataclass
class SecurityPolicyDTO:
    id: UUID
    name: str
    description: str
    require_mfa: bool
    password_min_length: int
    session_timeout_minutes: int
    api_key_max_expiry_days: int
    allowed_ips: List[str]
    is_active: bool


@dataclass
class SecurityContext:
    """Represents a structured context for security evaluations."""
    user_id: UUID
    tenant_id: UUID
    organization_id: UUID
    ip_address: str
    user_agent: str
    device_fingerprint: Optional[str] = None
    session_id: Optional[UUID] = None
    risk_score: float = 0.0
    is_mfa_authenticated: bool = False
    
    def as_dict(self) -> Dict[str, Any]:
        return {
            "user_id": str(self.user_id),
            "tenant_id": str(self.tenant_id),
            "organization_id": str(self.organization_id),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "device_fingerprint": self.device_fingerprint,
            "session_id": str(self.session_id) if self.session_id else None,
            "risk_score": self.risk_score,
            "is_mfa_authenticated": self.is_mfa_authenticated,
        }
