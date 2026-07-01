# Provider Lifecycle Report

**Date:** 2026-07-01
**Scope:** Provider initialization, shutdown/disposal, health, readiness, availability, and registration lifecycle.

## Current State

Providers implement the `AIProvider` abstract interface:

- `initialize()`
- `health_check()`
- `capabilities()`
- `supports(task)`
- `execute(request)`

The three certified offline providers are:

- `DummyProvider`
- `EchoProvider`
- `MockProvider`

All are deterministic, local, and free of network calls.

## Initialization

Current behavior:

- Providers expose `initialize()`.
- The method is a no-op in all current providers.
- `AIExecutionEngine` does not call `initialize()`.
- `ProviderRegistry` does not initialize providers at registration time.

Finding:

- Initialization is part of the provider contract but not part of the execution lifecycle.

Recommendation:

- Define initialization as idempotent.
- Track initialization state separately from registration.
- Keep initialization local-only in Sprint 3B.9.
- Do not load credentials, SDKs, HTTP clients, or external connections.

Suggested lifecycle states:

| State | Meaning |
|---|---|
| `registered` | Provider class is known to the registry |
| `created` | Provider instance has been constructed |
| `initialized` | Provider has completed local setup |
| `ready` | Provider can accept execution requests |
| `unhealthy` | Provider exists but should not be selected |
| `shutting_down` | Provider is being disposed |
| `disposed` | Provider should not be used |

## Shutdown and Disposal

Current behavior:

- No shutdown/disposal method exists.
- Providers do not hold resources that need disposal.

Finding:

- The absence of disposal is acceptable for current offline providers, but the lifecycle framework should reserve a disposal hook before production execution expands.

Recommendation:

- Add architecture for `shutdown()` or `dispose()` as an optional lifecycle hook.
- Keep it no-op for current providers.
- Require idempotence.
- Do not introduce async lifecycle or external cleanup yet.

## Health Model

Current behavior:

- `provider_metadata.HealthStatus` is a frozen dataclass with `healthy`, `message`, and `timestamp`.
- Concrete providers return `HealthStatus`.
- `AIProvider.health_check()` is typed as `Dict[str, Any]`.

Finding:

- The health contract is inconsistent. Runtime behavior follows `HealthStatus`; the abstract base still documents a dictionary model.

Recommendation:

- Standardize on a structured health model.
- Extend health with production-relevant local fields only.

Suggested future health fields:

| Field | Purpose |
|---|---|
| `healthy` | Provider is functioning |
| `ready` | Provider can execute now |
| `available` | Provider is eligible for selection |
| `configured` | Required local configuration is present |
| `enabled` | Policy/feature flag allows use |
| `message` | Human-readable status |
| `reason_code` | Machine-readable status reason |
| `checked_at` | Timestamp |
| `diagnostics` | Optional structured local diagnostics |

## Readiness

Readiness should mean the provider can accept an execution request now.

Examples:

- Initialized.
- Enabled by policy.
- Supports requested task.
- Health status is acceptable for the selected policy.

Readiness should not mean:

- The provider is registered.
- The provider exists in code.
- The provider is preferred by metadata.

## Availability

Availability should mean the provider is eligible to be considered by the router.

Availability should combine:

- Registration.
- Policy enablement.
- Health status.
- Capability match.
- Required/preferred/fallback constraints.

Availability should remain offline. It should not make remote calls.

## Registration Lifecycle

Current behavior:

- Providers register classes through `register_provider()`.
- Global registration occurs as a side effect of provider module import.
- Registry ordering is deterministic by provider `priority`, with default priority `0`.
- Duplicate provider names raise `ValueError`.
- Registry stores classes, not instances.

Findings:

- Class registration keeps providers lightweight and testable.
- Side-effect registration works but makes startup ordering important.
- Registry mutation is not thread-safe.
- `capabilities(name)` temporarily instantiates provider classes.

Recommendation:

- Keep class registration for Sprint 3B.9 unless instance lifecycle becomes required.
- Add lock protection or freeze-after-startup semantics.
- Avoid instantiating providers during routing if metadata can answer capability questions.
- Define registration as separate from provider readiness.

## Provider Lifecycle Target

Recommended future lifecycle:

```text
register provider class
    -> inspect metadata
    -> construct provider instance
    -> initialize provider
    -> health check
    -> mark ready/available
    -> execute request
    -> collect diagnostics
    -> shutdown/dispose when engine/container stops
```

For Sprint 3B.9, this should be implemented with local deterministic providers only.

## Regression Guardrails

- Do not introduce external providers.
- Do not introduce HTTP clients, SDKs, API keys, or network calls.
- Do not change business services.
- Preserve deterministic provider outputs.
- Preserve `AIExecutionEngine.execute()` returning `ExecutionResult` in all cases.
