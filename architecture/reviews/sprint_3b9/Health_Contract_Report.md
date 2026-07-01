# Health Contract Report

**Date:** 2026-07-01
**Step:** Sprint 3B.9 Step 1

## Objective

Align the official `AIProvider.health_check()` interface with the structured health model already used by the offline providers.

## Previous Contract

`AIProvider.health_check()` was typed as:

```python
def health_check(self) -> Dict[str, Any]:
```

The docstring described a dictionary health response.

## Aligned Contract

`AIProvider.health_check()` is now typed as:

```python
def health_check(self) -> HealthStatus:
```

The docstring now describes a structured health snapshot.

## Provider Compatibility

No provider runtime behavior changed.

Existing providers already returned `HealthStatus`:

- `DummyProvider`
- `EchoProvider`
- `MockProvider`

No provider execution logic was modified.

## Behavior Preserved

Providers remain:

- Deterministic.
- Offline.
- Side-effect free.
- Free of network calls.
- Free of external SDKs.
- Free of API keys.

## Test Evidence

Tests confirm:

- `AIProvider.health_check` type hint returns `HealthStatus`.
- `DummyProvider.health_check()` returns `HealthStatus`.
- `EchoProvider.health_check()` returns `HealthStatus`.
- `MockProvider.health_check()` returns `HealthStatus`.
- Offline provider health status remains healthy and message-bearing.

## Scope Boundaries

Not implemented in Step 1:

- New health checks.
- Health-aware routing.
- Health policy enforcement in the engine.
- Provider lifecycle state.
- Provider readiness/availability transitions.

Those remain future Sprint 3B.9 work after approval.
