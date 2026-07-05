import uuid
from typing import Optional, List
from ..dto import TaskDTO
from ..repositories import TaskRepository, ActivityEventRepository
from ..selectors import TaskSelector
from ..models import Task
from backend.shared.events.bus import DomainEventBus

class TaskService:
    def __init__(self, event_bus: DomainEventBus):
        self.event_bus = event_bus

    def create_task(self, tenant_id: uuid.UUID, workspace_id: uuid.UUID, creator_id: uuid.UUID, title: str, description: str = "", priority: str = "medium") -> TaskDTO:
        task = TaskRepository.create(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            title=title,
            description=description,
            priority=priority,
            creator_id=creator_id
        )

        ActivityEventRepository.append_event(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            event_type="Task Created",
            actor_id=creator_id,
            resource_type="Task",
            resource_id=task.id,
            payload={"title": task.title}
        )

        # Publish domain event
        self.event_bus.publish(
            event_name="collaboration.task.created",
            payload={"task_id": str(task.id), "workspace_id": str(workspace_id), "creator_id": str(creator_id)}
        )

        return self._to_dto(task)

    def assign_task(self, tenant_id: uuid.UUID, task_id: uuid.UUID, assignee_id: uuid.UUID, assigned_by: uuid.UUID) -> Optional[TaskDTO]:
        task = TaskRepository.update(tenant_id, task_id, assignee_id=assignee_id)
        if task:
            ActivityEventRepository.append_event(
                tenant_id=tenant_id,
                workspace_id=task.case_workspace_id,
                event_type="Task Assigned",
                actor_id=assigned_by,
                resource_type="Task",
                resource_id=task.id,
                payload={"assignee_id": str(assignee_id)}
            )

            self.event_bus.publish(
                event_name="collaboration.task.assigned",
                payload={"task_id": str(task.id), "assignee_id": str(assignee_id), "assigned_by": str(assigned_by)}
            )
            return self._to_dto(task)
        return None

    def _to_dto(self, task: Task) -> TaskDTO:
        return TaskDTO(
            id=task.id,
            case_workspace_id=task.case_workspace_id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            assignee_id=task.assignee_id,
            creator_id=task.creator_id,
            due_date=str(task.due_date) if task.due_date else None
        )
