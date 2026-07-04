# backend/apps/osint/tests/test_selectors.py
"""Tests for OSINT read-only selectors.

Uses @pytest.mark.django_db on function-based tests (project convention).
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
from backend.apps.osint.models import DiscoveryJob, DiscoveryProvider, DiscoveryResult
from backend.apps.osint.selectors import (
    get_active_providers,
    get_high_confidence_results,
    get_jobs_by_status,
    get_jobs_for_investigation,
    get_pending_jobs,
    get_provider_by_name,
    get_providers_by_capability,
    get_results_for_job,
    get_unverified_results,
)


def _make_provider(name=None, **kwargs):
    defaults = {
        "name": name or f"sel-prov-{uuid.uuid4().hex[:6]}",
        "display_name": "Selector Test Provider",
        "capabilities": ["email_lookup"],
    }
    defaults.update(kwargs)
    return DiscoveryProvider.objects.create(**defaults)


def _make_job(provider, status=DiscoveryJobStatus.PENDING):
    return DiscoveryJob.objects.create(
        provider=provider,
        status=status,
        triggered_by=DiscoveryJobTrigger.MANUAL,
        input_data={},
    )


def _make_result(job, provider, confidence="0.9000", result_type=DiscoveryResultType.PROFILE):
    return DiscoveryResult.objects.create(
        job=job,
        provider=provider,
        result_type=result_type,
        title="Test Finding",
        confidence=Decimal(confidence),
        raw_data={},
        normalised_data={},
    )


# ---------------------------------------------------------------------------
# DiscoveryProvider selectors
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_active_providers_excludes_inactive():
    active = _make_provider(is_active=True, provider_status=DiscoveryProviderStatus.ACTIVE)
    inactive = _make_provider(is_active=False)
    names = list(get_active_providers().values_list("name", flat=True))
    assert active.name in names
    assert inactive.name not in names


@pytest.mark.django_db
def test_get_providers_by_capability_filters_correctly():
    p1 = _make_provider(capabilities=["email_lookup", "person_lookup"])
    p2 = _make_provider(capabilities=["domain_lookup"])
    email_providers = list(
        get_providers_by_capability("email_lookup").values_list("name", flat=True)
    )
    assert p1.name in email_providers
    assert p2.name not in email_providers


@pytest.mark.django_db
def test_get_provider_by_name_returns_provider():
    p = _make_provider(name="my-unique-selector-provider")
    found = get_provider_by_name("my-unique-selector-provider")
    assert found.pk == p.pk


@pytest.mark.django_db
def test_get_provider_by_name_raises_for_unknown():
    with pytest.raises(DiscoveryProvider.DoesNotExist):
        get_provider_by_name("completely-unknown-xyz")


# ---------------------------------------------------------------------------
# DiscoveryJob selectors
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_jobs_by_status_filters_correctly():
    provider = _make_provider()
    pending_job = _make_job(provider, status=DiscoveryJobStatus.PENDING)
    _make_job(provider, status=DiscoveryJobStatus.COMPLETED)
    results = get_jobs_by_status(DiscoveryJobStatus.PENDING)
    ids = list(results.values_list("id", flat=True))
    assert pending_job.pk in ids


@pytest.mark.django_db
def test_get_pending_jobs_returns_pending_and_queued():
    provider = _make_provider()
    pending = _make_job(provider, status=DiscoveryJobStatus.PENDING)
    queued = _make_job(provider, status=DiscoveryJobStatus.QUEUED)
    _make_job(provider, status=DiscoveryJobStatus.COMPLETED)
    ids = list(get_pending_jobs().values_list("id", flat=True))
    assert pending.pk in ids
    assert queued.pk in ids


@pytest.mark.django_db
def test_get_jobs_for_investigation_filters_by_investigation():
    provider = _make_provider()
    inv_id = uuid.uuid4()
    job_with_inv = DiscoveryJob.objects.create(
        provider=provider,
        status=DiscoveryJobStatus.PENDING,
        triggered_by=DiscoveryJobTrigger.MANUAL,
        input_data={},
        investigation_id=inv_id,
    )
    _make_job(provider)  # no investigation
    ids = list(get_jobs_for_investigation(str(inv_id)).values_list("id", flat=True))
    assert job_with_inv.pk in ids
    assert len(ids) == 1


# ---------------------------------------------------------------------------
# DiscoveryResult selectors
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_results_for_job():
    provider = _make_provider()
    job = _make_job(provider)
    r1 = _make_result(job, provider, confidence="0.8000")
    r2 = _make_result(job, provider, confidence="0.6000")
    ids = list(get_results_for_job(str(job.pk)).values_list("id", flat=True))
    assert r1.pk in ids
    assert r2.pk in ids


@pytest.mark.django_db
def test_get_high_confidence_results_filters_by_threshold():
    provider = _make_provider()
    job = _make_job(provider)
    high = _make_result(job, provider, confidence="0.9000")
    low = _make_result(job, provider, confidence="0.4000")
    ids = list(
        get_high_confidence_results(str(job.pk), threshold="0.7000")
        .values_list("id", flat=True)
    )
    assert high.pk in ids
    assert low.pk not in ids


@pytest.mark.django_db
def test_get_unverified_results():
    provider = _make_provider()
    job = _make_job(provider)
    unverified = _make_result(job, provider)
    verified = _make_result(job, provider)
    verified.is_verified = True
    verified.save(update_fields=["is_verified"])
    ids = list(get_unverified_results(str(job.pk)).values_list("id", flat=True))
    assert unverified.pk in ids
    assert verified.pk not in ids
