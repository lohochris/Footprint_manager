# Sprint 3B.8 — Discovery Report

**Date:** 2026-07-01  
**Phase:** Discovery (No Code Changes)  
**Scope:** AIExecutionEngine integration with completed provider architecture

---

## Executive Summary

Sprint 3B.8 Discovery has been completed. The pipeline infrastructure is solid and provides clear extension points for AI integration. Three new components need to be created from scratch (`AIExecutionEngine`, `Router`, `IntelligenceStage`). One pre-existing defect was discovered in `PipelineRegistry` (syntax error) that does not block the Sprint 3B.8 integration path but must be documented and tracked.

**Sprint 3B.8 is safe to implement with the architecture described in this report.**

---

## 1. AIExecutionEngine

**Status: Does not exist.**

No `AIExecutionEngine` class exists anywhere in the codebase. It must be created in Sprint 3B.8. It will live in `backend/intelligence/` and will:

- Accept an `AIRequest`
- Delegate to a `Router` for provider selection
- Return an `AIResponse`
- Contain no HTTP, no SDK calls, no randomness

Extension point: `PipelineContext.intelligence_context` is available to carry the `AIResponse` back through the pipeline.

---

## 2. Router

**Status: Does not exist.**

No AI provider router exists. The `intelligence.providers.registry` singleton contains the registered providers (`dummy`, `echo`, `mock`). The Router will:

- Accept task metadata from `AIRequest`
- Query the registry for a capable provider
- Return the selected provider class
- Apply selection strategy (capability-based, priority-based, or name-based)

Note: The Django-level `PipelineRegistry` (at `apps/common/pipeline/registry.py`) is a separate, unrelated component and is **not** the provider registry. See Section 13 for the defect found in that file.

---

## 3. Provider Registry State

**Status: Fully operational.**

```
Registered providers (insertion order, all priority=0):
  "dummy"  →  DummyProvider   (text, chat)
  "echo"   →  EchoProvider    (text)
  "mock"   →  MockProvider    (text, chat, structured_output)
```

All three providers register at module-import time. The registry is populated when `intelligence.providers` is first imported.

---

## 4. Provider Selection Workflow

**Status: Not implemented — to be built.**

Proposed selection flow for the Router:

1. `AIRequest.task` → capability name (e.g., `"text"`)
2. Router queries `_registry.list()` for all providers
3. Filters to providers where `provider_cls().supports(task)` is `True`
4. Returns the highest-priority capable provider
5. Falls back to `_registry.default()` if no match

---

## 5. ExecutionResult Structure

**Status: Exists — fully functional.**

```python
@dataclass(frozen=True)
class ExecutionResult:
    success: bool
    data: Any = None
    error: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    status_code: int = 200
```

`AIResponse` from a provider execution will be surfaced through `ExecutionResult.data` or `ExecutionResult.metadata` depending on the design decision for `IntelligenceStage`.

---

## 6. ExecutionContext Propagation

**Status: Minimal implementation exists — extension needed.**

`intelligence/context.py` defines:

```python
@dataclass(frozen=True)
class ExecutionContext:
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

`PipelineContext` carries two intelligence-related fields (added ahead of this sprint):

```python
intelligence_enabled: bool | None = None   # gate for AI execution
intelligence_context: Any = None           # carrier for AI result
```

The `intelligence_context` field will hold the `ExecutionContext` or `AIResponse` as it flows through the pipeline.

---

## 7. IntelligenceStage Integration

**Status: Does not exist — to be built.**

`IntelligenceStage` will be a `PipelineStage` subclass that:

1. Reads `context.intelligence_enabled` (or checks `is_feature_enabled(ENABLE_AI)`)
2. Builds an `AIRequest` from `context.payload` and `context.metadata`
3. Calls `AIExecutionEngine.execute(request)`
4. Returns `context.with_updates(intelligence_context=response)`
5. On failure: returns the context with error captured (does not raise)

---

## 8. Dry-Run Workflow

**Status: No dry-run mechanism exists anywhere.**

The Sprint 3B.8 prompt mentions dry-run compatibility. Nothing in the current codebase implements dry-run behaviour. The `PipelineContext` has no `dry_run` field. If dry-run is required, `IntelligenceStage` should check for a `dry_run` flag in `context.metadata` and short-circuit execution.

---

## 9. Error Propagation Strategy

**Status: Defined by Pipeline infrastructure.**

The existing `Pipeline.run()` catches all exceptions from stages:

```python
except Exception as exc:
    return ExecutionResult(
        success=False,
        data=None,
        error=exc,
        metadata=context.metadata,
        status_code=500,
    )
```

`IntelligenceStage` must NOT raise unhandled exceptions — it must represent provider failures as structured `AIResponse` objects (e.g., `status="error"`) or let the Pipeline catch them and return `ExecutionResult(success=False, ...)`.

---

## 10. Feature Flag Usage

**Status: ENABLE_AI flag exists and is False by default.**

```python
ENABLE_AI = "ENABLE_AI"
# settings.FEATURE_FLAGS["ENABLE_AI"] = env.bool("FEATURE_ENABLE_AI", default=False)
```

`IntelligenceStage` must check `is_feature_enabled(ENABLE_AI)` before executing. If the flag is `False`, the stage should be a no-op (pass context through unchanged).

This preserves the Sprint 0.1 guarantee: AI features are disabled by default and cannot run unless explicitly enabled.

---

## 11. Existing Execution Lifecycle

The current lifecycle for a pipeline operation is:

```
BaseService.execute(operation, performed_by, tenant, payload, metadata)
  ↓
PipelineRegistry.get_handler(operation)       ← DEFECT: see Section 13
  ↓
PipelineContext(performed_by, tenant, payload, metadata)
  ↓
Pipeline([_HandlerStage]).run(context)
  ↓
ExecutionResult(success, data, error, metadata, execution_time, status_code)
```

The AI-enriched lifecycle will be:

```
Pipeline([..., IntelligenceStage(priority=500), ...]).run(context)
  ↓
IntelligenceStage
  ↓
AIExecutionEngine.execute(AIRequest)
  ↓
Router.select(task, registry)
  ↓
provider.execute(request) → AIResponse
  ↓
context.with_updates(intelligence_context=response)
  ↓
ExecutionResult(success=True, data=context.payload, metadata={..., "ai_response": ...})
```

---

## 12. Architectural Extension Points

| Extension Point | Location | Ready |
|---|---|---|
| `PipelineContext.intelligence_enabled` | `pipeline/core.py:32` | ✅ |
| `PipelineContext.intelligence_context` | `pipeline/core.py:33` | ✅ |
| `ProviderRegistry._registry` | `intelligence/providers/registry.py` | ✅ |
| `ENABLE_AI` feature flag | `shared/constants/feature_flags.py` | ✅ |
| `AIRequest` / `AIResponse` frozen dataclasses | `intelligence/providers/request.py`, `response.py` | ✅ |
| `ExecutionContext` in `intelligence/context.py` | `intelligence/context.py` | ✅ (minimal) |

---

## 13. Defects Discovered

### DEFECT-01 — PipelineRegistry Syntax Error (IndentationError)

**File:** `backend/apps/common/pipeline/registry.py`  
**Severity:** High  
**Type:** Pre-existing syntax error

**Description:** Workspace service registration code was inserted between the `PipelineRegistry` class docstring and the class body attributes (`_handlers`, `register`, `get_handler`, `clear`). The result is that the class body contains only the docstring. `_handlers` and all methods are at indented module level AFTER unindented module-level import/call statements — which Python rejects with `IndentationError: unexpected indent`.

**Confirmed:** `ast.parse()` raises `IndentationError` at line 33.

**Impact on Sprint 3B.8:** The `AIExecutionEngine` / `Router` / `IntelligenceStage` components use the **provider registry** (`intelligence.providers.registry`), not `PipelineRegistry`. **This defect does not block Sprint 3B.8 implementation.**

However, `BaseService.execute()` (in `base_service.py`) imports and uses `PipelineRegistry`. Any service that uses `BaseService.execute()` will fail to import.

**Corrective Action Required:** Repair the indentation in `registry.py` in a dedicated fix sprint or as part of Sprint 3B.8 scope. See `Architectural_Conflict_Report.md`.

---

## 14. Conflicts with Sprint 3B.8 Objectives

**No architectural conflicts found.**

The provider architecture (Sprint 3B.7) and the pipeline infrastructure are fully compatible. The planned Sprint 3B.8 integration flow is achievable without modifying any existing interface.

The `PipelineRegistry` defect is a pre-existing issue that affects a different code path and does not conflict with the AI integration objective.
