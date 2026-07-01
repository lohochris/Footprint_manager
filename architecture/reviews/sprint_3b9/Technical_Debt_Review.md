# Technical Debt Review

**Date:** 2026-07-01
**Scope:** Sprint 3B.9 debt items carried from Sprint 3B.7 and Sprint 3B.8.

## IntelligenceStage Priority

Current state:

- `IntelligenceStage.priority = 500`.
- Pipeline sorts lower priority earlier.
- No domain handler stage is currently part of the same stage chain in reviewed code.

Risk:

- AI execution could run too early or too late once service operation stages are introduced.

Recommendation:

- Define intended ordering before changing priority.
- Suggested policy:
  - Validation stages before intelligence.
  - Business mutation stages before intelligence only if AI enriches post-mutation state.
  - Intelligence before reporting/audit stages if diagnostics should be recorded.

Sprint 3B.9 action:

- Add ordering documentation and focused tests.
- Avoid broad pipeline refactor.

## Router Fallback Behavior

Current state:

- If no provider supports a task, router returns registry default.

Risk:

- A provider can execute a task it does not support.

Recommendation:

- Replace silent fallback with explicit policy.
- Default to fail closed for unsupported tasks.

Priority:

- High.

## `health_check()` Interface

Current state:

- Base provider contract says `Dict[str, Any]`.
- Concrete providers return `HealthStatus`.

Risk:

- Type checkers and future implementations may diverge.
- Health policy cannot rely on a stable contract.

Recommendation:

- Standardize on a structured health result.
- Update docs/tests together during implementation.

Priority:

- High.

## Registry Thread Safety

Current state:

- `ProviderRegistry` stores classes in a mutable dict.
- Global singleton is mutable.
- No lock protection exists.

Risk:

- Concurrent registration/unregistration could cause race conditions.
- Runtime mutation could affect provider selection unpredictably.

Recommendation:

- Prefer registration during startup followed by freeze/read-only runtime behavior.
- If runtime mutation remains supported, protect mutations with a lock.

Priority:

- Medium.

## MyPy Environment Issue

Current state:

- Sprint certifications mention a `NewSemanalDjangoPlugin` crash.
- This appears to be infrastructure/tooling debt, not application architecture.

Risk:

- Static type verification may remain partially blocked.

Recommendation:

- Keep mypy troubleshooting separate from production architecture changes.
- Add a minimal isolated mypy config for `backend/intelligence` if needed.

Priority:

- Medium, but not blocking provider policy design.

## Legacy `apps.ai` Skeleton

Current state:

- `backend/apps/ai/*` contains an older abstract gateway/provider skeleton.
- Its comments name external providers and async retry expectations.
- The certified execution pipeline is under `backend/intelligence/*`.

Risk:

- Two AI abstractions can drift.
- Future developers may implement external providers in the wrong boundary.

Recommendation:

- Document `backend/intelligence/*` as the Sprint 3B execution path.
- Keep `backend/apps/ai/*` dormant unless a future migration plan is approved.
- Do not delete or rewrite it in Sprint 3B.9 unless explicitly approved.

Priority:

- Medium.

## Encoding/Mojibake

Current state:

- Several files and reports show mojibake in comments/docstrings.

Risk:

- Readability and generated docs quality suffer.

Recommendation:

- Avoid broad churn during Sprint 3B.9.
- Fix touched documentation as needed.
- Consider a separate encoding cleanup sprint.

Priority:

- Low.

## Summary Priority Order

1. Router fallback behavior.
2. Health contract alignment.
3. Execution diagnostics and failure classification.
4. Provider lifecycle state.
5. Registry thread safety or freeze semantics.
6. IntelligenceStage ordering and diagnostics propagation.
7. MyPy environment isolation.
8. Encoding cleanup.
