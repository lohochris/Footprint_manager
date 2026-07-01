# backend/intelligence/engine.py
"""AI Execution Engine.

Orchestrates provider selection and execution for an incoming AIRequest.
Returns an ExecutionResult in all cases — exceptions never escape this module.
No HTTP calls, no external SDKs, no network access.
"""

from __future__ import annotations

import logging
import time

from apps.common.pipeline.core import ExecutionResult
from intelligence.providers.request import AIRequest
from intelligence.router import NoProviderAvailableError, ProviderNotFoundError, Router
from shared.constants.feature_flags import ENABLE_AI, is_feature_enabled

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
                metadata={"ai_enabled": False},
                execution_time=time.monotonic() - start,
                status_code=503,
            )

        # ── 2. Dry-run short-circuit ────────────────────────────────────
        if dry_run:
            return ExecutionResult(
                success=True,
                data=None,
                error=None,
                metadata={"dry_run": True, "task": request.task},
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
                metadata={"task": request.task},
                execution_time=time.monotonic() - start,
                status_code=503,
            )

        # ── 4. Provider execution ───────────────────────────────────────
        provider_name: str = getattr(provider_cls, "name", provider_cls.__name__)
        try:
            provider = provider_cls()
            response = provider.execute(request)
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Provider '%s' raised an exception for task '%s': %s",
                provider_name, request.task, exc,
                exc_info=True,
            )
            return ExecutionResult(
                success=False,
                data=None,
                error=exc,
                metadata={"provider": provider_name, "task": request.task},
                execution_time=time.monotonic() - start,
                status_code=500,
            )

        # ── 5. Map AIResponse → ExecutionResult ────────────────────────
        succeeded = response.status == "success"
        return ExecutionResult(
            success=succeeded,
            data=response,
            error=None if succeeded else response.diagnostics,
            metadata={"provider": provider_name, "task": request.task},
            execution_time=time.monotonic() - start,
            status_code=200 if succeeded else 502,
        )
