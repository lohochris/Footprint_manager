# Diagnostics Architecture

**Date:** 2026-07-01
**Scope:** Execution diagnostics, timing collection, failure classification, and result metadata.

## Current Diagnostics

Current diagnostics sources:

- `AIResponse.diagnostics`
- `ExecutionResult.metadata`
- Logger calls inside `AIExecutionEngine`
- Pipeline `stage_results`
- Pipeline `errors`

Current limitations:

- Diagnostics are not consistently structured.
- Router decisions are not captured.
- Health checks are not captured.
- Per-phase timings are not captured.
- Failure classes are not normalized.
- Final `Pipeline.run()` result does not surface `PipelineContext.intelligence_context`.

## Target Diagnostic Model

Diagnostics should be structured, deterministic, serializable, and safe to return through `ExecutionResult.metadata`.

Suggested top-level shape:

```text
metadata = {
    "task": "...",
    "provider": "...",
    "diagnostics": {
        "execution_id": "...",
        "policy": {...},
        "routing": {...},
        "health": {...},
        "timing": {...},
        "failure": {...},
        "attempts": [...]
    }
}
```

## Timing Collection

Current engine measures total elapsed time with `time.monotonic()`.

Recommended phase timings:

- `feature_flag_seconds`
- `policy_resolution_seconds`
- `routing_seconds`
- `provider_initialization_seconds`
- `health_check_seconds`
- `provider_execution_seconds`
- `response_mapping_seconds`
- `total_seconds`

All timings should use `time.monotonic()`.

## Failure Diagnostics

Recommended failure fields:

| Field | Purpose |
|---|---|
| `class` | Normalized failure class |
| `message` | Safe message |
| `exception_type` | Python exception type when applicable |
| `provider` | Provider involved |
| `task` | Requested task |
| `retryable` | Future retry eligibility |
| `fallback_attempted` | Whether fallback was attempted |
| `fallback_provider` | Provider used or considered |

Exception objects should remain in `ExecutionResult.error` only when current behavior requires it. Metadata diagnostics should use safe strings and structured fields.

## Router Diagnostics

Router diagnostics should include:

- Requested task.
- Required provider.
- Preferred provider.
- Fallback provider.
- Candidate provider names.
- Capability matches.
- Selected provider.
- Selection reason.
- Fallback reason if used.

## Health Diagnostics

Health diagnostics should include:

- Provider name.
- Health result.
- Readiness result.
- Availability result.
- Reason code.
- Health check duration.
- Whether health was required or skipped.

## Dry-Run Diagnostics

Current dry-run skips provider selection.

Recommended options:

| Option | Benefit | Risk |
|---|---|---|
| Keep current dry-run | Stable Sprint 3B.8 behavior | Does not validate routing/policy |
| Policy dry-run | Validates policy and selection without execution | Changes expectations |
| Full simulated dry-run | Exercises all lifecycle except provider execution | More implementation complexity |

Recommendation:

- Keep current dry-run semantics at first.
- Add a future `validate_only` or `policy_dry_run` mode if needed.

## Pipeline Visibility

Issue:

- `IntelligenceStage` attaches the engine result to `PipelineContext.intelligence_context`.
- `Pipeline.run()` returns only `ExecutionResult(data=context.payload, metadata=context.metadata)`.

Impact:

- A caller using only `Pipeline.run()` cannot see intelligence diagnostics unless the stage also copies them into metadata or the pipeline result model is extended.

Recommendation:

- Do not change business services in Sprint 3B.9.
- Prefer stage-level metadata enrichment if diagnostics must surface through the final pipeline result.
- Keep this change additive and tested.

## Safety Constraints

Diagnostics must not contain:

- API keys.
- External provider credentials.
- Raw secrets.
- Sensitive business payloads unless explicitly approved.

For current offline providers, diagnostics can safely include provider names, task names, timing, status, and reason codes.
