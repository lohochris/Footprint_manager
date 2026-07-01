# Health Check Architecture

**Date:** 2026-07-01
**Scope:** Provider health model, readiness, availability, and health validation flow.

## Current Health Contract

Current implementations:

- `HealthStatus` dataclass exists in `provider_metadata.py`.
- `DummyProvider.health_check()` returns `HealthStatus`.
- `EchoProvider.health_check()` returns `HealthStatus`.
- `MockProvider.health_check()` returns `HealthStatus`.

Current mismatch:

- `AIProvider.health_check()` is typed and documented as returning `Dict[str, Any]`.

## Required Decision

Sprint 3B.9 should standardize provider health on a structured object rather than dictionaries.

Recommended decision:

- Use a single frozen health dataclass.
- Keep it serializable through diagnostics conversion.
- Do not use provider-specific ad hoc health dictionaries.

## Proposed Health Concepts

Health:

- Whether the provider implementation is functioning.

Readiness:

- Whether the provider can execute the current request now.

Availability:

- Whether policy and router should consider the provider eligible.

These concepts should be related but not identical.

## Proposed Fields

| Field | Required | Purpose |
|---|---:|---|
| `healthy` | Yes | Implementation is operational |
| `ready` | Yes | Provider can execute now |
| `available` | Yes | Provider may be selected |
| `configured` | Yes | Required local config exists |
| `enabled` | Yes | Policy allows provider |
| `message` | Yes | Human-readable state |
| `reason_code` | Yes | Machine-readable state |
| `checked_at` | Yes | Timestamp |
| `details` | No | Structured local diagnostics |

For current offline providers, all fields should be deterministic except timestamp.

## Health Validation Flow

Recommended flow:

```text
ExecutionPolicy resolved
    -> Router finds candidate providers
    -> Health policy validates candidates
    -> Router selects eligible provider
    -> Engine executes selected provider
    -> Diagnostics record health snapshot
```

Alternative flow:

```text
ExecutionPolicy resolved
    -> Router selects candidate
    -> Engine health-checks selected provider
    -> Fallback policy asks router for another candidate if needed
```

Recommendation:

- Use the second flow initially. It is simpler and fits the existing engine/router boundary.
- Later, router can accept policy and health snapshots for health-aware ranking.

## Health Failure Mapping

| Health State | Result |
|---|---|
| `healthy=True`, `ready=True`, `available=True` | Execute |
| `healthy=False` | Fail or fallback |
| `ready=False` | Fail or fallback |
| `available=False` | Exclude from selection |
| Health check raises | Classify as `health_check_exception` |

Recommended status codes:

- `503` for no healthy/available provider.
- `500` only if internal health validation code fails unexpectedly.

## Health Diagnostics

Each execution result should include:

- Provider name.
- Health status.
- Health reason code.
- Health check duration.
- Whether fallback was considered.
- Whether health check was skipped and why.

## Offline Constraint

Health checks must remain local. They may inspect provider metadata and local state only.

Disallowed in Sprint 3B.9:

- HTTP health probes.
- SDK pings.
- API key validation calls.
- Remote model listing.
- External service reachability checks.

## Regression Requirements

- Existing providers remain healthy by default.
- Existing Sprint 3B.7 health tests remain valid or are migrated to the aligned health contract.
- Existing Sprint 3B.8 engine tests continue to pass with updated expectations only where policy diagnostics are added.
