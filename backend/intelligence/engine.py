# backend/intelligence/engine.py
"""AI Execution Engine.

Orchestrates provider selection and execution for an incoming AIRequest.
Returns an ExecutionResult in all cases — exceptions never escape this module.
No HTTP calls, no external SDKs, no network access.
"""

from __future__ import annotations

import logging
import time

from backend.apps.common.pipeline.core import ExecutionResult
from backend.intelligence.providers.request import AIRequest
from backend.intelligence.router import NoProviderAvailableError, ProviderNotFoundError, Router
from backend.shared.constants.feature_flags import ENABLE_AI, is_feature_enabled

logger = logging.getLogger(__name__)


class AIExecutionEngine:
    """Orchestrates AI provider execution.

    Responsibilities:
    - Check the ``ENABLE_AI`` feature flag.
    - Support ``dry_run`` mode (skip provider execution).
    - Delegate provider selection to :class:`Router`.
    - Instantiate and execute the selected provider.
    - Convert provider failures into a structured :class:`ExecutionResult`.
    - Never let provider exceptions escape.

    Parameters
    ----------
    router:
        Provider selector.  Defaults to a fresh :class:`Router` backed by
        the global provider registry.
    """

    def __init__(self, router: Router | None = None) -> None:
        self._router: Router = router if router is not None else Router()
        from backend.intelligence.policies.policy_builder import ExecutionPolicyBuilder
        self._policy_builder = ExecutionPolicyBuilder()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def execute(
        self,
        request: AIRequest,
        *,
        dry_run: bool = False,
    ) -> ExecutionResult:
        """Execute *request* and return an :class:`ExecutionResult`.

        This method **always** returns an :class:`ExecutionResult` and
        **never** raises.  All failure modes are encoded in the returned
        object.

        Parameters
        ----------
        request:
            Immutable AI request to execute.  Not mutated by this method.
        dry_run:
            When ``True``, skip provider execution entirely and return a
            simulated success result.  Useful for pipeline testing.

        Returns
        -------
        ExecutionResult
            ``success=True`` on provider success; ``success=False`` on
            any failure (flag disabled, routing failure, provider error).
        """
        start = time.monotonic()

        # ── 1. Feature flag gate ────────────────────────────────────────
        if not is_feature_enabled(ENABLE_AI):
            return ExecutionResult(
                success=False,
                data=None,
                error="AI execution is disabled (ENABLE_AI=False).",
                metadata={"ai_enabled": False, "diagnostics": {"allowed": False, "reason": "AI execution disabled"}},
                execution_time=time.monotonic() - start,
                status_code=503,
            )

        # Build policy
        policy = self._policy_builder.build(request, dry_run=dry_run)

        # ── 2. Dry-run short-circuit ────────────────────────────────────
        if policy.dry_run:
            return ExecutionResult(
                success=True,
                data=None,
                error=None,
                metadata={"dry_run": True, "task": request.task, "diagnostics": {"allowed": True, "dry_run": True}},
                execution_time=time.monotonic() - start,
                status_code=200,
            )

        # ── 3. Provider selection ───────────────────────────────────────
        try:
            provider_cls = self._router.select(request)
        except (ProviderNotFoundError, NoProviderAvailableError) as exc:
            logger.warning("Provider selection failed for task '%s': %s", request.task, exc)
            return ExecutionResult(
                success=False,
                data=None,
                error=exc,
                metadata={"task": request.task, "diagnostics": {"allowed": False, "routing_error": str(exc)}},
                execution_time=time.monotonic() - start,
                status_code=503,
            )

        # ── 4. Provider Instantiation & Policy evaluation ────────────────
        provider_name: str = getattr(provider_cls, "name", provider_cls.__name__)
        try:
            provider = provider_cls()
        except Exception as exc:
            return ExecutionResult(
                success=False,
                data=None,
                error=exc,
                metadata={
                    "provider": provider_name,
                    "task": request.task,
                    "diagnostics": {"allowed": False, "instantiation_error": str(exc)},
                },
                execution_time=time.monotonic() - start,
                status_code=500,
            )

        from backend.intelligence.policy import PolicyEngine
        policy_engine = PolicyEngine()
        eval_res = policy_engine.evaluate(request, provider, policy)

        if not eval_res.allowed:
            return ExecutionResult(
                success=False,
                data=None,
                error=eval_res.reason,
                metadata={
                    "provider": provider_name,
                    "task": request.task,
                    "diagnostics": eval_res.diagnostics or {"allowed": False, "reason": eval_res.reason},
                },
                execution_time=time.monotonic() - start,
                status_code=400,
            )

        # ── 5. Provider execution with retries ──────────────────────────
        attempts = 0
        max_attempts = policy.max_attempts if policy.retry_enabled else 1
        last_exc = None
        response = None

        while attempts < max_attempts:
            attempts += 1
            try:
                response = provider.execute(request)
                if response.status == "success":
                    break
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                logger.error(
                    "Provider '%s' raised an exception for task '%s' (attempt %d/%d): %s",
                    provider_name, request.task, attempts, max_attempts, exc,
                    exc_info=True,
                )

        # ── 6. Map AIResponse → ExecutionResult ────────────────────────
        succeeded = response is not None and response.status == "success"
        diagnostics = {
            "allowed": True,
            "attempts": attempts,
            "provider": provider_name,
            "lifecycle_state": getattr(provider, "lifecycle_state", "active"),
            "healthy": True,
        }
        if not succeeded:
            error_val = response.diagnostics if response is not None else last_exc
            diagnostics["error"] = str(error_val)
            return ExecutionResult(
                success=False,
                data=response,
                error=error_val,
                metadata={
                    "provider": provider_name,
                    "task": request.task,
                    "diagnostics": diagnostics,
                },
                execution_time=time.monotonic() - start,
                status_code=502 if response is not None else 500,
            )

        return ExecutionResult(
            success=True,
            data=response,
            error=None,
            metadata={
                "provider": provider_name,
                "task": request.task,
                "diagnostics": diagnostics,
            },
            execution_time=time.monotonic() - start,
            status_code=200,
        )
