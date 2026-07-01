# AIExecutionEngine Report

**Date:** 2026-07-01  
**Sprint:** 3B.8  
**File:** `backend/intelligence/engine.py`

---

## Overview

`AIExecutionEngine` orchestrates provider selection and execution. It **never raises** — all failure modes are encoded in a returned `ExecutionResult`.

---

## Public API

```python
class AIExecutionEngine:
    def __init__(self, router: Router | None = None) -> None: ...
    def execute(self, request: AIRequest, *, dry_run: bool = False) -> ExecutionResult: ...
```

---

## Execution Order

```
1. Check ENABLE_AI feature flag → return failure ExecutionResult if False
2. If dry_run=True → return simulated success (no provider involved)
3. Router.select(request) → provider class
   └─ ProviderNotFoundError / NoProviderAvailableError → return failure ExecutionResult
4. provider_cls()  (instantiate)
5. provider.execute(request) → AIResponse
   └─ Any exception → return failure ExecutionResult
6. Map AIResponse.status → ExecutionResult.success / status_code
```

---

## Status Code Mapping

| Condition | status_code |
|---|---|
| `ENABLE_AI=False` | 503 |
| `dry_run=True` | 200 |
| Provider selection failure | 503 |
| Provider raised exception | 500 |
| Provider returned `status="error"` | 502 |
| Provider returned `status="success"` | 200 |

---

## Feature Flag Integration

`is_feature_enabled(ENABLE_AI)` is checked as the first guard. The import is patchable at `intelligence.engine.is_feature_enabled` for unit testing.

---

## Dry-Run Mode

When `dry_run=True`, the engine skips provider selection and execution entirely, returning:

```python
ExecutionResult(success=True, data=None, metadata={"dry_run": True, "task": request.task}, status_code=200)
```

---

## Error Containment

A broad `except Exception` (noqa BLE001) catches all provider exceptions. This is intentional — the engine is the last line of defence against uncaught provider crashes.

---

## Test Coverage

- 37 tests across 8 classes
- **100% statement coverage**
- Covers: construction, flag-disabled, dry-run, success, provider failure response, selection failure, provider exception, immutability, determinism
