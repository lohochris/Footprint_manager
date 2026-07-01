# Sprint 3B.9 Discovery Report

**Date:** 2026-07-01
**Sprint:** 3B.9 - Provider Lifecycle and Execution Policy Framework
**Phase:** Discovery and Architecture Validation
**Scope:** Documentation only. No production code changes.

## Executive Summary

Sprint 3B.8 delivered a working offline execution chain:

`IntelligenceStage -> AIExecutionEngine -> Router -> ProviderRegistry -> Provider -> AIResponse -> ExecutionResult`

The current implementation is deterministic and fully offline, but it remains minimal. Production readiness now depends on making provider lifecycle, health validation, execution policy, diagnostics, and routing semantics explicit before adding more providers or richer execution behavior.

The discovery conclusion is that Sprint 3B.9 should introduce framework-level contracts only. It should not modify business services, serializers, models, repositories, external provider integrations, SDK clients, HTTP clients, API keys, vector stores, or external AI dependencies.

## Current Architecture Reviewed

Reviewed modules:

- `backend/intelligence/providers/base.py`
- `backend/intelligence/providers/provider_metadata.py`
- `backend/intelligence/providers/registry.py`
- `backend/intelligence/providers/dummy_provider.py`
- `backend/intelligence/providers/echo_provider.py`
- `backend/intelligence/providers/mock_provider.py`
- `backend/intelligence/router.py`
- `backend/intelligence/engine.py`
- `backend/intelligence/stages/intelligence_stage.py`
- `backend/intelligence/context.py`
- `backend/apps/common/pipeline/core.py`
- `backend/apps/common/pipeline/factory.py`
- `backend/apps/common/pipeline/registry.py`
- `backend/shared/constants/feature_flags.py`
- Sprint 3B.7 and Sprint 3B.8 test and certification reports

## Provider Lifecycle Findings

The provider contract currently exposes `initialize()`, `health_check()`, `capabilities()`, `supports()`, and `execute()`.

Findings:

- Initialization exists but is not called by the engine or router.
- Shutdown or disposal is not represented.
- Health exists but is not part of routing or execution validation.
- Readiness and availability are not distinct concepts.
- Registration is class-based and deterministic, but not thread-safe.
- Providers are instantiated ad hoc by the router for `supports()` checks and by the engine for execution.
- Provider state is effectively assumed to be stateless, lightweight, and safe to instantiate repeatedly.

Recommended target:

- Keep providers offline and deterministic.
- Add explicit lifecycle state without introducing external providers.
- Separate registration, initialization, health, readiness, availability, execution, and shutdown.
- Prefer class registration for now, but define whether future lifecycle state belongs in provider instances or a provider runtime wrapper.

## Execution Policy Findings

The engine currently applies only:

- Feature flag gate.
- Dry-run short-circuit.
- Router selection.
- Provider execution.
- Exception-to-`ExecutionResult` mapping.

Missing policy concepts:

- Health-check policy.
- Timeout policy.
- Retry policy architecture.
- Fallback policy.
- Provider selection policy.
- Failure classification.
- Diagnostics collection.
- Cancellation points.

Recommended target:

- Add a policy layer between `IntelligenceStage` and `Router`.
- Policy should be data-only or deterministic service logic.
- Retry should be modeled but disabled for now.
- Timeout should be measured/classified architecturally, not implemented with network or async primitives yet unless local execution requires it.

## Router Findings

The router currently supports:

- Explicit provider through `request.metadata["provider"]`.
- Capability-first selection.
- Default fallback when no provider supports a task.

Production concerns:

- Explicit provider currently behaves like "required provider" for unknown names, but bypasses capability checks for known names.
- Silent fallback to registry default can execute an unsupported task with a provider that does not claim support.
- No health or availability filtering exists.
- No distinction exists between preferred, required, and fallback providers.
- No diagnostics are returned from routing.

Recommended target:

- Support separate `preferred_provider`, `required_provider`, and `fallback_provider` semantics.
- Preserve backwards compatibility with `metadata["provider"]` initially by treating it as `required_provider`.
- Replace silent default fallback with policy-controlled fallback.
- Return selection diagnostics or attach them through the engine.

## AIExecutionEngine Findings

Current behavior:

- Always returns `ExecutionResult`.
- Prevents provider exceptions from escaping.
- Measures total execution time.
- Maps routing failure to 503.
- Maps provider exception to 500.
- Maps provider error response to 502.

Gaps:

- Does not call `initialize()`.
- Does not call `health_check()`.
- Does not classify failures beyond broad routing/provider categories.
- Does not collect per-phase timings.
- Does not expose policy hooks.
- Does not support cancellation checkpoints.
- Dry-run skips routing and provider execution entirely, so it does not validate policy or selection.

Recommended target:

- Define execution phases: flag gate, dry-run handling, policy build, health validation, routing, provider lifecycle, execution, diagnostics mapping, result mapping.
- Add diagnostics to `ExecutionResult.metadata`.
- Keep exceptions contained.
- Keep dry-run deterministic, but decide whether it should validate policy and routing in a future test mode.

## IntelligenceStage Findings

Current behavior:

- Priority is `500`.
- Context-level `intelligence_enabled=False` skips execution.
- `intelligence_enabled=True` bypasses the stage feature-flag check, but the engine still checks `ENABLE_AI`.
- Creates or reuses `ExecutionContext`.
- Builds `AIRequest` from pipeline payload and metadata.
- Attaches engine `ExecutionResult` to `PipelineContext.intelligence_context`.

Gaps:

- Stage priority is not validated against future domain handler ordering.
- The outer `Pipeline.run()` result does not include `intelligence_context`; it returns `data=context.payload` and `metadata=context.metadata`.
- Pipeline compatibility is acceptable for side-channel enrichment, but not sufficient if consumers need AI diagnostics from the final `Pipeline.run()` result.
- Context propagation is shallow and uses mutable dict copies.

Recommended target:

- Keep `IntelligenceStage` isolated from provider details.
- Treat policy configuration as metadata-derived or constructor-injected, not business-service driven.
- Decide whether the final pipeline result should surface intelligence diagnostics through metadata.

## Technical Debt Revisited

| Debt | Current Status | Sprint 3B.9 Recommendation |
|---|---|---|
| `IntelligenceStage.priority` | Hardcoded at `500`; ordering implications unresolved | Document intended stage ordering and add tests before changing |
| Router fallback behavior | Silent default fallback for unsupported tasks | Replace with explicit policy-controlled fallback |
| `health_check()` interface | Base says `Dict[str, Any]`; providers return `HealthStatus` | Align contract to a single health model |
| Registry thread safety | Plain dict with mutable global singleton | Add locking or freeze-after-startup semantics |
| MyPy environment issue | Reported `NewSemanalDjangoPlugin` crash | Keep separate from production architecture; verify with isolated config later |
| Encoding/mojibake in docs/comments | Present in several files/reports | Non-blocking; avoid broad churn in Sprint 3B.9 |

## Architecture Validation

Target future flow:

```text
Pipeline
    -> IntelligenceStage
    -> Execution Policy
    -> Health Check
    -> Router
    -> Provider
    -> Diagnostics
    -> ExecutionResult
```

Validation result:

- No business service changes are required.
- No serializer changes are required.
- No model changes are required.
- No repository changes are required.
- Sprint 3A guarantees can remain intact if pipeline core changes are avoided or strictly additive.
- Sprint 3B.7 guarantees can remain intact if provider metadata and offline reference providers remain deterministic.
- Sprint 3B.8 guarantees can remain intact if the engine continues returning `ExecutionResult` and provider exceptions never escape.

## Architectural Conflicts

One conflict was identified and documented separately:

- `backend/apps/ai/*` contains an older AI gateway/provider skeleton that names external provider concepts, while the certified Sprint 3B.7/3B.8 execution path lives under `backend/intelligence/*` and must remain offline.

See `Architectural_Conflict_Report.md`.

## Recommended Sprint 3B.9 Implementation Order

1. Align health model contracts.
2. Define lifecycle states and provider lifecycle boundaries.
3. Add diagnostics data structures and failure classification.
4. Introduce execution policy data model with retries disabled.
5. Update router selection semantics for required, preferred, and fallback provider behavior.
6. Integrate health validation into the engine before provider execution.
7. Add timing collection per execution phase.
8. Add cancellation checkpoints as no-op deterministic hooks.
9. Revisit `IntelligenceStage` priority and final diagnostics propagation.
10. Add regression tests for Sprint 3A, 3B.7, and 3B.8 guarantees.

## Stop Condition

Discovery reports have been generated. Production code should not be written until Sprint 3B.9 implementation is explicitly approved.
