import abc
from typing import Dict, Any, List
import uuid

class BaseNotificationProvider(abc.ABC):
    """
    Interface for notification delivery mechanisms.
    """

    @property
    @abc.abstractmethod
    def provider_id(self) -> str:
        """Return the unique identifier for this provider."""
        pass

    @abc.abstractmethod
    def deliver(self, tenant_id: uuid.UUID, user_id: uuid.UUID, notification_data: Dict[str, Any]) -> bool:
        """
        Deliver a notification to the user.
        Must return True if successfully delivered/queued, False otherwise.
        """
        pass

    @abc.abstractmethod
    def deliver_bulk(self, tenant_id: uuid.UUID, user_ids: List[uuid.UUID], notification_data: Dict[str, Any]) -> Dict[uuid.UUID, bool]:
        """
        Deliver a notification to multiple users.
        Returns a mapping of user_id to success status.
        """
        pass
