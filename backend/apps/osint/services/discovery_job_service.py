# backend/apps/osint/services/discovery_job_service.py
"""DiscoveryJobService — orchestrates OSINT provider execution.

Responsibilities
----------------
1. Create ``DiscoveryJob`` records from a ``DiscoveryRequest`` DTO.
2. Run a job synchronously against its assigned provider.
3. Manage the full job lifecycle: pending → running → completed / failed.
4. Persist ``DiscoveryResult`` rows from normalised provider output.
5. Emit domain events at each lifecycle transition.
6. Apply the provider's health-check before dispatching work.
7. Support cancellation and retry of existing jobs.

Sprint 6 note
-------------
``run()`` is synchronous.  It is designed to be called from a Celery task
(Sprint 7) by wrapping it in a task function with a feature-flag guard.
No async primitives or Celery imports appear in this service.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from backend.apps.osint.dto import DiscoveryRequest, DiscoveryResultDTO
from backend.apps.osint.enums import DiscoveryJobStatus, DiscoveryProviderStatus
from backend.apps.osint.events import (
    DiscoveryJobCompleted,
    DiscoveryJobFailed,
    DiscoveryJobQueued,
    DiscoveryJobStarted,
    DiscoveryResultCreated,
)
from backend.apps.osint.models import DiscoveryJob, DiscoveryProvider, DiscoveryResult
from backend.apps.osint.providers.registry import get_provider

logger = logging.getLogger(__name__)


class DiscoveryJobService:
    """Service that orchestrates OSINT discovery provider execution.

    All public methods operate inside ``django.db.transaction.atomic()``
    blocks to guarantee consistency between job state transitions and
    result persistence.
    """

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def create_job(
        self,
        request: DiscoveryRequest,
        user,
    ) -> DiscoveryJob:
        """Create and queue a new ``DiscoveryJob`` from a ``DiscoveryRequest``.

        Parameters
        ----------
        request:
            Validated ``DiscoveryRequest`` DTO from the caller.
        user:
            Authenticated user initiating the job (used for ``created_by``).

        Returns
        -------
        DiscoveryJob
            Persisted job in ``PENDING`` status.

        Raises
        ------
        DiscoveryProvider.DoesNotExist:
            If ``request.provider_name`` is not found in the catalogue.
        ValueError:
            If the provider is not selectable (inactive / deprecated).
        """
        provider_record = DiscoveryProvider.objects.get(
            name=request.provider_name
        )

        if not provider_record.is_selectable():
            raise ValueError(
                f"Provider '{request.provider_name}' is not selectable "
                f"(status={provider_record.provider_status}, "
                f"is_active={provider_record.is_active})."
            )

        with transaction.atomic():
            job = DiscoveryJob.objects.create(
                provider=provider_record,
                status=DiscoveryJobStatus.PENDING,
                triggered_by=request.triggered_by,
                capabilities_requested=request.capabilities,
                input_data=request.input_data,
                investigation_id=request.investigation_id,
                target_id=request.target_id,
                metadata=request.metadata,
                created_by=user,
            )

        self._emit(
            DiscoveryJobQueued(
                aggregate_id=job.id,
                aggregate_type="DiscoveryJob",
                job_id=job.id,
                provider_name=provider_record.name,
                triggered_by=request.triggered_by,
                metadata={"user_id": str(user.id) if user else None},
            )
        )

        logger.info(
            "DiscoveryJob created",
            extra={
                "job_id": str(job.id),
                "provider": provider_record.name,
                "triggered_by": request.triggered_by,
            },
        )
        return job

    def run(self, job: DiscoveryJob) -> list[DiscoveryResult]:
        """Execute a discovery job synchronously.

        Sequence
        --------
        1. Transition job → ``RUNNING``; record ``started_at``; emit
           ``DiscoveryJobStarted``.
        2. Resolve the ``BaseDiscoveryProvider`` implementation from the
           registry by ``job.provider.name``.
        3. Call ``provider.health_check()``; if unhealthy → fail job and
           emit ``DiscoveryJobFailed``.
        4. Call ``provider.validate_target(job.input_data)``.
        5. Call ``provider.discover(job.input_data)`` → ``list[dict]``.
        6. Normalise each raw result via ``provider.normalize(raw)``.
        7. Persist ``DiscoveryResult`` rows atomically.
        8. Transition job → ``COMPLETED``; compute ``duration_ms``; emit
           ``DiscoveryJobCompleted`` + ``DiscoveryResultCreated`` per result.
        9. On any exception → transition job → ``FAILED``; record
           ``failure_reason``; increment ``retry_count``; emit
           ``DiscoveryJobFailed``.

        Parameters
        ----------
        job:
            A ``DiscoveryJob`` in ``PENDING`` or ``QUEUED`` status.

        Returns
        -------
        list[DiscoveryResult]
            Persisted result rows (empty list on provider returning nothing).

        Raises
        ------
        ValueError:
            If the job is already in a terminal state.
        """
        if job.is_terminal:
            raise ValueError(
                f"Job {job.id} is already in terminal state '{job.status}'."
            )

        started_at = datetime.now(tz=UTC)
        self._transition(job, DiscoveryJobStatus.RUNNING, started_at=started_at)

        self._emit(
            DiscoveryJobStarted(
                aggregate_id=job.id,
                aggregate_type="DiscoveryJob",
                job_id=job.id,
                started_at=started_at,
            )
        )

        try:
            # Resolve behavioural provider from class registry
            provider_cls = get_provider(job.provider.name)
            if provider_cls is None:
                raise LookupError(
                    f"No BaseDiscoveryProvider registered for name "
                    f"'{job.provider.name}'."
                )

            provider = provider_cls()
            provider.initialize()

            # Health gate
            health = provider.health_check()
            self._record_health(job.provider, health)
            if not health.healthy:
                raise RuntimeError(
                    f"Provider '{job.provider.name}' failed health check: "
                    f"{health.message}"
                )

            # Validate input
            provider.validate_target(job.input_data)

            # Execute discovery
            raw_results: list[dict] = provider.discover(job.input_data)

            # Normalise and persist results
            result_objects: list[DiscoveryResult] = []
            with transaction.atomic():
                for raw in raw_results:
                    normalised = provider.normalize(raw)
                    dto = self._build_result_dto(normalised, raw)
                    db_result = DiscoveryResult.objects.create(
                        job=job,
                        provider=job.provider,
                        result_type=dto.result_type,
                        title=dto.title,
                        summary=dto.summary,
                        confidence=dto.confidence,
                        raw_data=dto.raw_data,
                        normalised_data=dto.normalised_data,
                        storage_key=dto.storage_key,
                        source_url=dto.source_url,
                        tags=dto.tags,
                        created_by_id=job.created_by_id,
                    )
                    result_objects.append(db_result)

            # Transition to completed
            completed_at = datetime.now(tz=UTC)
            duration_ms = int(
                (completed_at - started_at).total_seconds() * 1000
            )
            with transaction.atomic():
                job.status = DiscoveryJobStatus.COMPLETED
                job.completed_at = completed_at
                job.duration_ms = duration_ms
                job.save(
                    update_fields=[
                        "status",
                        "completed_at",
                        "duration_ms",
                        "updated_at",
                    ]
                )

            self._emit(
                DiscoveryJobCompleted(
                    aggregate_id=job.id,
                    aggregate_type="DiscoveryJob",
                    job_id=job.id,
                    completed_at=completed_at,
                    duration_ms=duration_ms,
                    result_count=len(result_objects),
                )
            )
            for result in result_objects:
                self._emit(
                    DiscoveryResultCreated(
                        aggregate_id=result.id,
                        aggregate_type="DiscoveryResult",
                        result_id=result.id,
                        job_id=job.id,
                        result_type=result.result_type,
                        confidence=str(result.confidence),
                    )
                )

            logger.info(
                "DiscoveryJob completed",
                extra={
                    "job_id": str(job.id),
                    "result_count": len(result_objects),
                    "duration_ms": duration_ms,
                },
            )
            return result_objects

        except Exception as exc:
            return self._fail_job(job, exc)

    def cancel(self, job: DiscoveryJob, user) -> DiscoveryJob:
        """Cancel a job that has not yet reached a terminal state.

        Parameters
        ----------
        job:
            Job to cancel.
        user:
            Analyst requesting cancellation (recorded via ``updated_by``).

        Returns
        -------
        DiscoveryJob
            The updated job with ``status = CANCELLED``.

        Raises
        ------
        ValueError:
            If the job is already in a terminal state.
        """
        if job.is_terminal:
            raise ValueError(
                f"Job {job.id} is already in terminal state '{job.status}' "
                f"and cannot be cancelled."
            )
        with transaction.atomic():
            job.status = DiscoveryJobStatus.CANCELLED
            job.completed_at = timezone.now()
            job.updated_by = user
            job.save(
                update_fields=[
                    "status",
                    "completed_at",
                    "updated_by",
                    "updated_at",
                ]
            )
        logger.info(
            "DiscoveryJob cancelled",
            extra={"job_id": str(job.id), "cancelled_by": str(user.id)},
        )
        return job

    def retry(self, job: DiscoveryJob, user) -> DiscoveryJob:
        """Reset a failed job to PENDING and increment the retry counter.

        Only failed jobs can be retried.  The job's ``failure_reason`` is
        preserved to maintain a full failure history before the next attempt.

        Parameters
        ----------
        job:
            A job in the ``FAILED`` state.
        user:
            Analyst requesting the retry.

        Returns
        -------
        DiscoveryJob
            The reset job now in ``PENDING`` state.

        Raises
        ------
        ValueError:
            If the job is not in the ``FAILED`` state.
        """
        if job.status != DiscoveryJobStatus.FAILED:
            raise ValueError(
                f"Only FAILED jobs can be retried. Current status: '{job.status}'."
            )

        # Check provider's max_retries
        if job.retry_count >= job.provider.max_retries:
            raise ValueError(
                f"Job {job.id} has reached the maximum retry limit "
                f"({job.provider.max_retries})."
            )

        with transaction.atomic():
            job.status = DiscoveryJobStatus.PENDING
            job.started_at = None
            job.completed_at = None
            job.duration_ms = None
            job.retry_count += 1
            job.updated_by = user
            job.save(
                update_fields=[
                    "status",
                    "started_at",
                    "completed_at",
                    "duration_ms",
                    "retry_count",
                    "updated_by",
                    "updated_at",
                ]
            )

        logger.info(
            "DiscoveryJob queued for retry",
            extra={
                "job_id": str(job.id),
                "retry_count": job.retry_count,
                "requested_by": str(user.id),
            },
        )
        return job

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    def _transition(
        self,
        job: DiscoveryJob,
        new_status: str,
        *,
        started_at: datetime | None = None,
    ) -> None:
        """Persist a job status transition atomically."""
        update_fields = ["status", "updated_at"]
        job.status = new_status
        if started_at is not None:
            job.started_at = started_at
            update_fields.append("started_at")
        with transaction.atomic():
            job.save(update_fields=update_fields)

    def _fail_job(
        self,
        job: DiscoveryJob,
        exc: Exception,
    ) -> list[DiscoveryResult]:
        """Transition job to FAILED, record failure reason, emit event."""
        failure_reason = str(exc)
        with transaction.atomic():
            job.status = DiscoveryJobStatus.FAILED
            job.completed_at = timezone.now()
            job.failure_reason = failure_reason
            job.save(
                update_fields=[
                    "status",
                    "completed_at",
                    "failure_reason",
                    "updated_at",
                ]
            )

        self._emit(
            DiscoveryJobFailed(
                aggregate_id=job.id,
                aggregate_type="DiscoveryJob",
                job_id=job.id,
                failure_reason=failure_reason,
                retry_count=job.retry_count,
            )
        )

        logger.error(
            "DiscoveryJob failed",
            extra={
                "job_id": str(job.id),
                "failure_reason": failure_reason,
                "retry_count": job.retry_count,
            },
            exc_info=True,
        )
        return []

    @staticmethod
    def _record_health(provider: DiscoveryProvider, health) -> None:
        """Persist the health snapshot onto the DiscoveryProvider record."""
        DiscoveryProvider.objects.filter(pk=provider.pk).update(
            last_health_check_at=datetime.now(tz=UTC),
            last_health_status=health.healthy,
            last_health_message=health.message[:500],
        )
        # Refresh the in-memory object to reflect the update
        provider.refresh_from_db(
            fields=["last_health_check_at", "last_health_status", "last_health_message"]
        )

    @staticmethod
    def _build_result_dto(normalised: dict, raw: dict) -> DiscoveryResultDTO:
        """Construct a DiscoveryResultDTO from normalised + raw provider dicts."""
        from backend.apps.osint.enums import DiscoveryResultType

        result_type = normalised.get("type", DiscoveryResultType.RAW)
        title = normalised.get("title", "Untitled Finding")
        summary = normalised.get("summary", "")
        source_url = normalised.get("source_url", "")
        storage_key = normalised.get("storage_key", "")
        tags = normalised.get("tags", [])

        raw_confidence = normalised.get("confidence", "1.0000")
        try:
            confidence = Decimal(str(raw_confidence)).quantize(Decimal("0.0001"))
        except Exception:
            confidence = Decimal("1.0000")

        return DiscoveryResultDTO(
            result_type=result_type,
            title=title,
            summary=summary,
            confidence=confidence,
            raw_data=raw,
            normalised_data=normalised,
            storage_key=storage_key,
            source_url=source_url,
            tags=tags,
        )

    @staticmethod
    def _emit(event) -> None:
        """Emit a domain event.

        Sprint 6 logs the event; an event dispatcher will be wired in a
        later sprint when the notification and analytics domains are ready.
        """
        logger.debug(
            "Domain event emitted",
            extra={"event": event.to_dict()},
        )
