"""
Apache Kafka message broker integration interface for Footprint Manager.

Defines the ``MessageBroker`` abstract interface for event streaming and
asynchronous message passing between services.  Concrete Kafka implementation
will be provided when the event streaming feature flag is enabled.
"""

from __future__ import annotations

import abc
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BrokerMessage:
    """
    A message to be published to a broker topic.

    Attributes:
        topic: Target topic name.
        key: Optional partition key for message routing.
        value: Message payload (must be JSON-serialisable).
        headers: Optional key-value headers attached to the message.
        partition: Optional explicit partition number.
    """

    topic: str
    value: Any
    key: str | None = None
    headers: dict[str, str] = field(default_factory=dict)
    partition: int | None = None


@dataclass(frozen=True)
class ConsumedMessage:
    """A message received from a broker topic."""

    topic: str
    partition: int
    offset: int
    key: str | None
    value: Any
    headers: dict[str, str]


MessageHandler = Callable[[ConsumedMessage], None]
"""Type alias for message consumer handler functions."""


class MessageBroker(abc.ABC):
    """Abstract message broker interface."""

    @abc.abstractmethod
    def publish(self, message: BrokerMessage) -> None:
        """
        Publish *message* to its configured topic.

        Args:
            message: The message to publish.
        """

    @abc.abstractmethod
    def subscribe(
        self,
        topics: list[str],
        handler: MessageHandler,
        *,
        group_id: str,
    ) -> None:
        """
        Subscribe to *topics* and invoke *handler* for each received message.

        Args:
            topics: List of topic names to subscribe to.
            handler: Callable invoked with each consumed message.
            group_id: Consumer group identifier for offset management.
        """

    @abc.abstractmethod
    def health_check(self) -> bool:
        """Return True if the broker is reachable."""

    @abc.abstractmethod
    def close(self) -> None:
        """Release producer and consumer resources."""


__all__ = [
    "BrokerMessage",
    "ConsumedMessage",
    "MessageHandler",
    "MessageBroker",
]
