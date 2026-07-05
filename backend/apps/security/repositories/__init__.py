from typing import Any, Dict, List, Optional
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist

from ..models import (
    APIKey,
    SecurityEvent,
    SecurityPolicy,
    SecuritySession,
    TrustedDevice,
)


class APIKeyRepository:
    def create_api_key(
        self,
        name: str,
        owner_id: UUID,
        key_hash: str,
        scopes: List[str],
        tenant_id: UUID,
        organization_id: UUID,
        expiration: Optional[Any] = None,
    ) -> APIKey:
        return APIKey.objects.create(
            name=name,
            owner_id=owner_id,
            key_hash=key_hash,
            scopes=scopes,
            workspace_id=tenant_id,
            organization_id=organization_id,
            expiration=expiration,
        )

    def get_by_hash(self, key_hash: str) -> Optional[APIKey]:
        try:
            return APIKey.objects.get(key_hash=key_hash, status=APIKey.Status.ACTIVE)
        except ObjectDoesNotExist:
            return None


class SessionRepository:
    def create_session(
        self,
        user_id: UUID,
        ip_address: str,
        user_agent: str,
        tenant_id: UUID,
        organization_id: UUID,
        device_id: Optional[UUID] = None,
        risk_score: float = 0.0,
    ) -> SecuritySession:
        return SecuritySession.objects.create(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            workspace_id=tenant_id,
            organization_id=organization_id,
            device_id=device_id,
            risk_score=risk_score,
        )

    def get_active_session(self, session_id: UUID) -> Optional[SecuritySession]:
        try:
            return SecuritySession.objects.get(id=session_id, is_active=True)
        except ObjectDoesNotExist:
            return None


class DeviceRepository:
    def get_or_create_device(
        self,
        owner_id: UUID,
        fingerprint: str,
        platform: str,
        browser: str,
        tenant_id: UUID,
        organization_id: UUID,
    ) -> TrustedDevice:
        device, _ = TrustedDevice.objects.get_or_create(
            owner_id=owner_id,
            fingerprint=fingerprint,
            workspace_id=tenant_id,
            defaults={
                "platform": platform,
                "browser": browser,
                "organization_id": organization_id,
            },
        )
        return device


class PolicyRepository:
    def get_active_policy(self, tenant_id: UUID) -> Optional[SecurityPolicy]:
        return SecurityPolicy.objects.filter(is_active=True, workspace_id=tenant_id).first()


class EventRepository:
    def log_event(
        self,
        event_type: str,
        tenant_id: UUID,
        organization_id: UUID,
        actor_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: str = "",
        details: Optional[Dict[str, Any]] = None,
    ) -> SecurityEvent:
        return SecurityEvent.objects.create(
            event_type=event_type,
            workspace_id=tenant_id,
            organization_id=organization_id,
            actor_id=actor_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
        )

__all__ = [
    "APIKeyRepository",
    "SessionRepository",
    "DeviceRepository",
    "PolicyRepository",
    "EventRepository",
]
