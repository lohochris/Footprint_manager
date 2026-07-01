# Execution Flow Report

**Date:** 2026-07-01  
**Sprint:** 3B.8 Discovery

---

## Target Flow (Sprint 3B.8 Objective)

```
Pipeline
  ↓
IntelligenceStage          (PipelineStage subclass — priority 500)
  ↓
AIExecutionEngine          (orchestrator — backend/intelligence/engine.py)
  ↓
Router                     (provider selector — backend/intelligence/router.py)
  ↓
Provider Registry          (intelligence/providers/registry.py — _registry singleton)
  ↓
Provider (DummyProvider / MockProvider / EchoProvider)
  ↓
AIResponse                 (frozen dataclass — intelligence/providers/response.py)
  ↓
ExecutionResult            (frozen dataclass — apps/common/pipeline/core.py)
```

---

## Current Flow (Sprint 3B.7 State)

```
Pipeline([stages]).run(PipelineContext)
  ↓
PipelineStage.execute(context) → PipelineContext
  ↓
ExecutionResult(success, data, metadata, ...)
```

Intelligence layer exists but is never invoked. `PipelineContext.intelligence_enabled` and `intelligence_context` fields are present but always `None`.

---

## Component Existence Matrix

| Component | File | Exists |
|---|---|---|
| `Pipeline` | `apps/common/pipeline/core.py` | ✅ |
| `PipelineStage` | `apps/common/pipeline/core.py` | ✅ |
| `PipelineContext` | `apps/common/pipeline/core.py` | ✅ (with intelligence hooks) |
| `ExecutionResult` | `apps/common/pipeline/core.py` | ✅ |
| `IntelligenceStage` | — | ❌ To be created |
| `AIExecutionEngine` | — | ❌ To be created |
| `Router` | — | ❌ To be created |
| `ProviderRegistry` / `_registry` | `intelligence/providers/registry.py` | ✅ |
| `AIRequest` | `intelligence/providers/request.py` | ✅ |
| `AIResponse` | `intelligence/providers/response.py` | ✅ |
| `ExecutionContext` | `intelligence/context.py` | ✅ (minimal) |
| `ENABLE_AI` feature flag | `shared/constants/feature_flags.py` | ✅ |

---

## Proposed IntelligenceStage Flow

```python
class IntelligenceStage(PipelineStage):
    priority = 500
    name = "IntelligenceStage"

    def execute(self, context: PipelineContext) -> PipelineContext:
        # 1. Guard: feature flag
        if not is_feature_enabled(ENABLE_AI):
            return context

        # 2. Guard: explicitly disabled in context
        if context.intelligence_enabled is False:
            return context

        # 3. Build request from context
        request = AIRequest(
            task=context.metadata.get("ai_task", "text"),
            execution_context=context.intelligence_context,
            payload=context.payload,
            metadata=context.metadata,
        )

        # 4. Execute via engine
        engine = AIExecutionEngine(router=Router())
        response = engine.execute(request)

        # 5. Return updated context
        return context.with_updates(intelligence_context=response)
```

---

## Feature Flag Gate

The `ENABLE_AI` flag (`shared/constants/feature_flags.py`) is `False` by default:

```python
FEATURE_FLAGS = {
    "ENABLE_AI": env.bool("FEATURE_ENABLE_AI", default=False),
}
```

`IntelligenceStage` will check this flag first and return the context unchanged if the flag is disabled. This preserves the Sprint 0.1 guarantee that AI features cannot run without explicit configuration.

---

## Data Flow: AIRequest Construction

`PipelineContext` → `AIRequest`:

| AIRequest field | Source |
|---|---|
| `task` | `context.metadata.get("ai_task", "text")` |
| `execution_context` | `context.intelligence_context` |
| `payload` | `context.payload` |
| `metadata` | `context.metadata` |
| `options` | `context.metadata.get("ai_options")` (optional) |

---

## Data Flow: AIResponse Integration

`AIResponse` → `PipelineContext` → `ExecutionResult`:

| AIResponse field | Destination |
|---|---|
| `status` | `context.intelligence_context.status` |
| `output` | `ExecutionResult.data` or `context.metadata["ai_output"]` |
| `metadata` | `context.metadata["ai_metadata"]` |
| `diagnostics` | `context.metadata["ai_diagnostics"]` (if present) |

---

## No Business-Layer Changes Required

The Sprint 3B.8 flow is entirely within the `intelligence/` package and the pipeline infrastructure. It does not require changes to:

- Business services (`apps/investigations/`, `apps/organizations/`, etc.)
- Serializers
- Models or migrations
- Repositories/selectors
- API viewsets
- URL routing
- Frontend
- Sprint 3A code
