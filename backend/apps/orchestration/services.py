import uuid
from typing import Dict, Any
from .repositories import PlaybookRepository, WorkflowExecutionRepository
from .providers.factory import ProviderFactory
from .dto import PlaybookExecutionParams, WorkflowExecutionDTO
import structlog

logger = structlog.get_logger(__name__)

class WorkflowService:
    @staticmethod
    def start_execution(params: PlaybookExecutionParams) -> WorkflowExecutionDTO:
        logger.info("orchestration.service.starting_execution", playbook_version_id=str(params.playbook_version_id))

        # In a real system, we'd fetch the playbook definition from the repo
        # using the version id.
        # For now, we mock the definition.
        playbook_def = {
            "steps": [
                {"id": "step_1", "type": "osint", "config": {}},
                {"id": "step_2", "type": "ai", "config": {}}
            ]
        }

        # 1. Persist the pending execution
        execution = WorkflowExecutionRepository.create_execution(
            tenant_id=params.tenant_id,
            playbook_version_id=params.playbook_version_id,
            creator_id=params.creator_id,
            workspace_id=params.workspace_id
        )

        # 2. Update status to running
        WorkflowExecutionRepository.update_status(execution.id, "running")

        # 3. Hand off to the workflow provider abstraction
        provider = ProviderFactory.get_provider("in_process")

        # Provide execution details to the backend
        context_data = {
            "tenant_id": params.tenant_id,
            "workspace_id": params.workspace_id,
            "variables": params.variables
        }

        try:
            # For async providers (Celery), this would be fire-and-forget.
            # In process, it blocks until done.
            provider.execute_workflow(execution.id, context_data, playbook_def)
            WorkflowExecutionRepository.update_status(execution.id, "completed", {"success": True})
        except Exception as e:
            logger.error("orchestration.service.execution_failed", error=str(e))
            WorkflowExecutionRepository.update_status(execution.id, "failed")

        execution.refresh_from_db()

        return WorkflowExecutionDTO(
            id=str(execution.id),
            playbook_version_id=str(execution.playbook_version_id),
            status=execution.status,
            outputs=execution.outputs
        )
