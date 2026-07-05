import uuid
from typing import List, Optional
from django.db.models import QuerySet
from .models import (
    CaseWorkspace, Task, Comment, Notification,
    Watchlist, Bookmark, SharedNote, ActivityEvent
)

class CaseWorkspaceSelector:
    @staticmethod
    def get_by_id(tenant_id: uuid.UUID, workspace_id: uuid.UUID) -> Optional[CaseWorkspace]:
        return CaseWorkspace.objects.filter(tenant_id=tenant_id, id=workspace_id).first()

    @staticmethod
    def list_active(tenant_id: uuid.UUID) -> QuerySet[CaseWorkspace]:
        return CaseWorkspace.objects.filter(tenant_id=tenant_id, status=CaseWorkspace.Status.ACTIVE)

class TaskSelector:
    @staticmethod
    def get_by_id(tenant_id: uuid.UUID, task_id: uuid.UUID) -> Optional[Task]:
        return Task.objects.filter(tenant_id=tenant_id, id=task_id).first()

    @staticmethod
    def list_by_workspace(tenant_id: uuid.UUID, workspace_id: uuid.UUID) -> QuerySet[Task]:
        return Task.objects.filter(tenant_id=tenant_id, case_workspace_id=workspace_id).select_related('assignee', 'creator')

    @staticmethod
    def list_assigned_to_user(tenant_id: uuid.UUID, user_id: uuid.UUID) -> QuerySet[Task]:
        return Task.objects.filter(tenant_id=tenant_id, assignee_id=user_id).exclude(status__in=[Task.Status.COMPLETED, Task.Status.ARCHIVED])

class NotificationSelector:
    @staticmethod
    def list_unread_for_user(tenant_id: uuid.UUID, user_id: uuid.UUID) -> QuerySet[Notification]:
        return Notification.objects.filter(tenant_id=tenant_id, user_id=user_id, is_read=False).order_by('-created_at')

class ActivityEventSelector:
    @staticmethod
    def list_by_workspace(tenant_id: uuid.UUID, workspace_id: uuid.UUID) -> QuerySet[ActivityEvent]:
        return ActivityEvent.objects.filter(tenant_id=tenant_id, case_workspace_id=workspace_id).order_by('-created_at')
