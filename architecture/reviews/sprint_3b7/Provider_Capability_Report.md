# Sprint 3B.7 — Provider Capability Report

**Date:** 2026-07-01

---

## Capability Model

Capabilities are represented by `ProviderCapabilities`, a frozen dataclass of boolean flags. Each flag defaults to `False` (deny-by-default). Providers declare what they support at construction time by setting flags to `True`.

```
ProviderCapabilities
├── supports_text               bool  (default False)
├── supports_chat               bool  (default False)
├── supports_structured_output  bool  (default False)
├── supports_streaming          bool  (default False)
└── supports_embeddings         bool  (default False)
```

---

## Capability Matrix

| Provider | text | chat | structured_output | streaming | embeddings |
|---|:---:|:---:|:---:|:---:|:---:|
| `DummyProvider` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `MockProvider` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `EchoProvider` | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## Capability Derivation

Each provider implements `capabilities() -> list[str]` by iterating the `ProviderCapabilities` flags on its metadata and appending the string key for each `True` flag. This keeps the runtime capability list always consistent with the static metadata declaration.

```python
# Pattern used by all Sprint 3B.7 providers:
def capabilities(self) -> list[str]:
    caps = self.metadata.capabilities
    result: list[str] = []
    if caps.supports_text:            result.append("text")
    if caps.supports_chat:            result.append("chat")
    if caps.supports_structured_output: result.append("structured_output")
    if caps.supports_streaming:       result.append("streaming")
    if caps.supports_embeddings:      result.append("embeddings")
    return result
```

---

## Capability Lists

| Provider | `capabilities()` return value |
|---|---|
| `DummyProvider` | `["text", "chat"]` |
| `MockProvider` | `["text", "chat", "structured_output"]` |
| `EchoProvider` | `["text"]` |

---

## supports() Contract

`supports(task: str) -> bool` delegates to `capabilities()`:

```python
def supports(self, task: str) -> bool:
    return task in self.capabilities()
```

| Provider | `supports("text")` | `supports("chat")` | `supports("embeddings")` |
|---|:---:|:---:|:---:|
| `DummyProvider` | `True` | `True` | `False` |
| `MockProvider` | `True` | `True` | `False` |
| `EchoProvider` | `True` | `False` | `False` |

---

## Registry Integration

The registry exposes capability lookup via the singleton:

```python
from intelligence.providers.registry import _registry
_registry.capabilities("dummy")  # → ["text", "chat"]
_registry.capabilities("mock")   # → ["text", "chat", "structured_output"]
_registry.capabilities("echo")   # → ["text"]
```

---

## Design Notes

1. **Immutability:** `ProviderCapabilities` is frozen. A provider's declared capabilities cannot be changed after construction without creating a new provider class.
2. **Extensibility:** New capability flags can be added to `ProviderCapabilities` without breaking existing providers (new flags default to `False`).
3. **No capability-method pattern:** Sprint 3B.7 replaces the old `supports_text()`, `supports_chat()` etc. instance methods (which existed on the old `DummyProvider`) with the unified `ProviderCapabilities` model. The single source of truth is now the metadata object, not scattered instance methods.
