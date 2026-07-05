import abc
from typing import Any, Dict, Optional

class BaseIntegrationProvider(abc.ABC):
    @property
    @abc.abstractmethod
    def provider_id(self) -> str:
        pass

    @abc.abstractmethod
    def deliver(self, endpoint_url: str, payload: Dict[str, Any], credentials: Optional[str] = None) -> Dict[str, Any]:
        """
        Deliver payload to the external system.
        Must return a standardized response dictionary or raise an exception.
        """
        pass
