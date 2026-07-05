from typing import List, Optional
from uuid import UUID

from django.db.models import QuerySet

from ..models import APIKey, SecurityEvent, SecurityPolicy, SecuritySession, TrustedDevice


class APIKeySelector:
    def get_user_keys(self, user_id: UUID, tenant_id: UUID) -> QuerySet[APIKey]:
        return APIKey.objects.filter(owner_id=user_id, workspace_id=tenant_id).order_by("-created_at")


class SessionSelector:
    def get_user_sessions(self, user_id: UUID, tenant_id: UUID) -> QuerySet[SecuritySession]:
        return SecuritySession.objects.filter(user_id=user_id, workspace_id=tenant_id).order_by("-login_time")


class DeviceSelector:
    def get_user_devices(self, user_id: UUID, tenant_id: UUID) -> QuerySet[TrustedDevice]:
        return TrustedDevice.objects.filter(owner_id=user_id, workspace_id=tenant_id).order_by("-last_activity")


class EventSelector:
    def get_events_for_tenant(self, tenant_id: UUID, limit: int = 100) -> QuerySet[SecurityEvent]:
        return SecurityEvent.objects.filter(workspace_id=tenant_id).order_by("-timestamp")[:limit]

__all__ = [
    "APIKeySelector",
    "SessionSelector",
    "DeviceSelector",
    "EventSelector",
]
