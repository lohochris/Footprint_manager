# Router Report

**Date:** 2026-07-01  
**Sprint:** 3B.8  
**File:** `backend/intelligence/router.py`

---

## Overview

`Router` selects an AI provider class for an incoming `AIRequest`. It contains no business logic, no HTTP calls, no SDKs, and no external dependencies.

---

## Public API

```python
class Router:
    def __init__(self, registry: ProviderRegistry | None = None) -> None: ...
    def select(self, request: AIRequest) -> type[AIProvider]: ...
```

---

## Exceptions

| Exception | When raised |
|---|---|
| `ProviderNotFoundError` | `request.metadata["provider"]` is set but the name is not registered |
| `NoProviderAvailableError` | Registry is empty or no provider can handle the task and no default exists |

---

## Selection Strategy

```
1. If request.metadata["provider"] is set → select by name (explicit)
2. Otherwise → filter by task capability (capability-first)
3. If no capable provider → fall back to registry default (first by priority)
4. If registry is empty → raise NoProviderAvailableError
```

---

## Behaviour with Global Registry

| Task | Selected Provider | Reason |
|---|---|---|
| `"text"` | `DummyProvider` | First provider (insertion order) supporting text |
| `"chat"` | `DummyProvider` | First provider supporting chat |
| `"structured_output"` | `MockProvider` | Only provider supporting structured_output |
| `"embeddings"` | `DummyProvider` | No capable provider; falls back to default |
| (explicit `"echo"`) | `EchoProvider` | Name match |

---

## Test Coverage

- 25 tests across 7 classes
- 100% statement coverage
- Covers: construction, explicit selection, capability selection, fallback, empty registry, error messages, return type validation

---

## Design Notes

- Returns a **class** (not instance): caller controls instantiation and constructor args.
- Accepts injectable `ProviderRegistry` for test isolation.
- Selection is deterministic for any given registry state.
