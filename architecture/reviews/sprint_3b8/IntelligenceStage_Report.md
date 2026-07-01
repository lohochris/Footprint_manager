# IntelligenceStage Report

**Date:** 2026-07-01  
**Sprint:** 3B.8  
**Files:** `backend/intelligence/stages/__init__.py`, `backend/intelligence/stages/intelligence_stage.py`

---

## Overview

`IntelligenceStage` is a `PipelineStage` subclass that bridges the Service Execution Pipeline with the AI Execution Engine. It contains no business logic, no provider knowledge, and no database access.

---

## Class Definition

```python
class IntelligenceStage(PipelineStage):
    priority: int = 500
    name: str = "IntelligenceStage"

    def __init__(self, engine: AIExecutionEngine | None = None) -> None: ...
    def execute(self, context: PipelineContext) -> PipelineContext: ...
```

---

## Guard Logic

```
1. intelligence_enabled is False  →  return context unchanged (no-op)
2. intelligence_enabled is None AND ENABLE_AI=False  →  return context unchanged
3. Otherwise → proceed with AI execution
```

`intelligence_enabled=True` bypasses the stage-level flag check, allowing pipeline test scenarios to force execution regardless of the global setting.

---

## ExecutionContext Handling

| `context.intelligence_context` | Action |
|---|---|
| `isinstance(..., ExecutionContext)` | Reuse existing context |
| Anything else (None, string, other) | Create fresh `ExecutionContext(data=payload, metadata=metadata)` |

---

## AIRequest Construction

| AIRequest field | Source |
|---|---|
| `task` | `context.metadata.get("ai_task", "text")` |
| `execution_context` | Built or reused `ExecutionContext` |
| `payload` | `context.payload` |
| `metadata` | `context.metadata` |
| `options` | `context.metadata.get("ai_options")` |

---

## Pipeline Priority

`priority = 500` — runs before the `_HandlerStage` at priority 1000 in `BaseService.execute()`. This means intelligence enrichment occurs before domain business logic in the current pipeline ordering. This may need to be revisited in Sprint 3B.9 depending on whether enrichment should precede or follow domain handlers.

---

## Immutability

`PipelineContext` is frozen. `IntelligenceStage` only calls `context.with_updates(intelligence_context=result)` — it never mutates existing fields. The original context is returned unchanged when the stage is skipped.

---

## Test Coverage

- 34 tests across 8 classes
- **100% statement coverage**
- Covers: construction, context disable guard, feature flag guard, ExecutionContext create/reuse, successful execution, engine failure containment, pipeline propagation, immutability, determinism
