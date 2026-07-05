from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import TaskSerializer, AssignTaskSerializer, NotificationSerializer
from ..services.task_service import TaskService
from ..services.notification_service import NotificationService
from ..selectors import TaskSelector, NotificationSelector
from backend.shared.events.bus import DomainEventBus

# Instantiate global services
event_bus = DomainEventBus()
task_service = TaskService(event_bus)
notification_service = NotificationService()

class TaskViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        tenant_id = request.user.tenant_id
        workspace_id = request.query_params.get("workspace_id")

        if workspace_id:
            tasks = TaskSelector.list_by_workspace(tenant_id, workspace_id)
        else:
            tasks = TaskSelector.list_assigned_to_user(tenant_id, request.user.id)

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def create(self, request):
        tenant_id = request.user.tenant_id
        workspace_id = request.data.get("case_workspace_id")
        title = request.data.get("title")
        description = request.data.get("description", "")
        priority = request.data.get("priority", "medium")

        task_dto = task_service.create_task(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            creator_id=request.user.id,
            title=title,
            description=description,
            priority=priority
        )
        return Response({"id": task_dto.id, "title": task_dto.title}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        tenant_id = request.user.tenant_id
        serializer = AssignTaskSerializer(data=request.data)
        if serializer.is_valid():
            assignee_id = serializer.validated_data["assignee_id"]
            task_dto = task_service.assign_task(
                tenant_id=tenant_id,
                task_id=pk,
                assignee_id=assignee_id,
                assigned_by=request.user.id
            )
            if task_dto:
                return Response({"status": "assigned"})
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NotificationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        tenant_id = request.user.tenant_id
        notifications = NotificationSelector.list_unread_for_user(tenant_id, request.user.id)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def mark_read(self, request):
        tenant_id = request.user.tenant_id
        notification_ids = request.data.get("notification_ids", [])
        notification_service.mark_as_read(tenant_id, request.user.id, notification_ids)
        return Response({"status": "marked as read"})
