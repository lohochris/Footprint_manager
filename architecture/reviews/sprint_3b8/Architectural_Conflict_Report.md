# Architectural Conflict Report

**Date:** 2026-07-01  
**Sprint:** 3B.8 Discovery

---

## Summary

**One pre-existing defect was discovered during Sprint 3B.8 Discovery.**

This defect does NOT block Sprint 3B.8 implementation. It is documented here for visibility and tracking.

---

## CONFLICT-01 — PipelineRegistry Syntax Error

**Severity:** High  
**Type:** Pre-existing defect (not introduced by Sprint 3B.7 or 3B.8)  
**File:** `backend/apps/common/pipeline/registry.py`  
**Line:** 33  
**Error:** `IndentationError: unexpected indent`

### Description

Workspace service registration code was inserted at module level inside what should be the `PipelineRegistry` class body:

```python
class PipelineRegistry:
    """docstring"""              ← class body ends here (implicitly)

# These lines are at module level:
from apps.organizations.services.workspace_service import WorkspaceService
PipelineRegistry.register('workspace.create', ...)
# ...

    _handlers: dict[str, Callable] = {}   ← IndentationError: unexpected indent
    
    @classmethod
    def register(cls, ...): ...
```

As a result:
1. `PipelineRegistry` class body contains only the docstring.
2. The class has no `_handlers`, no `register`, no `get_handler`, no `clear` methods.
3. The workspace registrations attempt to call `PipelineRegistry.register(...)` before the method exists.
4. The file fails `ast.parse()` — confirmed with `IndentationError` at line 33.

### Impact

| Consumer | Impact |
|---|---|
| `BaseService.execute()` | Cannot import `PipelineRegistry` — will raise `IndentationError` |
| Sprint 3B.8 (`AIExecutionEngine`, `Router`, `IntelligenceStage`) | **No impact** — uses `intelligence.providers.registry`, not `PipelineRegistry` |
| Provider Registry (`intelligence.providers.registry`) | **No impact** — entirely independent |
| Sprint 3B.7 providers | **No impact** |
| Django system check (`manage.py check`) | **No impact** — Django does not import this file during system checks |

### Why This Was Not Previously Caught

- Django system checks do not import service layer files.
- No existing test imports `PipelineRegistry` directly.
- The file is never imported by `INSTALLED_APPS` entry points.

### Required Fix

Restructure `registry.py` so that:
1. `_handlers` and all class methods are properly indented inside the `PipelineRegistry` class body.
2. Workspace service registrations are moved to AFTER the full class definition.
3. The file passes `ast.parse()`.

### Sprint 3B.8 Position

This defect is **not required to be fixed in Sprint 3B.8** unless a Sprint 3B.8 component needs to use `PipelineRegistry`. The AI execution path (`AIExecutionEngine → Router → ProviderRegistry`) is independent.

However, fixing the defect is **strongly recommended** to prevent `ImportError` from propagating when service tests are introduced. The fix is a pure refactor — no behaviour change.

**Recommendation:** Fix as a first step in Sprint 3B.8 or as a dedicated follow-up task before any service integration work.

---

## No Other Conflicts Found

The following areas were inspected and confirmed clean:

| Area | Status |
|---|---|
| `AIProvider` ABC (`base.py`) | ✅ No conflict |
| Provider registry (`intelligence/providers/registry.py`) | ✅ No conflict |
| `AIRequest` / `AIResponse` | ✅ No conflict |
| `PipelineContext` / `ExecutionResult` | ✅ No conflict |
| `ExecutionContext` | ✅ No conflict |
| Feature flags (`ENABLE_AI`) | ✅ No conflict |
| Sprint 3B.7 test suite | ✅ No conflict |
| Sprint 3A baseline | ✅ No conflict |
