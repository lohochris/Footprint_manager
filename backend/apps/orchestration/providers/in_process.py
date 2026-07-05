import uuid
from typing import Any, Dict
from .base import BaseWorkflowProvider
from backend.apps.orchestration.engine.core import WorkflowEngine
from backend.apps.orchestration.engine.context import ExecutionContext
import structlog

logger = structlog.get_logger(__name__)

class InProcessWorkflowProvider(BaseWorkflowProvider):
    """
    Executes workflows in-process synchronously.
    Primarily used for testing, immediate lightweight automations, or single-node deployments.
    """
    def execute_workflow(self, execution_id: uuid.UUID, context_data: Dict[str, Any], playbook_def: Dict[str, Any]) -> None:
        logger.info("orchestration.in_process_provider.executing", execution_id=str(execution_id))

        # Rehydrate context
        context = ExecutionContext(
            workflow_execution_id=execution_id,
            tenant_id=uuid.UUID(str(context_data.get("tenant_id"))),
            workspace_id=uuid.UUID(str(context_data["workspace_id"])) if context_data.get("workspace_id") else None,
            variables=context_data.get("variables", {})
        )

        engine = WorkflowEngine(context=context, dag_definition=playbook_def)
        engine.execute()

    def pause_workflow(self, execution_id: uuid.UUID) -> None:
        logger.warning("orchestration.in_process_provider.pause_not_supported", execution_id=str(execution_id))

    def resume_workflow(self, execution_id: uuid.UUID) -> None:
        logger.warning("orchestration.in_process_provider.resume_not_supported", execution_id=str(execution_id))

    def cancel_workflow(self, execution_id: uuid.UUID) -> None:
        logger.warning("orchestration.in_process_provider.cancel_not_supported", execution_id=str(execution_id))
