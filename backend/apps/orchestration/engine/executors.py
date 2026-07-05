from .registry import IStepExecutor, StepRegistry
from .context import ExecutionContext
import structlog

logger = structlog.get_logger(__name__)

class AIStepExecutor(IStepExecutor):
    def execute(self, step_config: dict, context: ExecutionContext) -> dict:
        logger.info("Executing AI Step", step_config=step_config)
        # Mock logic
        return {"ai_result": "Success", "confidence": 0.99}

class OSINTStepExecutor(IStepExecutor):
    def execute(self, step_config: dict, context: ExecutionContext) -> dict:
        logger.info("Executing OSINT Step", step_config=step_config)
        return {"osint_result": "Discovery completed", "entities_found": 5}

class GraphStepExecutor(IStepExecutor):
    def execute(self, step_config: dict, context: ExecutionContext) -> dict:
        logger.info("Executing Graph Step", step_config=step_config)
        return {"graph_result": "Node expanded", "new_edges": 2}

class ApprovalStepExecutor(IStepExecutor):
    def execute(self, step_config: dict, context: ExecutionContext) -> dict:
        logger.info("Executing Approval Step", step_config=step_config)
        # Typically this pauses the workflow until a user intervenes
        return {"approval_status": "Waiting"}

def register_executors():
    StepRegistry.register("ai", AIStepExecutor)
    StepRegistry.register("osint", OSINTStepExecutor)
    StepRegistry.register("graph", GraphStepExecutor)
    StepRegistry.register("approval", ApprovalStepExecutor)
