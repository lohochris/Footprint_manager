# Sprint 6 — OSINT Discovery Domain Implementation Report

**Date:** 2026-07-04
**Sprint:** 6 — OSINT Discovery Bounded Context
**Status:** Implemented

---

## Executive Summary

Sprint 6 introduces the **OSINT Discovery** bounded context as a standalone
Django application (`backend/apps/osint/`).  The domain provides three
aggregate roots — `DiscoveryProvider`, `DiscoveryJob`, `DiscoveryResult` — and
exposes a provider framework, service layer, selector layer, pipeline
integration, and domain event module.

All eight architectural refinements authorised by the sprint sponsor are
implemented.

---

## Refinement Certification

### Refinement 1 — `DecimalField` for relationship confidence

`DiscoveryResult.confidence` is declared as:
```python
confidence = models.DecimalField(
    max_digits=5,
    decimal_places=4,
    default=Decimal("1.0000"),
    validators=[MinValueValidator(Decimal("0.0000")), MaxValueValidator(Decimal("1.0000"))],
)
```
This matches the `InvestigationTarget.confidence` pattern certified in Sprint 3A.
No `FloatField` appears anywhere in the OSINT domain.

---

### Refinement 2 — `DiscoveryProvider` aligned with Sprint 3B provider framework

`DiscoveryProvider` carries all Sprint 3B-aligned fields:

| Field | Type | Purpose |
|---|---|---|
| `version` | CharField | SemVer string |
| `capabilities` | JSONField | List of `DiscoveryCapability` values |
| `last_health_check_at` | DateTimeField | Health snapshot timestamp |
| `last_health_status` | BooleanField | Healthy at last probe |
| `last_health_message` | CharField | Health message |
| `priority` | IntegerField | Routing priority (mirrors `ProviderRegistry`) |
| `timeout_seconds` | PositiveIntegerField | Max discover() duration |
| `max_retries` | PositiveSmallIntegerField | Max automatic retries |

---

### Refinement 3 — Execution metadata on `DiscoveryJob`

`DiscoveryJob` carries full execution observability:

| Field | Purpose |
|---|---|
| `started_at` | UTC datetime when `provider.discover()` began |
| `completed_at` | UTC datetime when job reached terminal state |
| `duration_ms` | Wall-clock ms computed by `DiscoveryJobService` |
| `failure_reason` | Most recent error description; preserved across retries |
| `triggered_by` | `DiscoveryJobTrigger` value (manual/scheduled/webhook/api) |
| `retry_count` | Number of retry attempts made |

---

### Refinement 4 — `DiscoveryResult` references `DiscoveryProvider` FK

```python
provider = models.ForeignKey(
    DiscoveryProvider,
    on_delete=models.SET_NULL,
    related_name="results",
    null=True,
    blank=True,
)
```
`SET_NULL` preserves results when the provider catalogue entry is deleted.
The FK is denormalised from `job.provider` for efficient per-provider filtering.

---

### Refinement 5 — Storage-agnostic identifier

`DiscoveryResult.storage_key` (CharField, max_length=1024) references
`StoredFile.key` from `backend.shared.storage`.  No `FileField` or filesystem
path appears on the model.

---

### Refinement 6 — Anti-corruption layer for Evidence uploads

`EvidenceUploadRequest` in `backend/apps/osint/dto.py` is a frozen dataclass
with `storage_key`, `original_filename`, `mime_type`, `size_bytes`,
`checksum_sha256`.  Zero Django file primitives (`SimpleUploadedFile`,
`InMemoryUploadedFile`, `FileField`) appear in the OSINT domain.

Test `TestEvidenceUploadRequestDTO.test_no_django_file_primitives_in_module`
statically asserts this constraint via `inspect.getsource()`.

---

### Refinement 7 — Standardised provider interface

`BaseDiscoveryProvider` (ABC) defines seven methods:

```
initialize()         — load credentials / warm up
health_check()       — return DiscoveryHealthStatus snapshot
capabilities()       — list of DiscoveryCapability strings
supports(capability) — bool
validate_target(input_data) — raise on invalid input
discover(input_data) — list[dict] raw results
normalize(raw)       — dict canonical schema
```

`NoOpDiscoveryProvider` implements all seven methods deterministically
for offline testing.  `DiscoveryProviderRegistry` provides priority-ordered
registration matching `intelligence.providers.registry.ProviderRegistry`.

---

### Refinement 8 — Domain events

Five domain events in `backend/apps/osint/events/__init__.py`:

| Event | Trigger |
|---|---|
| `DiscoveryJobQueued` | Job created and placed in queue |
| `DiscoveryJobStarted` | Job transitions to RUNNING |
| `DiscoveryJobCompleted` | Job transitions to COMPLETED |
| `DiscoveryJobFailed` | Job transitions to FAILED |
| `DiscoveryResultCreated` | DiscoveryResult row persisted |

All extend `backend.shared.events.BaseDomainEvent`.
All are frozen dataclasses (immutable).
All have unique `event_type` strings in the `"osint.*"` namespace.
`DiscoveryJobService._emit()` logs events; dispatcher integration is deferred
to the Notifications sprint.

---

## File Inventory

```
backend/apps/osint/
├── __init__.py
├── apps.py                         OsintConfig AppConfig
├── admin.py                        ModelAdmin for all 3 models
├── enums.py                        5 TextChoices enumerations
├── dto.py                          DiscoveryRequest, DiscoveryResultDTO, EvidenceUploadRequest
├── registry.py                     PipelineFactory + PipelineRegistry wiring
├── events/
│   └── __init__.py                 5 domain events
├── migrations/
│   ├── __init__.py
│   └── 0001_initial.py             3 tables, 10 indexes (auto-generated)
├── models/
│   ├── __init__.py
│   ├── discovery_provider.py       DiscoveryProvider aggregate root
│   ├── discovery_job.py            DiscoveryJob aggregate root
│   └── discovery_result.py        DiscoveryResult aggregate root
├── providers/
│   ├── __init__.py
│   ├── base.py                     BaseDiscoveryProvider ABC (7 methods)
│   ├── noop_provider.py            NoOpDiscoveryProvider + self-registration
│   ├── provider_metadata.py        DiscoveryHealthStatus frozen dataclass
│   └── registry.py                 DiscoveryProviderRegistry + singleton
├── selectors/
│   ├── __init__.py
│   └── discovery_selectors.py     8 read-only QuerySet helpers
├── services/
│   ├── __init__.py
│   ├── discovery_job_service.py   DiscoveryJobService (create/run/cancel/retry)
│   └── pipeline_stages.py         8 pipeline stages for 2 operations
└── tests/
    ├── __init__.py
    ├── test_events.py
    ├── test_models.py
    ├── test_providers.py
    ├── test_selectors.py
    └── test_services.py
```

### Modified files

| File | Change |
|---|---|
| `backend/config/settings/base.py` | Added `"backend.apps.osint"` to `LOCAL_APPS` |

---

## Database Schema

### `osint_discoveryprovider`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `name` | varchar(100) UNIQUE | slug |
| `display_name` | varchar(200) | |
| `version` | varchar(30) | SemVer |
| `description` | text | |
| `provider_status` | varchar(20) | active/inactive/degraded/deprecated |
| `priority` | int | lower = higher priority |
| `timeout_seconds` | int | |
| `max_retries` | smallint | |
| `capabilities` | jsonb | list of DiscoveryCapability values |
| `last_health_check_at` | timestamptz NULL | |
| `last_health_status` | boolean NULL | |
| `last_health_message` | varchar(500) | |
| `configuration` | jsonb | credentials placeholder |
| `is_active` | boolean | |
| `created_at` / `updated_at` | timestamptz | |
| `created_by_id` / `updated_by_id` | UUID FK NULL | |

### `osint_discoveryjob`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `investigation_id` | UUID FK NULL → investigations | |
| `target_id` | UUID FK NULL → investigations_target | SET_NULL |
| `provider_id` | UUID FK → osint_discoveryprovider | PROTECT |
| `status` | varchar(20) | |
| `triggered_by` | varchar(20) | |
| `capabilities_requested` | jsonb | |
| `input_data` | jsonb | |
| `started_at` | timestamptz NULL | |
| `completed_at` | timestamptz NULL | |
| `duration_ms` | int NULL | |
| `failure_reason` | text | |
| `retry_count` | smallint | |
| `scheduled_at` | timestamptz NULL | |
| `metadata` | jsonb | |
| `is_deleted` / `deleted_at` | soft-delete | |

### `osint_discoveryresult`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `job_id` | UUID FK → osint_discoveryjob | CASCADE |
| `provider_id` | UUID FK NULL → osint_discoveryprovider | SET_NULL |
| `result_type` | varchar(20) | |
| `title` | varchar(500) | |
| `summary` | text | |
| `confidence` | numeric(5,4) | **DecimalField** [0.0000, 1.0000] |
| `raw_data` | jsonb | |
| `normalised_data` | jsonb | |
| `storage_key` | varchar(1024) | **not file_path** |
| `evidence_id` | UUID NULL | plain UUID, not FK |
| `source_url` | varchar(2000) | |
| `tags` | jsonb | |
| `is_verified` | boolean | |
| `verified_by_id` | UUID NULL | plain UUID, not FK |
| `is_deleted` / `deleted_at` | soft-delete | |

---

## Future Sprint Integration Points

| Domain | Integration | Notes |
|---|---|---|
| Identity Resolution | Consume `DiscoveryResult.normalised_data` | Link `evidence_id` |
| Graph Intelligence | Subscribe to `DiscoveryResultCreated` events | Node/edge creation |
| Risk Intelligence | Subscribe to `DiscoveryJobCompleted` events | Score computation |
| Notifications | Wire `DiscoveryJobService._emit()` to dispatcher | Sprint 7 |
| Celery async | Wrap `DiscoveryJobService.run()` in a task | Sprint 7 |
