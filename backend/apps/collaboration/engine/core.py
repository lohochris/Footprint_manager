from backend.shared.events.bus import DomainEventBus
from ..services.task_service import TaskService
from ..services.notification_service import NotificationService
from ..events import CollaborationEventSubscribers

class CollaborationEngine:
    """
    Orchestration core for the collaboration context.
    Delegates domain logic to services and coordinates cross-service behavior.
    """
    def __init__(self, event_bus: DomainEventBus):
        self.event_bus = event_bus
        self.notification_service = NotificationService()
        self.task_service = TaskService(event_bus=self.event_bus)

        self.subscribers = CollaborationEventSubscribers(
            event_bus=self.event_bus,
            notification_service=self.notification_service
        )

    def initialize(self):
        # Setup specific orchestration logic if needed
        pass
