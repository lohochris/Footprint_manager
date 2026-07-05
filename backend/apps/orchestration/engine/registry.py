from typing import Dict, Type, TYPE_CHECKING
import structlog

if TYPE_CHECKING:
    from .context import ExecutionContext

logger = structlog.get_logger(__name__)

class IStepExecutor:
    """
    Interface for executable steps within a workflow playbook.
    """
    def execute(self, step_config: dict, context: 'ExecutionContext') -> dict:
        """
        Execute the step with the given configuration and execution context.
        Returns a dictionary representing the outputs of this step.
        """
        raise NotImplementedError("Step executors must implement the execute method.")


class StepRegistry:
    """
    Registry for pluggable StepExecutor implementations.
    """
    _executors: Dict[str, Type[IStepExecutor]] = {}

    @classmethod
    def register(cls, step_type: str, executor_cls: Type[IStepExecutor]) -> None:
        cls._executors[step_type] = executor_cls
        logger.info("orchestration.step_registered", step_type=step_type, executor=executor_cls.__name__)

    @classmethod
    def get_executor(cls, step_type: str) -> Type[IStepExecutor]:
        if step_type not in cls._executors:
            raise ValueError(f"No StepExecutor registered for type '{step_type}'")
        return cls._executors[step_type]

    @classmethod
    def list_executors(cls) -> list[str]:
        return list(cls._executors.keys())
