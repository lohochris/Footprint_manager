import uuid
from typing import Dict, Any, List
from ..dto import NotificationDTO
from ..repositories import NotificationRepository
from ..selectors import NotificationSelector
from ..providers.registry import notification_provider_registry

class NotificationService:
    def notify_user(self, tenant_id: uuid.UUID, user_id: uuid.UUID, category: str, title: str, body: str = "", provider_id: str = "in_app") -> NotificationDTO:
        # 1. Persistence-first notification
        notification = NotificationRepository.create(
            tenant_id=tenant_id,
            user_id=user_id,
            category=category,
            title=title,
            body=body
        )

        # 2. Invoke provider
        provider = notification_provider_registry.get(provider_id)
        if provider:
            provider.deliver(tenant_id, user_id, {"title": title, "body": body, "category": category})

        return self._to_dto(notification)

    def mark_as_read(self, tenant_id: uuid.UUID, user_id: uuid.UUID, notification_ids: List[uuid.UUID]):
        NotificationRepository.mark_read(tenant_id, user_id, notification_ids)

    def _to_dto(self, notification) -> NotificationDTO:
        return NotificationDTO(
            id=notification.id,
            user_id=notification.user_id,
            category=notification.category,
            priority=notification.priority,
            title=notification.title,
            body=notification.body,
            is_read=notification.is_read
        )
