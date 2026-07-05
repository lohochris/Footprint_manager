import uuid
from typing import List
from ..models.event import StreamEvent
from ..selectors import StreamEventSelector

class ReplayEngine:
    @staticmethod
    def replay_events(tenant_id: uuid.UUID, channel_id: uuid.UUID, last_sequence_number: int) -> List[StreamEvent]:
        """
        Retrieves ordered events that occurred after the given sequence number.
        This enables robust recovery for clients that temporarily disconnect.
        """
        events = StreamEventSelector.get_events_since(tenant_id, channel_id, last_sequence_number)
        return list(events)
