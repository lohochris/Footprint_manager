import uuid
from typing import Dict, Any
from .context import ExecutionContext
from .registry import StepRegistry
from backend.shared.events import DomainEventBus
import structlog

logger = structlog.get_logger(__name__)

class WorkflowEngine:
    """
    Core engine for interpreting and orchestrating Playbook DAGs.
    Separated from Provider. The engine evaluates steps and invokes the StepRegistry.
    """
    def __init__(self, context: ExecutionContext, dag_definition: Dict[str, Any]):
        self.context = context
        self.dag = dag_definition
        # Simplified linear/sequential execution for now
        self.steps = self.dag.get("steps", [])

    def execute(self) -> None:
        """
        Executes the workflow graph.
        """
        logger.info("orchestration.engine.execute_started", execution_id=self.context.workflow_execution_id)
        DomainEventBus.publish("workflow.started", execution_id=self.context.workflow_execution_id)

        for step in self.steps:
            step_id = step.get("id")
            step_type = step.get("type")
            config = step.get("config", {})

            logger.info("orchestration.engine.step_starting", step_id=step_id, step_type=step_type)
            DomainEventBus.publish("step.starting", execution_id=self.context.workflow_execution_id, step_id=step_id)

            try:
                executor_cls = StepRegistry.get_executor(step_type)
                executor = executor_cls()

                # Execute step
                output = executor.execute(config, self.context)
                self.context.add_step_output(step_id, output)

                logger.info("orchestration.engine.step_completed", step_id=step_id)
                DomainEventBus.publish("step.completed", execution_id=self.context.workflow_execution_id, step_id=step_id, output=output)
            except Exception as e:
                logger.error("orchestration.engine.step_failed", step_id=step_id, error=str(e))
                DomainEventBus.publish("step.failed", execution_id=self.context.workflow_execution_id, step_id=step_id, error=str(e))
                raise

        logger.info("orchestration.engine.execute_completed", execution_id=self.context.workflow_execution_id)
        DomainEventBus.publish("workflow.completed", execution_id=self.context.workflow_execution_id)
