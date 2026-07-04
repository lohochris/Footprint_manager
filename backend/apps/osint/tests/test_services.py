# backend/apps/osint/tests/test_services.py
"""Integration tests for DiscoveryJobService.

Function-based test style (project convention) with @pytest.mark.django_db.
Uses NoOpDiscoveryProvider registered in the singleton registry.
"""

import uuid
from decimal import Decimal
from unittest.mock import patch

import pytest

from backend.apps.osint.dto import DiscoveryRequest
from backend.apps.osint.enums import DiscoveryJobStatus, DiscoveryJobTrigger
from backend.apps.osint.models import DiscoveryJob, DiscoveryProvider, DiscoveryResult
from backend.apps.osint.services import DiscoveryJobService


def _make_provider_record(**kwargs):
    """Create a DiscoveryProvider catalogue entry for the noop provider."""
    defaults = {
        "display_name": "No-Op Provider",
        "version": "1.0.0",
        "capabilities": ["person_lookup", "email_lookup"],
        "max_retries": 2,
    }
    defaults.update(kwargs)
    return DiscoveryProvider.objects.get_or_create(
        name=defaults.pop("name", "noop"),
        defaults=defaults,
    )[0]


def _make_request(**kwargs):
    defaults = {
        "provider_name": "noop",
        "capabilities": ["email_lookup"],
        "input_data": {"email": "test@example.com"},
        "triggered_by": DiscoveryJobTrigger.MANUAL,
    }
    defaults.update(kwargs)
    return DiscoveryRequest(**defaults)


def _make_job(provider=None, status=DiscoveryJobStatus.PENDING, **kwargs):
    if provider is None:
        provider = _make_provider_record()
    defaults = {
        "provider": provider,
        "status": status,
        "triggered_by": DiscoveryJobTrigger.MANUAL,
        "input_data": {"email": "test@example.com"},
    }
    defaults.update(kwargs)
    return DiscoveryJob.objects.create(**defaults)


# ---------------------------------------------------------------------------
# create_job tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_create_job_persists_record(django_user_model):
    _make_provider_record()
    user = django_user_model.objects.create_user(
        username="testuser_create", password="Password1234!"
    )
    service = DiscoveryJobService()
    job = service.create_job(_make_request(), user)
    assert isinstance(job, DiscoveryJob)
    assert job.pk is not None
    assert job.status == DiscoveryJobStatus.PENDING


@pytest.mark.django_db
def test_create_job_with_invalid_provider_raises(django_user_model):
    user = django_user_model.objects.create_user(
        username="testuser_invalid", password="Password1234!"
    )
    service = DiscoveryJobService()
    with pytest.raises(DiscoveryProvider.DoesNotExist):
        service.create_job(
            _make_request(provider_name="nonexistent_xyz"),
            user,
        )


@pytest.mark.django_db
def test_create_job_with_inactive_provider_raises(django_user_model):
    DiscoveryProvider.objects.get_or_create(
        name="noop-inactive",
        defaults={
            "display_name": "Inactive",
            "is_active": False,
        },
    )
    user = django_user_model.objects.create_user(
        username="testuser_inactive", password="Password1234!"
    )
    service = DiscoveryJobService()
    with pytest.raises(ValueError, match="not selectable"):
        service.create_job(
            _make_request(provider_name="noop-inactive"),
            user,
        )


# ---------------------------------------------------------------------------
# run tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_run_happy_path_completes_job():
    provider = _make_provider_record()
    job = _make_job(provider)
    service = DiscoveryJobService()
    results = service.run(job)
    job.refresh_from_db()
    assert job.status == DiscoveryJobStatus.COMPLETED
    assert job.started_at is not None
    assert job.completed_at is not None
    assert job.duration_ms is not None
    assert job.duration_ms >= 0
    assert len(results) == 1


@pytest.mark.django_db
def test_run_persists_discovery_results():
    provider = _make_provider_record()
    job = _make_job(provider)
    service = DiscoveryJobService()
    results = service.run(job)
    assert DiscoveryResult.objects.filter(job=job).count() == 1
    result = results[0]
    assert isinstance(result.confidence, Decimal)


@pytest.mark.django_db
def test_run_result_provider_fk_matches_job_provider():
    provider = _make_provider_record()
    job = _make_job(provider)
    service = DiscoveryJobService()
    results = service.run(job)
    assert results[0].provider_id == provider.pk


@pytest.mark.django_db
def test_run_on_terminal_job_raises():
    provider = _make_provider_record()
    job = _make_job(provider, status=DiscoveryJobStatus.COMPLETED)
    service = DiscoveryJobService()
    with pytest.raises(ValueError, match="terminal state"):
        service.run(job)


@pytest.mark.django_db
def test_run_unhealthy_provider_fails_job():
    """When health_check returns unhealthy, job must transition to FAILED."""
    from backend.apps.osint.providers.noop_provider import NoOpDiscoveryProvider

    provider = _make_provider_record()
    job = _make_job(provider)

    unhealthy_provider = NoOpDiscoveryProvider(healthy=False)

    service = DiscoveryJobService()
    with patch(
        "backend.apps.osint.services.discovery_job_service.get_provider",
        return_value=lambda: unhealthy_provider,
    ):
        results = service.run(job)

    job.refresh_from_db()
    assert job.status == DiscoveryJobStatus.FAILED
    assert job.failure_reason != ""
    assert results == []


@pytest.mark.django_db
def test_run_records_health_snapshot_on_provider_record():
    provider = _make_provider_record()
    job = _make_job(provider)
    service = DiscoveryJobService()
    service.run(job)
    provider.refresh_from_db()
    assert provider.last_health_status is True
    assert provider.last_health_check_at is not None


# ---------------------------------------------------------------------------
# cancel tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_cancel_pending_job(django_user_model):
    user = django_user_model.objects.create_user(
        username="cancel_user", password="Password1234!"
    )
    provider = _make_provider_record()
    job = _make_job(provider)
    service = DiscoveryJobService()
    cancelled = service.cancel(job, user)
    assert cancelled.status == DiscoveryJobStatus.CANCELLED


@pytest.mark.django_db
def test_cancel_terminal_job_raises(django_user_model):
    user = django_user_model.objects.create_user(
        username="cancel_user2", password="Password1234!"
    )
    provider = _make_provider_record()
    job = _make_job(provider, status=DiscoveryJobStatus.COMPLETED)
    service = DiscoveryJobService()
    with pytest.raises(ValueError, match="terminal state"):
        service.cancel(job, user)


# ---------------------------------------------------------------------------
# retry tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_retry_resets_to_pending(django_user_model):
    user = django_user_model.objects.create_user(
        username="retry_user", password="Password1234!"
    )
    provider = _make_provider_record()
    job = _make_job(provider, status=DiscoveryJobStatus.FAILED, failure_reason="Timeout", retry_count=0)
    service = DiscoveryJobService()
    retried = service.retry(job, user)
    assert retried.status == DiscoveryJobStatus.PENDING
    assert retried.retry_count == 1


@pytest.mark.django_db
def test_retry_non_failed_job_raises(django_user_model):
    user = django_user_model.objects.create_user(
        username="retry_user2", password="Password1234!"
    )
    provider = _make_provider_record()
    job = _make_job(provider, status=DiscoveryJobStatus.PENDING)
    service = DiscoveryJobService()
    with pytest.raises(ValueError, match="FAILED"):
        service.retry(job, user)


@pytest.mark.django_db
def test_retry_beyond_max_raises(django_user_model):
    user = django_user_model.objects.create_user(
        username="retry_user3", password="Password1234!"
    )
    provider = _make_provider_record()
    # max_retries is 2; retry_count=2 means limit already reached
    job = _make_job(
        provider,
        status=DiscoveryJobStatus.FAILED,
        failure_reason="Timeout",
        retry_count=2,
    )
    service = DiscoveryJobService()
    with pytest.raises(ValueError, match="maximum retry limit"):
        service.retry(job, user)
