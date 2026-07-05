import uuid
from typing import List, Optional, Dict, Any
from .models import (
    CaseWorkspace, Task, Assignment, Comment, Mention,
    Notification, Watchlist, Bookmark, SharedNote, ActivityEvent
)

class CaseWorkspaceRepository:
    @staticmethod
    def create(tenant_id: uuid.UUID, name: str, **kwargs) -> CaseWorkspace:
        return CaseWorkspace.objects.create(tenant_id=tenant_id, name=name, **kwargs)

    @staticmethod
    def update(tenant_id: uuid.UUID, workspace_id: uuid.UUID, **kwargs) -> Optional[CaseWorkspace]:
        updated = CaseWorkspace.objects.filter(tenant_id=tenant_id, id=workspace_id).update(**kwargs)
        if updated:
            return CaseWorkspace.objects.get(tenant_id=tenant_id, id=workspace_id)
        return None

class TaskRepository:
    @staticmethod
    def create(tenant_id: uuid.UUID, workspace_id: uuid.UUID, title: str, **kwargs) -> Task:
        return Task.objects.create(tenant_id=tenant_id, case_workspace_id=workspace_id, title=title, **kwargs)

    @staticmethod
    def update(tenant_id: uuid.UUID, task_id: uuid.UUID, **kwargs) -> Optional[Task]:
        updated = Task.objects.filter(tenant_id=tenant_id, id=task_id).update(**kwargs)
        if updated:
            return Task.objects.get(tenant_id=tenant_id, id=task_id)
        return None

class NotificationRepository:
    @staticmethod
    def create(tenant_id: uuid.UUID, user_id: uuid.UUID, category: str, title: str, **kwargs) -> Notification:
        return Notification.objects.create(
            tenant_id=tenant_id,
            user_id=user_id,
            category=category,
            title=title,
            **kwargs
        )

    @staticmethod
    def mark_read(tenant_id: uuid.UUID, user_id: uuid.UUID, notification_ids: List[uuid.UUID]):
        from django.utils import timezone
        Notification.objects.filter(
            tenant_id=tenant_id,
            user_id=user_id,
            id__in=notification_ids
        ).update(is_read=True, read_at=timezone.now())

class ActivityEventRepository:
    @staticmethod
    def append_event(tenant_id: uuid.UUID, workspace_id: uuid.UUID, event_type: str, **kwargs) -> ActivityEvent:
        # Append-only / immutable
        return ActivityEvent.objects.create(
            tenant_id=tenant_id,
            case_workspace_id=workspace_id,
            event_type=event_type,
            **kwargs
        )
