import uuid
from typing import Dict, Any
from backend.shared.events.bus import DomainEventBus
from .services.notification_service import NotificationService

class CollaborationEventSubscribers:
    """
    Subscribes to domain events across the platform and acts on them within the collaboration context.
    """
    def __init__(self, event_bus: DomainEventBus, notification_service: NotificationService):
        self.notification_service = notification_service
        event_bus.subscribe("collaboration.task.assigned", self.on_task_assigned)

    def on_task_assigned(self, payload: Dict[str, Any]):
        # E.g., send notification to the assignee
        assignee_id_str = payload.get("assignee_id")
        if not assignee_id_str:
            return

        assignee_id = uuid.UUID(assignee_id_str)
        # Assuming a default tenant context or retrieving from payload
        # In a real app, tenant_id would be passed in the payload or context
        tenant_id_str = payload.get("tenant_id")

        if tenant_id_str:
            self.notification_service.notify_user(
                tenant_id=uuid.UUID(tenant_id_str),
                user_id=assignee_id,
                category="task_assigned",
                title="New Task Assigned",
                body=f"You have been assigned to task {payload.get('task_id')}"
            )
