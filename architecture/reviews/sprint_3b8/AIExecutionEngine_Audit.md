# AIExecutionEngine Audit

**Date:** 2026-07-01  
**Sprint:** 3B.8 Discovery

---

## Current State

`AIExecutionEngine` **does not exist** in the codebase.

No file, class, or function with this name exists anywhere under `backend/`.

---

## Proposed Design

### Location

```
backend/intelligence/engine.py
```

### Responsibilities

1. Accept an `AIRequest`.
2. Delegate provider selection to a `Router`.
3. Call `provider.execute(request)`.
4. Return an `AIResponse`.
5. Not raise uncaught exceptions — surface failures as error-status `AIResponse`.

### Interface (proposed)

```python
class AIExecutionEngine:
    def __init__(self, router: Router) -> None: ...
    def execute(self, request: AIRequest) -> AIResponse: ...
```

### Constraints

- No HTTP calls.
- No SDK instantiation.
- No randomness.
- No environment variable dependencies.
- Must be synchronous (no async/await).
- Must be testable with any registered provider.

---

## Dependencies

| Dependency | Status |
|---|---|
| `AIRequest` (`intelligence/providers/request.py`) | ✅ Exists |
| `AIResponse` (`intelligence/providers/response.py`) | ✅ Exists |
| `Router` (to be created) | ❌ Not yet built |
| `ProviderRegistry` (`intelligence/providers/registry.py`) | ✅ Exists |

---

## Interaction with Pipeline

`AIExecutionEngine` is not a `PipelineStage`. It is a dependency of `IntelligenceStage`. The stage creates the engine, delegates execution, and returns the context update.

```
IntelligenceStage.execute(context)
  → builds AIRequest from context
  → calls AIExecutionEngine.execute(request)
  → receives AIResponse
  → returns context.with_updates(intelligence_context=response)
```

---

## Error Handling Strategy

The engine should catch provider exceptions and return a structured `AIResponse(status="error", ...)` rather than propagating the exception. This allows the pipeline to continue (or stop gracefully via `IntelligenceStage`) without leaking implementation details.

---

## Test Strategy

- Unit test with `DummyProvider` (always succeeds).
- Unit test with `MockProvider(MockScenario.FAILURE)` (always fails gracefully).
- No Django DB required.
- No external calls.
