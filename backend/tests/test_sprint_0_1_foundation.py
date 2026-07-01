"""Sprint 0.1 architecture foundation tests."""

from dataclasses import dataclass

from django.conf import settings
from shared.cache import CacheBackend
from shared.constants import ENABLE_AI, FEATURE_FLAG_NAMES, get_feature_flags, is_feature_enabled
from shared.event_bus import EventHandler, InProcessEventDispatcher
from shared.events import BaseDomainEvent
from shared.search import SearchBackend
from shared.storage import StorageBackend


@dataclass(frozen=True)
class SampleEvent(BaseDomainEvent):
    """Event used to verify dispatcher contracts."""

    event_type = "tests.sample.event"


class RecordingHandler(EventHandler[SampleEvent]):
    """Event handler that records delivered events."""

    def __init__(self) -> None:
        self.events: list[SampleEvent] = []

    def handle(self, event: SampleEvent) -> None:
        self.events.append(event)


def test_feature_flags_are_configured_and_disabled_by_default():
    flags = get_feature_flags()

    assert set(settings.FEATURE_FLAGS) == FEATURE_FLAG_NAMES
    assert flags[ENABLE_AI] is False
    assert all(value is False for value in flags.values())
    assert is_feature_enabled(ENABLE_AI) is False


def test_event_dispatcher_delivers_registered_domain_events():
    dispatcher = InProcessEventDispatcher()
    handler = RecordingHandler()
    event = SampleEvent()

    dispatcher.register(SampleEvent, handler)
    dispatcher.dispatch(event)

    assert handler.events == [event]
    assert dispatcher.handler_count(SampleEvent) == 1


def test_shared_interfaces_remain_abstract():
    assert CacheBackend.__abstractmethods__
    assert SearchBackend.__abstractmethods__
    assert StorageBackend.__abstractmethods__
