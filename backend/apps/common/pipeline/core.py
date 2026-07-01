import abc
import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PipelineContext:
    """Immutable context passed through pipeline stages.

    Attributes:
        performed_by: The user or service performing the operation.
        tenant: Tenant identifier (e.g., organization).
        payload: Arbitrary input data for the operation.
        metadata: Additional metadata that can be enriched by stages.
        stage_results: Mapping of stage name to its result data.
        errors: List of errors encountered during execution.
        execution_id: Unique identifier for this pipeline run.
        timestamps: Dict with 'start' and optional 'end' timestamps.
    """

    performed_by: Any
    tenant: Any
    payload: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    stage_results: dict[str, Any] = field(default_factory=dict)
    errors: list[Exception] = field(default_factory=list)
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamps: dict[str, float] = field(default_factory=lambda: {"start": time.time()})
    # New optional fields for intelligence support
    intelligence_enabled: bool | None = None
    intelligence_context: Any = None


    def with_updates(self, **kwargs) -> "PipelineContext":
        """Return a new instance with the supplied fields updated.

        This method respects immutability by creating a shallow copy with
        modifications. Nested mutable objects (dict/list) should be replaced
        entirely if you wish to avoid accidental mutation.
        """
        data = self.__dict__.copy()
        data.update(kwargs)
        return PipelineContext(**data)


@dataclass(frozen=True)
class ExecutionResult:
    """Standardised result returned by a pipeline execution.

    Attributes:
        success: Whether the pipeline completed without fatal errors.
        data: The primary result payload (often the business object).
        error: Optional error object if success is False.
        metadata: Additional information supplied by stages.
        execution_time: Total elapsed time in seconds.
        status_code: HTTP‑like status code for adapters.
    """

    success: bool
    data: Any = None
    error: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    status_code: int = 200


class PipelineStage(abc.ABC):
    """Base class for all pipeline stages.

    Concrete stages must define a ``priority`` class attribute used for
    ordering and implement the :meth:`execute` method.
    """

    priority: int = 0
    name: str = "BaseStage"

    @abc.abstractmethod
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute the stage logic and return a new ``PipelineContext``.

        Implementations must treat the ``context`` as immutable and return a
        fresh instance (typically via ``context.with_updates``).
        """
        raise NotImplementedError


class Pipeline:
    """Orchestrates execution of a series of :class:`PipelineStage` objects.

    The pipeline is constructed with an ordered list of stage instances.
    Execution proceeds sequentially based on stage ``priority`` ordering.
    """

    def __init__(self, stages: list[PipelineStage]):
        # Sort stages by priority (ascending). Lower number = earlier execution.
        self.stages = sorted(stages, key=lambda s: getattr(s, "priority", 0))

    def run(self, initial_context: PipelineContext) -> ExecutionResult:
        context = initial_context
        start = time.time()
        for stage in self.stages:
            try:
                context = stage.execute(context)
                # Record successful stage result for debugging/auditing.
                context = context.with_updates(
                    stage_results={**context.stage_results, stage.name: "success"}
                )
            except Exception as exc:  # pylint: disable=broad-except
                # Capture the error, stop further execution.
                context = context.with_updates(
                    errors=context.errors + [exc],
                    stage_results={**context.stage_results, stage.name: f"error: {exc}"},
                )
                return ExecutionResult(
                    success=False,
                    data=None,
                    error=exc,
                    metadata=context.metadata,
                    execution_time=time.time() - start,
                    status_code=500,
                )
        end = time.time()
        return ExecutionResult(
            success=True,
            data=context.payload,
            error=None,
            metadata=context.metadata,
            execution_time=end - start,
            status_code=200,
        )
