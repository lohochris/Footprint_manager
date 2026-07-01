# Execution Policy Report

**Date:** 2026-07-01
**Scope:** Health-check policy, timeout policy, retry architecture, fallback policy, provider selection, and failure classification.

## Current State

The current engine has implicit policy behavior:

- `ENABLE_AI=False` returns a failed `ExecutionResult` with status `503`.
- `dry_run=True` returns a successful simulated `ExecutionResult`.
- Router failures return status `503`.
- Provider exceptions return status `500`.
- Provider error responses return status `502`.

There is no explicit execution policy object.

## Recommended Policy Layer

Add a deterministic policy layer between `IntelligenceStage` and `Router`:

```text
IntelligenceStage
    -> build AIRequest
    -> resolve ExecutionPolicy
    -> AIExecutionEngine executes with policy
```

The policy should be data-oriented and offline. It should not create external clients or call external services.

## Policy Inputs

Potential inputs:

- `request.task`
- `request.metadata`
- `request.options`
- `context.execution_id`
- Feature flags
- Provider metadata
- Static application settings

Policy should not depend on:

- Business service classes.
- Serializers.
- Database models.
- External AI provider status.
- Network calls.

## Health-Check Policy

Required decisions:

- Check health before provider execution.
- Decide whether health is checked before or after provider selection.
- Decide whether unhealthy preferred providers can fall back.
- Decide whether required unhealthy providers fail closed.

Recommended behavior:

| Scenario | Recommended Result |
|---|---|
| Required provider unhealthy | Fail closed with classified health failure |
| Preferred provider unhealthy | Try fallback if policy allows |
| Fallback provider unhealthy | Continue evaluating remaining fallback candidates or fail |
| No healthy providers | Return `ExecutionResult(success=False, status_code=503)` |

## Timeout Policy

Current providers are local and synchronous. There are no actual timeouts.

Recommended Sprint 3B.9 architecture:

- Define timeout configuration.
- Measure elapsed time.
- Classify provider timeout responses from deterministic mock scenarios.
- Do not introduce network timeout clients.
- Do not introduce async cancellation unless needed by local execution.

Potential fields:

- `total_timeout_seconds`
- `provider_timeout_seconds`
- `health_check_timeout_seconds`
- `timeout_strategy`

## Retry Policy

Retry should be architecture-only in this sprint.

Recommended behavior:

- Define retry policy fields.
- Default `max_attempts=1`.
- Do not perform retries yet.
- Classify retry eligibility for future use.

Potential fields:

- `max_attempts`
- `retry_enabled`
- `retry_on_failure_classes`
- `backoff_strategy`
- `jitter_enabled`

For Sprint 3B.9:

- `retry_enabled=False`
- `max_attempts=1`
- Diagnostics should include `attempt=1`.

## Fallback Policy

Current router fallback silently selects registry default when no provider supports a task.

Risk:

- Unsupported tasks can be executed by providers that explicitly do not support them.

Recommended behavior:

- Fallback should be explicit and policy-driven.
- Fallback should never bypass capability checks unless a policy explicitly allows compatibility fallback.
- Required provider should not fall back unless `allow_required_fallback=True`, which should default to `False`.

Suggested modes:

| Mode | Meaning |
|---|---|
| `none` | Fail when selected provider cannot execute |
| `capability_match` | Use another provider that supports the task |
| `named_fallback` | Use configured fallback provider if healthy and capable |
| `default_provider` | Use registry default only if capable |

## Provider Selection Policy

Recommended selection semantics:

| Field | Semantics |
|---|---|
| `required_provider` | Must use this provider or fail |
| `preferred_provider` | Try this provider first, then policy fallback |
| `fallback_provider` | Named fallback candidate |
| `selection_strategy` | Capability-first, priority-first, health-first, or explicit-only |

Backward compatibility:

- Current `request.metadata["provider"]` should initially map to `required_provider`.

## Failure Classification

Current failures are represented by raw exceptions or response diagnostics.

Recommended classifications:

| Class | Examples | Status |
|---|---|---|
| `feature_disabled` | `ENABLE_AI=False` | 503 |
| `provider_not_found` | Required provider missing | 503 |
| `no_provider_available` | Empty registry or no eligible provider | 503 |
| `provider_unhealthy` | Health check failed | 503 |
| `provider_not_ready` | Not initialized or unavailable | 503 |
| `unsupported_task` | No capable provider for task | 422 or 503, decision needed |
| `provider_error_response` | `AIResponse.status != "success"` | 502 |
| `provider_exception` | Provider raised | 500 |
| `timeout` | Timeout policy exceeded or mock timeout scenario | 504 |
| `cancelled` | Future cancellation point triggered | 499 or 503, decision needed |
| `policy_violation` | Request conflicts with policy | 400 or 422 |

## Policy Hooks

Recommended deterministic hooks:

- `before_selection`
- `after_selection`
- `before_health_check`
- `after_health_check`
- `before_provider_execute`
- `after_provider_execute`
- `on_failure`
- `on_result`

Hooks should collect diagnostics and enforce policy. They should not call external providers.

## Acceptance Guardrails

- No retries executed in Sprint 3B.9 unless separately approved.
- No external provider integration.
- No HTTP or SDK clients.
- No business service changes.
- All policy behavior must be unit-tested with offline providers.
