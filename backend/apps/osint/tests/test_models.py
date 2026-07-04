# backend/apps/osint/tests/test_models.py
"""Model-level unit tests for DiscoveryProvider, DiscoveryJob, DiscoveryResult.

Uses function-based test style (matching the project's established convention)
with @pytest.mark.django_db for ORM-touching tests.
"""

import uuid
from decimal import Decimal

import pytest

from backend.apps.osint.enums import (
    DiscoveryJobStatus,
    DiscoveryJobTrigger,
    DiscoveryProviderStatus,
    DiscoveryResultType,
)


# ---------------------------------------------------------------------------
# Enum helpers (no DB required)
# ---------------------------------------------------------------------------

def test_terminal_states_contains_expected_values():
    terminals = DiscoveryJobStatus.terminal_states()
    assert DiscoveryJobStatus.COMPLETED in terminals
    assert DiscoveryJobStatus.FAILED in terminals
    assert DiscoveryJobStatus.CANCELLED in terminals


def test_non_terminal_states_not_in_terminal_set():
    terminals = DiscoveryJobStatus.terminal_states()
    assert DiscoveryJobStatus.PENDING not in terminals
    assert DiscoveryJobStatus.RUNNING not in terminals
    assert DiscoveryJobStatus.QUEUED not in terminals


def test_all_statuses_have_labels():
    for value, label in DiscoveryJobStatus.choices:
        assert label, f"DiscoveryJobStatus.{value} has no label"


def test_all_provider_statuses_present():
    values = {c[0] for c in DiscoveryProviderStatus.choices}
    assert "active" in values
    assert "inactive" in values
    assert "degraded" in values
    assert "deprecated" in values


def test_six_result_types():
    """Result type set must be stable — changes require a migration."""
    values = {c[0] for c in DiscoveryResultType.choices}
    expected = {"profile", "relationship", "asset", "indicator", "document", "raw"}
    assert values == expected


# ---------------------------------------------------------------------------
# DiscoveryProvider model tests (DB required)
# ---------------------------------------------------------------------------

def _make_provider(**kwargs):
    from backend.apps.osint.models import DiscoveryProvider

    defaults = {
        "name": f"test-provider-{uuid.uuid4().hex[:8]}",
        "display_name": "Test Provider",
        "version": "2.1.0",
        "description": "Sprint 6 test provider",
        "priority": 10,
        "timeout_seconds": 45,
        "max_retries": 2,
        "capabilities": ["email_lookup", "person_lookup"],
    }
    defaults.update(kwargs)
    return DiscoveryProvider.objects.create(**defaults)


@pytest.mark.django_db
def test_create_provider_with_full_fields():
    provider = _make_provider()
    assert provider.pk is not None
    assert provider.version == "2.1.0"
    assert provider.priority == 10
    assert provider.timeout_seconds == 45
    assert provider.max_retries == 2


@pytest.mark.django_db
def test_default_provider_status_is_active():
    provider = _make_provider()
    assert provider.provider_status == DiscoveryProviderStatus.ACTIVE


@pytest.mark.django_db
def test_is_selectable_true_when_active():
    provider = _make_provider(
        is_active=True,
        provider_status=DiscoveryProviderStatus.ACTIVE,
    )
    assert provider.is_selectable() is True


@pytest.mark.django_db
def test_is_selectable_false_when_inactive():
    provider = _make_provider(is_active=False)
    assert provider.is_selectable() is False


@pytest.mark.django_db
def test_is_selectable_false_when_deprecated():
    provider = _make_provider(
        provider_status=DiscoveryProviderStatus.DEPRECATED
    )
    assert provider.is_selectable() is False


@pytest.mark.django_db
def test_supports_capability_true():
    provider = _make_provider()
    assert provider.supports_capability("email_lookup") is True


@pytest.mark.django_db
def test_supports_capability_false():
    provider = _make_provider()
    assert provider.supports_capability("unknown_cap") is False


@pytest.mark.django_db
def test_provider_str_includes_name_and_version():
    provider = _make_provider(name="clearbit", version="3.0.0")
    assert "clearbit" in str(provider)
    assert "3.0.0" in str(provider)


# ---------------------------------------------------------------------------
# DiscoveryJob model tests (DB required)
# ---------------------------------------------------------------------------

def _make_job_provider():
    from backend.apps.osint.models import DiscoveryProvider

    return DiscoveryProvider.objects.create(
        name=f"job-test-provider-{uuid.uuid4().hex[:6]}",
        display_name="Job Test Provider",
    )


def _make_job(provider=None, **kwargs):
    from backend.apps.osint.models import DiscoveryJob

    if provider is None:
        provider = _make_job_provider()
    defaults = {
        "provider": provider,
        "status": DiscoveryJobStatus.PENDING,
        "triggered_by": DiscoveryJobTrigger.MANUAL,
        "capabilities_requested": ["email_lookup"],
        "input_data": {"email": "test@example.com"},
    }
    defaults.update(kwargs)
    return DiscoveryJob.objects.create(**defaults)


@pytest.mark.django_db
def test_create_job():
    job = _make_job()
    assert job.pk is not None
    assert job.status == DiscoveryJobStatus.PENDING


@pytest.mark.django_db
def test_is_terminal_false_for_pending():
    job = _make_job(status=DiscoveryJobStatus.PENDING)
    assert job.is_terminal is False


@pytest.mark.django_db
def test_is_terminal_true_for_completed():
    job = _make_job(status=DiscoveryJobStatus.COMPLETED)
    assert job.is_terminal is True


@pytest.mark.django_db
def test_is_terminal_true_for_failed():
    job = _make_job(status=DiscoveryJobStatus.FAILED)
    assert job.is_terminal is True


@pytest.mark.django_db
def test_is_terminal_true_for_cancelled():
    job = _make_job(status=DiscoveryJobStatus.CANCELLED)
    assert job.is_terminal is True


@pytest.mark.django_db
def test_execution_metadata_nullable_on_create():
    job = _make_job()
    assert job.started_at is None
    assert job.completed_at is None
    assert job.duration_ms is None
    assert job.failure_reason == ""
    assert job.retry_count == 0


@pytest.mark.django_db
def test_triggered_by_field():
    job = _make_job(triggered_by=DiscoveryJobTrigger.SCHEDULED)
    assert job.triggered_by == DiscoveryJobTrigger.SCHEDULED


# ---------------------------------------------------------------------------
# DiscoveryResult model tests (DB required)
# ---------------------------------------------------------------------------

def _make_result_provider():
    from backend.apps.osint.models import DiscoveryProvider

    return DiscoveryProvider.objects.create(
        name=f"result-test-prov-{uuid.uuid4().hex[:6]}",
        display_name="Result Test Provider",
    )


def _make_result_job(provider):
    from backend.apps.osint.models import DiscoveryJob

    return DiscoveryJob.objects.create(
        provider=provider,
        status=DiscoveryJobStatus.COMPLETED,
        triggered_by=DiscoveryJobTrigger.MANUAL,
        input_data={},
    )


def _make_result(job, provider, **kwargs):
    from backend.apps.osint.models import DiscoveryResult

    defaults = {
        "job": job,
        "provider": provider,
        "result_type": DiscoveryResultType.PROFILE,
        "title": "Jane Doe",
        "confidence": Decimal("0.9500"),
        "raw_data": {"name": "Jane Doe"},
        "normalised_data": {"title": "Jane Doe"},
    }
    defaults.update(kwargs)
    return DiscoveryResult.objects.create(**defaults)


@pytest.mark.django_db
def test_create_result():
    provider = _make_result_provider()
    job = _make_result_job(provider)
    result = _make_result(job, provider)
    assert result.pk is not None
    assert result.confidence == Decimal("0.9500")


@pytest.mark.django_db
def test_confidence_is_decimal_not_float():
    """Regression: confidence must be Decimal, not float."""
    provider = _make_result_provider()
    job = _make_result_job(provider)
    result = _make_result(job, provider, confidence=Decimal("0.7500"))
    assert isinstance(result.confidence, Decimal)


@pytest.mark.django_db
def test_storage_key_defaults_to_empty():
    provider = _make_result_provider()
    job = _make_result_job(provider)
    result = _make_result(job, provider)
    assert result.storage_key == ""


@pytest.mark.django_db
def test_evidence_id_is_uuid_not_fk():
    """evidence_id must be a UUIDField, not a ForeignKey."""
    from django.db import models as dj_models
    from backend.apps.osint.models import DiscoveryResult

    field = DiscoveryResult._meta.get_field("evidence_id")
    assert isinstance(field, dj_models.UUIDField), (
        "evidence_id must be a UUIDField, not a ForeignKey"
    )


@pytest.mark.django_db
def test_provider_fk_allows_null():
    """provider FK must be nullable (SET_NULL on provider deletion)."""
    from django.db import models as dj_models
    from backend.apps.osint.models import DiscoveryResult

    field = DiscoveryResult._meta.get_field("provider")
    assert field.null is True


@pytest.mark.django_db
def test_result_str_representation():
    provider = _make_result_provider()
    job = _make_result_job(provider)
    result = _make_result(job, provider, title="Alice Smith")
    assert "Alice Smith" in str(result)
    assert "profile" in str(result)
