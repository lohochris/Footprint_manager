# backend/intelligence/stages/intelligence_stage.py
"""IntelligenceStage — pipeline integration for AI execution.

Bridges the Service Execution Pipeline with the AI Execution Engine.
Contains no business logic, no provider selection, no database access,
and no direct provider communication.
"""

from __future__ import annotations

from backend.apps.common.pipeline.core import PipelineContext, PipelineStage
from intelligence.context import ExecutionContext
from intelligence.engine import AIExecutionEngine
from intelligence.providers.request import AIRequest
from shared.constants.feature_flags import ENABLE_AI, is_feature_enabled


class IntelligenceStage(PipelineStage):
    """Integrates AI execution into a :class:`Pipeline` as a stage.

    Execution is governed by two independent guards, checked in order:

    1. **Context-level override** — ``context.intelligence_enabled``:
       - ``False``: stage is a guaranteed no-op (return context unchanged).
       - ``True``: skip the global feature-flag check and proceed.
       - ``None``: defer to the global ``ENABLE_AI`` feature flag.

    2. **Global feature flag** — ``ENABLE_AI`` (checked only when
       ``context.intelligence_enabled is None``):
       - ``False``: stage is a no-op for this execution.
       - ``True``: proceed with AI execution.

    When both guards allow execution the stage:
    - Reuses ``context.intelligence_context`` if it already holds an
      :class:`ExecutionContext`, otherwise creates a fresh one from the
      pipeline payload and metadata.
    - Constructs an :class:`AIRequest` and delegates to
      :class:`AIExecutionEngine`.
    - Returns a new :class:`PipelineContext` with
      ``intelligence_context`` set to the :class:`ExecutionResult`.

    The engine **never raises** — all failure modes are expressed as a
    failed :class:`ExecutionResult` inside ``intelligence_context``.

    Parameters
    ----------
    engine:
        The execution engine to use.  Defaults to a fresh
        :class:`AIExecutionEngine` (which itself defaults to the global
        provider registry).
    """

    priority: int = 500
    name: str = "IntelligenceStage"

    def __init__(self, engine: AIExecutionEngine | None = None) -> None:
        self._engine: AIExecutionEngine = (
            engine if engine is not None else AIExecutionEngine()
        )

    # ------------------------------------------------------------------
    # PipelineStage contract
    # ------------------------------------------------------------------

    def execute(self, context: PipelineContext) -> PipelineContext:
        """Run AI execution and attach the result to *context*.

        Always returns a :class:`PipelineContext` — never raises.

        Parameters
        ----------
        context:
            Immutable pipeline context for the current execution.

        Returns
        -------
        PipelineContext
            A new context with ``intelligence_context`` updated (or the
            original context if the stage was skipped).
        """
        # ── Guard 1: explicit context-level disable ─────────────────────
        if context.intelligence_enabled is False:
            return context

        # ── Guard 2: global feature flag (skipped when override=True) ───
        if (
            context.intelligence_enabled is None
            and not is_feature_enabled(ENABLE_AI)
        ):
            return context

        # ── Build or reuse ExecutionContext ─────────────────────────────
        exec_ctx: ExecutionContext = (
            context.intelligence_context
            if isinstance(context.intelligence_context, ExecutionContext)
            else ExecutionContext(
                data=dict(context.payload),
                metadata=dict(context.metadata),
            )
        )

        # ── Build AIRequest ─────────────────────────────────────────────
        request = AIRequest(
            task=context.metadata.get("ai_task", "text"),
            execution_context=exec_ctx,
            payload=context.payload,
            metadata=context.metadata,
            options=context.metadata.get("ai_options"),
        )

        # ── Delegate to engine (never raises) ──────────────────────────
        result = self._engine.execute(request)

        # ── Attach result and return new context ────────────────────────
        return context.with_updates(intelligence_context=result)
