"""Pipeline Factory

Provides a factory for constructing :class:`Pipeline` instances. The factory can be
extended to read configuration from Django settings, allowing per‑operation stage
lists and custom stage ordering.
"""


from .core import Pipeline, PipelineStage


class PipelineFactory:
    """Factory responsible for creating pipelines for a given operation.

    The default implementation returns a :class:`Pipeline` with no stages. In a
    real system the factory would look up registered stage classes (perhaps via
    settings) and instantiate them. The ``stage_registry`` attribute maps an
    operation name to a list of :class:`PipelineStage` subclasses.
    """

    # Mapping operation -> list of stage classes (subclasses of PipelineStage)
    stage_registry: dict[str, list[type[PipelineStage]]] = {}

    @classmethod
    def register_stages(cls, operation: str, stages: list[type[PipelineStage]]) -> None:
        """Register a list of stage classes for *operation*.

        Args:
            operation: Dotted operation name (e.g., ``"organization.create"``).
            stages: Ordered list of ``PipelineStage`` subclasses. Ordering is
                determined by their ``priority`` attribute during pipeline
                construction.
        """
        cls.stage_registry[operation] = stages

    @classmethod
    def create_pipeline(cls, operation: str) -> Pipeline:
        """Create a :class:`Pipeline` for *operation*.

        If no stages are registered for the operation an empty pipeline is
        returned, which will simply pass the initial context through.
        """
        stage_classes = cls.stage_registry.get(operation, [])
        # Instantiate each stage class (no args required for abstract base).
        stages = [stage_cls() for stage_cls in stage_classes]
        return Pipeline(stages)
