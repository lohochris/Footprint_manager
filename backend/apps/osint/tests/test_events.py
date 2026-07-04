# backend/apps/osint/tests/test_events.py
"""Unit tests for OSINT domain events.

Verifies that all five domain events:
  1. Can be instantiated with sensible defaults.
  2. Extend BaseDomainEvent and have unique event_type strings.
  3. Serialise to dict via to_dict() with the expected keys.
  4. Are immutable (frozen dataclasses).
"""

import uuid
from datetime import datetime, UTC
from decimal import Decimal

import pytest

from backend.apps.osint.events import (
    DiscoveryJobCompleted,
    DiscoveryJobFailed,
    DiscoveryJobQueued,
    DiscoveryJobStarted,
    DiscoveryResultCreated,
)
from backend.shared.events import BaseDomainEvent


class TestDiscoveryJobQueued:
    def test_inherits_base_domain_event(self):
        event = DiscoveryJobQueued(
            job_id=uuid.uuid4(),
            provider_name="noop",
            triggered_by="manual",
        )
        assert isinstance(event, BaseDomainEvent)

    def test_event_type_string(self):
        assert DiscoveryJobQueued.event_type == "osint.discovery_job.queued"

    def test_to_dict_contains_required_keys(self):
        job_id = uuid.uuid4()
        event = DiscoveryJobQueued(
            job_id=job_id,
            provider_name="noop",
            triggered_by="manual",
        )
        d = event.to_dict()
        assert d["event_type"] == "osint.discovery_job.queued"
        assert d["job_id"] == str(job_id)
        assert d["provider_name"] == "noop"
        assert d["triggered_by"] == "manual"
        assert "event_id" in d
        assert "occurred_at" in d

    def test_is_immutable(self):
        event = DiscoveryJobQueued(job_id=uuid.uuid4(), provider_name="x", triggered_by="api")
        with pytest.raises((AttributeError, TypeError)):
            event.provider_name = "mutated"  # type: ignore[misc]


class TestDiscoveryJobStarted:
    def test_event_type_string(self):
        assert DiscoveryJobStarted.event_type == "osint.discovery_job.started"

    def test_to_dict_contains_started_at(self):
        now = datetime.now(tz=UTC)
        event = DiscoveryJobStarted(job_id=uuid.uuid4(), started_at=now)
        d = event.to_dict()
        assert d["started_at"] == now.isoformat()


class TestDiscoveryJobCompleted:
    def test_event_type_string(self):
        assert DiscoveryJobCompleted.event_type == "osint.discovery_job.completed"

    def test_to_dict_contains_execution_metadata(self):
        now = datetime.now(tz=UTC)
        event = DiscoveryJobCompleted(
            job_id=uuid.uuid4(),
            completed_at=now,
            duration_ms=1234,
            result_count=5,
        )
        d = event.to_dict()
        assert d["duration_ms"] == 1234
        assert d["result_count"] == 5
        assert d["completed_at"] == now.isoformat()


class TestDiscoveryJobFailed:
    def test_event_type_string(self):
        assert DiscoveryJobFailed.event_type == "osint.discovery_job.failed"

    def test_to_dict_contains_failure_metadata(self):
        event = DiscoveryJobFailed(
            job_id=uuid.uuid4(),
            failure_reason="Provider timeout",
            retry_count=2,
        )
        d = event.to_dict()
        assert d["failure_reason"] == "Provider timeout"
        assert d["retry_count"] == 2


class TestDiscoveryResultCreated:
    def test_event_type_string(self):
        assert DiscoveryResultCreated.event_type == "osint.discovery_result.created"

    def test_to_dict_contains_result_fields(self):
        result_id = uuid.uuid4()
        job_id = uuid.uuid4()
        event = DiscoveryResultCreated(
            result_id=result_id,
            job_id=job_id,
            result_type="profile",
            confidence="0.9500",
        )
        d = event.to_dict()
        assert d["result_id"] == str(result_id)
        assert d["job_id"] == str(job_id)
        assert d["result_type"] == "profile"
        assert d["confidence"] == "0.9500"

    def test_confidence_is_string_not_decimal(self):
        """Confidence must be stored as str to survive JSON round-trip exactly."""
        event = DiscoveryResultCreated(
            result_id=uuid.uuid4(),
            job_id=uuid.uuid4(),
            result_type="raw",
            confidence="0.7500",
        )
        assert isinstance(event.confidence, str)


class TestAllEventsHaveUniqueEventTypes:
    def test_event_type_uniqueness(self):
        event_classes = [
            DiscoveryJobQueued,
            DiscoveryJobStarted,
            DiscoveryJobCompleted,
            DiscoveryJobFailed,
            DiscoveryResultCreated,
        ]
        types = [cls.event_type for cls in event_classes]
        assert len(types) == len(set(types)), "Duplicate event_type strings found"

    def test_all_event_types_are_namespaced(self):
        event_classes = [
            DiscoveryJobQueued,
            DiscoveryJobStarted,
            DiscoveryJobCompleted,
            DiscoveryJobFailed,
            DiscoveryResultCreated,
        ]
        for cls in event_classes:
            assert cls.event_type.startswith("osint."), (
                f"{cls.__name__}.event_type does not start with 'osint.'"
            )
