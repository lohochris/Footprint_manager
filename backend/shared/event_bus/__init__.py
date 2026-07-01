"""
Event bus interfaces for Footprint Manager.

Provides the abstract contracts for event handling and dispatching.
Concrete implementations (in-process synchronous, Celery, Kafka) are
registered in their respective app packages.

Design:
- ``EventHandler`` — protocol for any class that handles a specific event type.
- ``EventDispatcher`` — abstract base for event routing and delivery.
- ``InProcessEventDispatcher`` — synchronous in-process dispatcher for
  use in development, testing, and early production before message brokers
  are introduced.

Usage::

    from shared.event_bus import EventDispatcher, EventHandler, InProcessEventDispatcher
    from shared.events import BaseDomainEvent

    class AuditHandler(EventHandler[BaseDomainEvent]):
        def handle(self, event):
            ...

    dispatcher = InProcessEventDispatcher()
    dispatcher.register(BaseDomainEvent, AuditHandler())
    dispatcher.dispatch(some_event)
"""

from __future__ import annotations

import abc
import logging
from typing import Generic, TypeVar

from shared.events import BaseDomainEvent

logger = logging.getLogger(__name__)

E = TypeVar("E", bound=BaseDomainEvent)


class EventHandler(Generic[E], abc.ABC):
    """
    Abstract handler for a specific domain event type.

    Each handler should be responsible for a single side-effect or reaction
    to an event.  Multiple handlers may be registered for the same event type.

    Type parameter:
        E: The concrete ``BaseDomainEvent`` subclass this handler processes.
    """

    @abc.abstractmethod
    def handle(self, event: E) -> None:
        """
        Process *event*.

        Args:
            event: The domain event to handle.

        Raises:
            Exception: Handlers should raise on unrecoverable failures so the
                dispatcher can decide on retry or dead-letter behaviour.
        """


class EventDispatcher(abc.ABC):
    """
    Abstract event dispatcher — the central hub for event routing.

    Responsibilities:
    - Maintain a registry of event type → list of handlers.
    - Route published events to all registered handlers.
    - Provide error isolation so one failing handler does not block others.
    """

    @abc.abstractmethod
    def register(
        self,
        event_type: type[BaseDomainEvent],
        handler: EventHandler[BaseDomainEvent],
    ) -> None:
        """
        Register *handler* to receive events of *event_type*.

        Args:
            event_type: The event class to subscribe to.
            handler: The handler instance to invoke.
        """

    @abc.abstractmethod
    def dispatch(self, event: BaseDomainEvent) -> None:
        """
        Dispatch *event* to all registered handlers.

        Args:
            event: The domain event to deliver.
        """

    @abc.abstractmethod
    def clear(self) -> None:
        """Remove all registered handlers (primarily for testing isolation)."""


class InProcessEventDispatcher(EventDispatcher):
    """
    Synchronous in-process event dispatcher.

    Events are dispatched immediately in the caller's thread.  Handler
    exceptions are logged and isolated — a failing handler does not prevent
    subsequent handlers from being invoked.

    This implementation is suitable for development, test environments, and
    early production.  Replace or extend with a Celery or Kafka-backed
    implementation when cross-process event propagation is required.
    """

    def __init__(self) -> None:
        self._registry: dict[type[BaseDomainEvent], list[EventHandler[BaseDomainEvent]]] = {}

    def register(
        self,
        event_type: type[BaseDomainEvent],
        handler: EventHandler[BaseDomainEvent],
    ) -> None:
        if event_type not in self._registry:
            self._registry[event_type] = []
        self._registry[event_type].append(handler)
        logger.debug(
            "event_handler_registered",
            extra={
                "event_type": event_type.__name__,
                "handler": type(handler).__name__,
            },
        )

    def dispatch(self, event: BaseDomainEvent) -> None:
        handlers = self._registry.get(type(event), [])
        logger.debug(
            "event_dispatching",
            extra={
                "event_type": type(event).__name__,
                "event_id": str(event.event_id),
                "handler_count": len(handlers),
            },
        )
        for handler in handlers:
            try:
                handler.handle(event)
            except Exception:
                logger.exception(
                    "event_handler_failed",
                    extra={
                        "event_type": type(event).__name__,
                        "event_id": str(event.event_id),
                        "handler": type(handler).__name__,
                    },
                )

    def clear(self) -> None:
        self._registry.clear()

    def handler_count(self, event_type: type[BaseDomainEvent]) -> int:
        """Return the number of handlers registered for *event_type*."""
        return len(self._registry.get(event_type, []))


__all__ = [
    "EventHandler",
    "EventDispatcher",
    "InProcessEventDispatcher",
]
