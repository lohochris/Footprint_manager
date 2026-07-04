# backend/apps/osint/selectors/discovery_selectors.py
"""Read-only query helpers for the OSINT Discovery domain.

Selectors follow the Django service-layer pattern established in the
investigations and evidence domains: they encapsulate all ORM query logic
so that viewsets, serializers, and services import a named function rather
than constructing ``QuerySet`` chains inline.

All functions return unevaluated ``QuerySet`` objects so callers can
apply additional filters, pagination, and prefetch strategies.
"""

from __future__ import annotations

from django.db import connection
import uuid
from typing import Union
from django.db.models import QuerySet

from backend.apps.osint.enums import DiscoveryJobStatus, DiscoveryProviderStatus
from backend.apps.osint.models import DiscoveryJob, DiscoveryProvider, DiscoveryResult


# ---------------------------------------------------------------------------
# DiscoveryProvider selectors
# ---------------------------------------------------------------------------

def get_active_providers() -> QuerySet[DiscoveryProvider]:
    """Return all selectable DiscoveryProvider records ordered by priority.

    A provider is selectable when ``is_active=True`` and
    ``provider_status=ACTIVE``.
    """
    return DiscoveryProvider.objects.filter(
        is_active=True,
        provider_status=DiscoveryProviderStatus.ACTIVE,
    ).order_by("priority", "name")


def get_providers_by_capability(capability: str) -> QuerySet[DiscoveryProvider]:
    """Return active providers whose ``capabilities`` JSON list contains *capability*.

    Uses the database JSON containment lookup when available. SQLite does
    not support JSON ``contains``, so tests and local development fall back
    to an ID subquery built from the active provider set.

    Parameters
    ----------
    capability:
        A ``DiscoveryCapability`` value string (e.g. ``"email_lookup"``).
    """
    providers = get_active_providers()
    if connection.features.supports_json_field_contains:
        return providers.filter(capabilities__contains=[capability])

    provider_ids = [
        provider.pk
        for provider in providers.only("id", "capabilities")
        if capability in (provider.capabilities or [])
    ]
    return get_active_providers().filter(pk__in=provider_ids)


def get_provider_by_name(name: str) -> DiscoveryProvider:
    """Return the DiscoveryProvider with the given *name*.

    Raises
    ------
    DiscoveryProvider.DoesNotExist:
        If no provider with *name* exists.
    """
    return DiscoveryProvider.objects.get(name=name)


# ---------------------------------------------------------------------------
# DiscoveryJob selectors
# ---------------------------------------------------------------------------

def get_jobs_for_investigation(investigation_id: str) -> QuerySet[DiscoveryJob]:
    """Return all DiscoveryJobs linked to the given investigation UUID string.

    Ordered by most recent creation date first.

    Parameters
    ----------
    investigation_id:
        UUID string of the parent ``Investigation``.
    """
    return (
        DiscoveryJob.objects
        .filter(investigation_id=investigation_id, is_deleted=False)
        .select_related("provider")
        .order_by("-created_at")
    )


def get_jobs_by_status(status: str) -> QuerySet[DiscoveryJob]:
    """Return all non-deleted DiscoveryJobs in the given *status*.

    Parameters
    ----------
    status:
        A ``DiscoveryJobStatus`` value string.
    """
    return (
        DiscoveryJob.objects
        .filter(status=status, is_deleted=False)
        .select_related("provider", "investigation", "target")
        .order_by("-created_at")
    )


def get_pending_jobs() -> QuerySet[DiscoveryJob]:
    """Return all jobs in PENDING or QUEUED status, oldest first."""
    return (
        DiscoveryJob.objects
        .filter(
            status__in=[DiscoveryJobStatus.PENDING, DiscoveryJobStatus.QUEUED],
            is_deleted=False,
        )
        .select_related("provider")
        .order_by("created_at")
    )


# ---------------------------------------------------------------------------
# DiscoveryResult selectors
# ---------------------------------------------------------------------------

def get_results_for_job(job_id: uuid.UUID | str) -> QuerySet[DiscoveryResult]:
    """Return all DiscoveryResults for the given job UUID string.

    Ordered by descending confidence, then creation date.

    Parameters
    ----------
    job_id:
        UUID string of the parent ``DiscoveryJob``.
    """
    if isinstance(job_id, str):
        job_id = uuid.UUID(job_id)
    return (
        DiscoveryResult.objects
        .filter(job_id=job_id, is_deleted=False)
        .select_related("provider")
        .order_by("-confidence", "-created_at")
    )


def get_results_for_investigation(
    investigation_id: str,
) -> QuerySet[DiscoveryResult]:
    """Return all DiscoveryResults for jobs linked to the given investigation.

    Parameters
    ----------
    investigation_id:
        UUID string of the parent ``Investigation``.
    """
    return (
        DiscoveryResult.objects
        .filter(
            job__investigation_id=investigation_id,
            is_deleted=False,
        )
        .select_related("job", "provider")
        .order_by("-confidence", "-created_at")
    )


def get_high_confidence_results(
    job_id: uuid.UUID | str,
    threshold: str = "0.7000",
) -> QuerySet[DiscoveryResult]:
    """Return results above the given *threshold* confidence for *job_id*.

    Parameters
    ----------
    job_id:
        UUID string of the parent ``DiscoveryJob``.
    threshold:
        Minimum confidence as a string (default ``"0.7000"``).
        Passed to ``Decimal`` comparison for precision safety.
    """
    from decimal import Decimal

    if isinstance(job_id, str):
        job_id = uuid.UUID(job_id)
    return (
        DiscoveryResult.objects
        .filter(
            job_id=job_id,
            confidence__gte=Decimal(threshold),
            is_deleted=False,
        )
        .select_related("provider")
        .order_by("-confidence")
    )


def get_unverified_results(job_id: uuid.UUID | str) -> QuerySet[DiscoveryResult]:
    """Return results that have not yet been analyst-verified for *job_id*."""
    if isinstance(job_id, str):
        job_id = uuid.UUID(job_id)
    return (
        DiscoveryResult.objects
        .filter(job_id=job_id, is_verified=False, is_deleted=False)
        .order_by("-confidence")
    )
