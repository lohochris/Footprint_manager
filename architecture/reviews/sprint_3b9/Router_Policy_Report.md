# Router Policy Report

**Date:** 2026-07-01
**Scope:** Preferred provider, required provider, fallback provider, policy-driven selection, and router behavior.

## Current Router Behavior

Selection order:

1. If `request.metadata["provider"]` exists, select that provider by name.
2. Otherwise, choose the first registered provider that supports `request.task`.
3. If no provider supports the task, return registry default.
4. If registry is empty, raise `NoProviderAvailableError`.

The router returns provider classes, not instances.

## Current Strengths

- Deterministic.
- Simple.
- Fully offline.
- Testable with isolated registries.
- Does not execute providers.
- Keeps business logic out of routing.

## Current Risks

| Risk | Impact |
|---|---|
| Explicit provider bypasses capability checks | A provider can be selected for unsupported tasks |
| Silent default fallback | Unsupported tasks can execute against an arbitrary default |
| No health filtering | Unhealthy providers can be selected |
| No policy object | Selection semantics are encoded in metadata conventions |
| No diagnostics | Selection decisions are hard to inspect |

## Preferred Provider

Meaning:

- Try this provider first when it is registered, healthy, available, and capable.
- If it is not eligible, use fallback policy.

Recommended metadata:

- `preferred_provider`

Recommended behavior:

- Missing preferred provider should not fail if fallback is allowed.
- Unhealthy preferred provider should not fail if fallback is allowed.
- Unsupported preferred provider should not fail if capability fallback is allowed.

## Required Provider

Meaning:

- The request must use this provider.
- If it is missing, unhealthy, unavailable, or incapable, fail closed.

Recommended metadata:

- `required_provider`

Backward compatibility:

- Treat current `metadata["provider"]` as `required_provider` in Sprint 3B.9 unless explicitly changed.

Recommended behavior:

- Unknown required provider -> `provider_not_found`.
- Unhealthy required provider -> `provider_unhealthy`.
- Unsupported required provider -> `unsupported_task`.
- No implicit fallback.

## Fallback Provider

Meaning:

- A named provider to use if preferred selection cannot proceed.

Recommended metadata:

- `fallback_provider`

Recommended behavior:

- Fallback provider must still be registered, healthy, available, and capable.
- Fallback should be reported in diagnostics.
- Fallback should never hide a required-provider failure unless policy explicitly permits it.

## Policy-Driven Selection

Router should eventually accept either:

- `AIRequest` plus `ExecutionPolicy`, or
- a derived immutable `ProviderSelectionRequest`.

Recommended selection inputs:

- Task.
- Required provider.
- Preferred provider.
- Fallback provider.
- Capability requirements.
- Health requirement.
- Fallback mode.
- Selection strategy.

Recommended selection output:

- Selected provider class.
- Selection reason.
- Candidate diagnostics.
- Fallback diagnostics.

## Selection Strategies

Initial strategies:

| Strategy | Meaning |
|---|---|
| `required_only` | Use named provider or fail |
| `preferred_then_capable` | Try preferred, then any capable provider |
| `capability_first` | Current default, but without unsupported default fallback |
| `priority_first` | Sort capable providers by priority |
| `health_first` | Prefer healthy and ready providers |

Sprint 3B.9 should start with `capability_first` plus explicit required/preferred/fallback semantics.

## Fallback Behavior Recommendation

Replace current default fallback with:

```text
if no capable providers:
    fail with NoProviderAvailableError or UnsupportedTaskError
```

Then add policy modes:

```text
fallback_mode = "none" | "named" | "capability" | "default_if_capable"
```

Default should be `none` or `default_if_capable`, not current unconditional default fallback.

## Router Boundary

Router should not:

- Execute providers.
- Initialize providers.
- Dispose providers.
- Perform network calls.
- Mutate business payloads.
- Know about business services.

Router may:

- Inspect provider metadata.
- Query registry.
- Instantiate providers only if current capability APIs require it.
- Return diagnostics.

## Tests Required

Add tests for:

- Required provider success.
- Required provider unknown.
- Required provider unsupported task.
- Preferred provider selected when eligible.
- Preferred provider falls back when policy allows.
- Fallback provider selected only when capable.
- No silent default fallback.
- Router diagnostics include candidate and selection reason.
