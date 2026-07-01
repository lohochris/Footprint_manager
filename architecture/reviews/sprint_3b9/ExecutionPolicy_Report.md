# ExecutionPolicy Report

**Date:** 2026-07-01
**Step:** Sprint 3B.9 Step 1

## Implementation

`ExecutionPolicy` was added in:

- `backend/intelligence/policies/execution_policy.py`

It is a frozen dataclass and is immutable after construction.

## Fields

| Field | Default | Purpose |
|---|---|---|
| `required_provider` | `None` | Provider that must be used by future routing policy |
| `preferred_provider` | `None` | Provider that should be tried first by future routing policy |
| `fallback_provider` | `None` | Named fallback candidate for future policy |
| `fallback_mode` | `"none"` | Fallback strategy declaration |
| `selection_strategy` | `"capability_first"` | Provider selection strategy declaration |
| `retry_enabled` | `False` | Retry architecture switch |
| `max_attempts` | `1` | Attempt count; remains `1` when retries disabled |
| `timeout_seconds` | `None` | Timeout declaration; no timeout execution added |
| `health_required` | `True` | Health validation declaration |
| `diagnostics_enabled` | `True` | Diagnostics collection declaration |
| `dry_run` | `False` | Dry-run declaration |

## ExecutionPolicyBuilder

`ExecutionPolicyBuilder` was added in:

- `backend/intelligence/policies/policy_builder.py`

Builder responsibilities:

- Normalize request policy metadata.
- Normalize request policy options.
- Apply defaults.
- Apply feature flag snapshot.
- Validate values.
- Return immutable `ExecutionPolicy`.

Builder non-responsibilities:

- No provider selection.
- No provider execution.
- No health checks.
- No retries.
- No fallback execution.
- No network operations.
- No external AI provider integration.

## Mapping Rules

Precedence:

1. Base defaults.
2. Builder defaults.
3. `AIRequest.options`.
4. `AIRequest.metadata`.
5. Explicit `dry_run` argument to `build()`.

Backward compatibility:

- `AIRequest.metadata["provider"]` maps to `ExecutionPolicy.required_provider`.
- Explicit `required_provider` takes precedence over legacy `provider`.

## Validation Rules

Valid fallback modes:

- `none`
- `named`
- `capability`
- `default_if_capable`

Valid selection strategies:

- `required_only`
- `preferred_then_capable`
- `capability_first`
- `priority_first`
- `health_first`

Validation:

- `max_attempts >= 1`.
- `timeout_seconds > 0` when set.
- Invalid fallback modes raise `ValueError`.
- Invalid selection strategies raise `ValueError`.
- Retry remains disabled by default.

## Feature Flag Behavior

The builder accepts a feature flag snapshot. When `ENABLE_AI` is false, `health_required` is normalized to `False`.

This does not execute the feature flag gate and does not change `AIExecutionEngine`. It only records policy intent.

## Test Evidence

Dedicated tests confirm:

- Defaults.
- Immutability.
- Metadata mapping.
- Options mapping.
- Backward compatibility.
- Precedence.
- Validation.
- Retry architecture defaults.
- Dry-run mapping.
- Diagnostics mapping.
- Feature flag handling.

Result:

- Step 1 focused tests: `30 passed`.
- Sprint 3B targeted regression: `274 passed`.
