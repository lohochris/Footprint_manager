# Execution Context Report

**Date:** 2026-07-01  
**Sprint:** 3B.8 Discovery

---

## Current State

Two "execution context" concepts coexist in the codebase. Their relationship and propagation strategy must be clarified for Sprint 3B.8.

---

## Context Type 1 — PipelineContext

**File:** `backend/apps/common/pipeline/core.py`  
**Type:** `@dataclass(frozen=True)`

```python
@dataclass(frozen=True)
class PipelineContext:
    performed_by: Any
    tenant: Any
    payload: dict[str, Any]        # primary data being processed
    metadata: dict[str, Any]       # enrichable metadata
    stage_results: dict[str, Any]  # stage execution audit trail
    errors: list[Exception]        # captured errors
    execution_id: str              # unique run ID (UUID)
    timestamps: dict[str, float]   # start/end timing
    # Intelligence hooks (added ahead of Sprint 3B.8):
    intelligence_enabled: bool | None = None
    intelligence_context: Any = None
```

**Role in Sprint 3B.8:** The primary container that flows through the pipeline. `IntelligenceStage` reads from it and writes back via `context.with_updates(intelligence_context=ai_response)`.

---

## Context Type 2 — ExecutionContext

**File:** `backend/intelligence/context.py`  
**Type:** `@dataclass(frozen=True)`

```python
@dataclass(frozen=True)
class ExecutionContext:
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Role in Sprint 3B.8:** Passed to `AIRequest.execution_context`. Can carry intelligence-specific data (e.g., previous AI results, session context) into the provider execution. Currently minimal — sufficient for the Sprint 3B.8 offline providers.

---

## Propagation Model

```
PipelineContext (pipeline level)
    ↓  IntelligenceStage reads payload + metadata
AIRequest.execution_context = ExecutionContext(data=..., metadata=...)
    ↓  Provider executes
AIResponse (frozen)
    ↓  IntelligenceStage updates context
PipelineContext.intelligence_context = AIResponse
    ↓  Pipeline returns
ExecutionResult.metadata["ai_response"] = context.intelligence_context
```

---

## intelligence_context Field

`PipelineContext.intelligence_context` typed as `Any`. In Sprint 3B.8 it will hold an `AIResponse` object. In later sprints it may hold a richer `ExecutionContext` or a structured intelligence result.

The `Any` typing is intentional — it keeps the pipeline infrastructure independent of the `intelligence` package, preserving Clean Architecture layering:

```
apps/common/pipeline  ──────────────────────────────────────────────→
                                                     (no dependency)
intelligence/                                                       ←─
```

---

## intelligence_enabled Flag

`PipelineContext.intelligence_enabled` is currently always `None` (never set by any existing code). Sprint 3B.8 introduces:

- `None` → check the `ENABLE_AI` feature flag
- `True` → override: run AI even if flag is off (for testing)
- `False` → override: skip AI even if flag is on

---

## No Conflicts

Both context types serve distinct purposes and do not overlap. No modifications to `ExecutionContext` or `PipelineContext` are required for Sprint 3B.8.

---

## Recommendation for Sprint 3B.8

- Pass `ExecutionContext(data=context.payload, metadata=context.metadata)` as `AIRequest.execution_context`.
- Store `AIResponse` in `PipelineContext.intelligence_context`.
- Surface the response in `ExecutionResult.metadata` as `"ai_response"` for downstream consumers.
- Do NOT change the type annotation of `intelligence_context` from `Any` — this preserves the pipeline/intelligence layer boundary.
