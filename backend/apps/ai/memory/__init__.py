"""
Conversation memory interface for Footprint Manager AI module.

Provides the ``ConversationMemory`` abstract interface for maintaining
multi-turn conversation state.  Implementations may use in-memory storage,
Redis, or a database backend depending on the deployment environment.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class ConversationTurn:
    """
    A single exchange in a conversation.

    Attributes:
        role: Speaker role — ``"user"`` or ``"assistant"``.
        content: Text content of the turn.
        timestamp: UTC time when this turn was recorded.
        metadata: Optional structured metadata (tool calls, token counts, etc.).
    """

    role: str
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
    metadata: dict = field(default_factory=dict)


class ConversationMemory(abc.ABC):
    """
    Abstract conversation memory interface.

    Each conversation is identified by a ``session_id``.  Implementations
    must be safe for concurrent access within a single session.
    """

    @abc.abstractmethod
    def add_turn(self, session_id: str, turn: ConversationTurn) -> None:
        """
        Append *turn* to the conversation identified by *session_id*.

        Args:
            session_id: Unique conversation session identifier.
            turn: The conversation turn to add.
        """

    @abc.abstractmethod
    def get_history(
        self,
        session_id: str,
        *,
        limit: int | None = None,
    ) -> list[ConversationTurn]:
        """
        Retrieve the conversation history for *session_id*.

        Args:
            session_id: Unique conversation session identifier.
            limit: Maximum number of recent turns to return (None = all).

        Returns:
            Ordered list of conversation turns (oldest first).
        """

    @abc.abstractmethod
    def clear(self, session_id: str) -> None:
        """
        Clear all turns for *session_id*.

        Args:
            session_id: Unique conversation session identifier.
        """

    @abc.abstractmethod
    def session_exists(self, session_id: str) -> bool:
        """Return True if a session with *session_id* has any stored turns."""

    def to_messages(self, session_id: str, *, limit: int | None = None) -> list[dict]:
        """
        Return the conversation history as a list of message dicts compatible
        with the OpenAI / Anthropic message format.

        Args:
            session_id: Unique conversation session identifier.
            limit: Maximum number of recent turns.

        Returns:
            List of ``{"role": ..., "content": ...}`` dicts.
        """
        return [
            {"role": turn.role, "content": turn.content}
            for turn in self.get_history(session_id, limit=limit)
        ]


__all__ = [
    "ConversationTurn",
    "ConversationMemory",
]
