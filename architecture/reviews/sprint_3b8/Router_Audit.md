# Router Audit

**Date:** 2026-07-01  
**Sprint:** 3B.8 Discovery

---

## Current State

An AI provider `Router` **does not exist** in the codebase.

The `intelligence/providers/registry.py` singleton (`_registry`) provides the lookup mechanism but no routing logic. There is a separate `apps/common/pipeline/registry.py` (`PipelineRegistry`) that routes service operations to handlers — this is a **completely different** registry with no connection to AI provider selection.

---

## Proposed Design

### Location

```
backend/intelligence/router.py
```

### Responsibilities

1. Accept task metadata from an `AIRequest`.
2. Query the provider registry for capable providers.
3. Apply the selection strategy.
4. Return the selected provider **class** (not instance).

### Interface (proposed)

```python
class Router:
    def __init__(self, registry: ProviderRegistry | None = None) -> None: ...
    def select(self, request: AIRequest) -> type[AIProvider]: ...
```

### Selection Strategy (proposed: capability-first, priority-ordered)

```
1. task = request.task
2. candidates = [p for p in _registry.list() if p().supports(task)]
3. if candidates: return candidates[0]   (lowest priority value = highest priority)
4. else: return _registry.default()      (fallback to first registered)
5. if no providers at all: raise RuntimeError("No provider registered")
```

### Constraints

- No HTTP calls.
- No randomness.
- Must be testable with a fresh `ProviderRegistry` instance (isolation).
- Selection must be deterministic for a given registry state.

---

## Interaction with AIExecutionEngine

```python
class AIExecutionEngine:
    def __init__(self, router: Router) -> None:
        self._router = router

    def execute(self, request: AIRequest) -> AIResponse:
        provider_cls = self._router.select(request)
        provider = provider_cls()
        return provider.execute(request)
```

---

## Known Registry State

At Sprint 3B.7 completion, the global registry contains:

| Name | Capabilities | Priority |
|---|---|---|
| `dummy` | text, chat | 0 |
| `echo` | text | 0 |
| `mock` | text, chat, structured_output | 0 |

All three share priority 0. For the same task, selection order follows insertion order: `dummy` → `echo` → `mock`.

---

## Distinction from PipelineRegistry

| | AI Router / ProviderRegistry | PipelineRegistry |
|---|---|---|
| File | `intelligence/providers/registry.py` | `apps/common/pipeline/registry.py` |
| Purpose | Select AI provider for a request | Map operation name → service handler |
| Status | ✅ Functional | ❌ Syntax error — non-importable |
| Used by | AIExecutionEngine (proposed) | BaseService.execute() |
| Current defect | None | IndentationError at line 33 |

---

## Test Strategy

- Unit test routing with isolated `ProviderRegistry` instance.
- Test capability-based selection (task matches/mismatches).
- Test fallback when no capable provider.
- Test empty registry raises `RuntimeError` or returns `None`.
