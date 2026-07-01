# Architectural Conflict Report

**Date:** 2026-07-01
**Scope:** Conflicts discovered during Sprint 3B.9 discovery.

## Conflict 1: Certified Intelligence Pipeline vs Legacy `apps.ai` Skeleton

### Summary

The certified Sprint 3B.7/3B.8 provider execution path lives in:

- `backend/intelligence/*`

There is also an older AI abstraction skeleton in:

- `backend/apps/ai/gateway/__init__.py`
- `backend/apps/ai/providers/__init__.py`
- `backend/apps/ai/tasks/__init__.py`
- `backend/apps/ai/apps.py`

The older skeleton references gateway/provider concepts and comments naming external provider families. It is not the certified Sprint 3B execution path.

### Why It Matters

Sprint 3B.9 explicitly forbids:

- External AI providers.
- OpenAI.
- Gemini.
- Anthropic.
- Ollama.
- HTTP clients.
- SDKs.
- API keys.

The legacy skeleton does not instantiate those providers, but its naming and comments create ambiguity about where future provider lifecycle and execution policy work should occur.

### Current Runtime Risk

Low.

Reason:

- The reviewed `apps.ai` code is abstract or placeholder-oriented.
- It does not introduce concrete external provider calls.
- Sprint 3B.8 tests validate `backend/intelligence/*` as the active offline execution chain.

### Architecture Risk

Medium.

Reason:

- Two AI provider abstractions exist.
- One registers provider instances; the other registers provider classes.
- One uses `GatewayRequest/GatewayResponse`; the other uses `AIRequest/AIResponse`.
- One exposes `complete()` and `is_available()`; the other exposes `initialize()`, `health_check()`, `supports()`, and `execute()`.

### Recommendation

For Sprint 3B.9:

- Treat `backend/intelligence/*` as the authoritative provider lifecycle and execution policy boundary.
- Do not implement policy or lifecycle in `backend/apps/ai/*`.
- Do not delete the legacy skeleton without explicit approval.
- Add documentation that `apps.ai` remains dormant or future-facing.

For a later sprint:

- Decide whether `apps.ai` should become an adapter over `backend/intelligence/*`, be migrated, or be retired.

## Conflict 2: Pipeline Result Visibility

### Summary

`IntelligenceStage` stores the engine result in `PipelineContext.intelligence_context`, but `Pipeline.run()` returns an `ExecutionResult` whose `metadata` is only `context.metadata` and whose `data` is only `context.payload`.

### Why It Matters

The future flow requires:

```text
Diagnostics -> ExecutionResult
```

The engine already returns diagnostics-capable `ExecutionResult`, but the outer pipeline result does not automatically expose that result.

### Current Runtime Risk

Low.

Reason:

- Sprint 3B.8 acceptance only required the stage to work inside the pipeline and return a successful pipeline result.

### Architecture Risk

Medium.

Reason:

- Production diagnostics may be invisible to callers who only receive the final pipeline result.

### Recommendation

For Sprint 3B.9:

- Prefer adding intelligence diagnostics into `context.metadata` from `IntelligenceStage` if final pipeline visibility is required.
- Avoid changing business services.
- Avoid broad `Pipeline.run()` contract changes unless explicitly approved.

## Conflict 3: Health Contract Type Mismatch

### Summary

`AIProvider.health_check()` is documented as returning a dictionary, while concrete providers return `HealthStatus`.

### Risk

Medium.

### Recommendation

Resolve early in Sprint 3B.9 by standardizing the health contract.

## Conflict Decision

Architectural conflicts exist but none require business service, serializer, model, or repository changes during Sprint 3B.9.
