from typing import Callable, Dict, List
import structlog

logger = structlog.get_logger(__name__)

class DomainEventBus:
    """
    A lightweight internal event bus for the platform.
    Allows decoupling domain logic from execution hooks across bounded contexts.
    """
    _subscribers: Dict[str, List[Callable]] = {}

    @classmethod
    def subscribe(cls, event_name: str, handler: Callable) -> None:
        if event_name not in cls._subscribers:
            cls._subscribers[event_name] = []
        cls._subscribers[event_name].append(handler)

    @classmethod
    def publish(cls, event_name: str, **kwargs) -> None:
        logger.debug("event_bus.published", event_name=event_name)
        handlers = cls._subscribers.get(event_name, [])
        for handler in handlers:
            try:
                handler(**kwargs)
            except Exception as e:
                logger.error("event_bus.handler_failed", event_name=event_name, error=str(e))
