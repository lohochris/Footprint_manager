# Sprint 3B.7 — Provider Registry Report

**Date:** 2026-07-01

---

## Registry Architecture

The registry (`ProviderRegistry`) is a module-level singleton defined in `registry.py`. It was implemented in Sprint 3A and is unchanged by Sprint 3B.7.

### API Surface

| Method | Signature | Behaviour |
|---|---|---|
| `register` | `(provider: Type[AIProvider]) -> None` | Stores class under its `name` attribute (or class name). Raises `ValueError` on duplicate. |
| `unregister` | `(name: str) -> None` | Silent no-op if name absent. |
| `get` | `(name: str) -> Optional[Type[AIProvider]]` | Returns class or `None`. |
| `list` | `() -> List[Type[AIProvider]]` | All classes ordered by `priority` attribute (asc, default 0). |
| `default` | `() -> Optional[Type[AIProvider]]` | First entry from `list()`, or `None`. |
| `capabilities` | `(name: str) -> List[str]` | Instantiates the class (no-arg) and calls `.capabilities()`. Raises `KeyError` if unknown. |

Convenience module-level wrappers: `register_provider`, `unregister_provider`, `get_provider`, `list_providers`.

---

## Registered Providers (Post Sprint 3B.7)

| Name | Class | Priority | Registration point |
|---|---|---|---|
| `"dummy"` | `DummyProvider` | 0 (default) | `dummy_provider.py` module bottom |
| `"echo"` | `EchoProvider` | 0 (default) | `echo_provider.py` module bottom |
| `"mock"` | `MockProvider` | 0 (default) | `mock_provider.py` module bottom |

**Registration order** (insertion order, all priority 0): `dummy` → `echo` → `mock`  
This matches the alphabetical import order in `__init__.py` (`dummy_provider` → `echo_provider` → `mock_provider`).

---

## Registration Mechanics

All three providers self-register via a module-level `register_provider()` call at the bottom of their respective files — the same pattern DummyProvider used in Sprint 3A. Registration is triggered when:

1. A provider module is imported directly (e.g., `import intelligence.providers.dummy_provider`).
2. The package is imported (e.g., `from intelligence.providers import DummyProvider`) — because `__init__.py` imports all three provider modules.

Python's module cache (`sys.modules`) ensures each provider registers exactly once per process.

---

## Duplicate-Registration Protection

```python
# Attempting to register the same provider twice:
register_provider(DummyProvider)  # → ValueError: Provider 'dummy' is already registered.
```

Verified by test `TestGlobalRegistry::test_duplicate_registration_still_rejected_globally`.

---

## Thread Safety

The backing store is a plain `dict`. Concurrent `register` calls in multi-threaded environments are not protected. This is unchanged from Sprint 3A and is acceptable for the current single-threaded Django WSGI deployment model.

---

## Registry Capability Lookup

`registry.capabilities(name)` instantiates the provider class with no arguments and calls `.capabilities()`. This requires:

1. All registered providers have a no-argument constructor (or all arguments optional).
2. `capabilities()` is side-effect free.

All three Sprint 3B.7 providers satisfy both requirements:
- `DummyProvider()` — no constructor, default Python `__init__`.
- `EchoProvider()` — no constructor, default Python `__init__`.
- `MockProvider()` — `scenario` argument defaults to `MockScenario.SUCCESS`.

---

## Known Limitation

`registry.capabilities()` instantiates the class on every call. For providers with expensive constructors, this is inefficient. Sprint 3B.8+ may wish to cache the result or use class-level capability introspection via `ProviderCapabilities`.
