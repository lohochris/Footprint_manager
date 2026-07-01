# Sprint 3B.9 Step 1 Engineering Report

**Date:** 2026-07-01
**Step:** Execution Policy Foundation
**Status:** Implemented

## Objective

Create the execution policy foundation and align the provider health contract without introducing external providers, networking, retries, health-aware routing, or provider lifecycle state management.

## Code Changes

Added:

- `backend/intelligence/policies/__init__.py`
- `backend/intelligence/policies/execution_policy.py`
- `backend/intelligence/policies/policy_builder.py`
- `backend/tests/test_sprint_3b9_step1_policy.py`

Updated:

- `backend/intelligence/providers/base.py`

## ExecutionPolicy

Implemented `ExecutionPolicy` as a frozen dataclass.

Fields:

- `required_provider`
- `preferred_provider`
- `fallback_provider`
- `fallback_mode`
- `selection_strategy`
- `retry_enabled`
- `max_attempts`
- `timeout_seconds`
- `health_required`
- `diagnostics_enabled`
- `dry_run`

The class contains no execution logic, provider selection, retries, routing, health checks, networking, or side effects.

## ExecutionPolicyBuilder

Implemented deterministic policy construction from:

- `AIRequest.metadata`
- `AIRequest.options`
- optional defaults
- feature flag snapshot

Behavior:

- Copies request metadata/options before inspection.
- Maps legacy `metadata["provider"]` to `required_provider`.
- Allows explicit `required_provider` to override legacy `provider`.
- Lets metadata override options.
- Normalizes retry, timeout, diagnostics, health, fallback, selection, and dry-run fields.
- Validates fallback mode and selection strategy.
- Keeps retries disabled by default and forces `max_attempts=1` when retry is disabled.
- Performs no provider selection, provider execution, health checks, network calls, or external AI integration.

## Health Contract Alignment

Updated `AIProvider.health_check()` to officially return `HealthStatus`.

No runtime behavior changed:

- `DummyProvider.health_check()` already returned `HealthStatus`.
- `EchoProvider.health_check()` already returned `HealthStatus`.
- `MockProvider.health_check()` already returned `HealthStatus`.

Provider behavior remains deterministic, offline, side-effect free, and unchanged.

## Explicit Non-Changes

No changes were made to:

- Business services.
- Serializers.
- Repositories.
- Models.
- Migrations.
- `IntelligenceStage`.
- `Router`.
- `AIExecutionEngine`.
- External AI providers.
- HTTP clients.
- SDKs.
- API keys.
- Retry execution.
- Health-aware routing.
- Provider lifecycle state management.

## Test Coverage Added

Added 30 dedicated Step 1 tests covering:

- ExecutionPolicy defaults.
- Immutability.
- Absence of execution methods on policy data.
- Builder defaults.
- Metadata mapping.
- Backward-compatible `provider` mapping.
- Required-provider precedence.
- Options support.
- Metadata-over-options precedence.
- Retry architecture defaults.
- Timeout normalization.
- Validation failures.
- Dry-run normalization.
- Diagnostics flag mapping.
- Feature-flag effect on `health_required`.
- Request metadata immutability.
- Base provider health contract return type.
- Offline provider compatibility.

## Regression Validation

Targeted Sprint 3B regression suite passed:

- Sprint 3B.7 provider tests.
- Sprint 3B.8 router tests.
- Sprint 3B.8 engine tests.
- Sprint 3B.8 stage tests.
- Sprint 3B.9 Step 1 policy tests.

Result:

- `274 passed`

## Technical Debt Identified

Tooling/environment debt:

- Exact `cd backend; pytest` fails before collection due import path resolution: `ModuleNotFoundError: No module named 'backend'`.
- Full collection via repo-root targeted paths exposes existing duplicate model import conflict between `backend.apps...` and `apps...`.
- Exact `ruff check .` fails because root `ruff.toml` uses `[tool.ruff]`, which is invalid in standalone `ruff.toml`.
- Exact `mypy .` hits the known `NewSemanalDjangoPlugin` internal error.
- Exact `bandit -r .` scans tests and reports many existing assert/test-secret findings.
- `.pytest_cache` under `backend` reports permission warnings.

Step 1 code-specific checks passed with corrective commands:

- Step 1 focused tests passed.
- Sprint 3B regression tests passed.
- Scoped Ruff passed using `pyproject.toml`.
- Plugin-free scoped MyPy passed.
- Corrective coverage run passed.

## Stop Condition

Step 1 is complete. Do not proceed to Step 2 until approved.
