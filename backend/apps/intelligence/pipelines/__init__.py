# Import registry to ensure PipelineFactory registers the stages
from . import registry

__all__ = ["registry"]
