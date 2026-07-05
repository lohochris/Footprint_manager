from typing import Any, Dict
import uuid

class BaseWorkflowProvider:
    """
    Abstract interface for workflow execution backends.
    This separates the orchestration logic (WorkflowEngine) from how the code runs (Celery, Temporal, etc.)
    """
    def execute_workflow(self, execution_id: uuid.UUID, context_data: Dict[str, Any], playbook_def: Dict[str, Any]) -> None:
        raise NotImplementedError

    def pause_workflow(self, execution_id: uuid.UUID) -> None:
        raise NotImplementedError

    def resume_workflow(self, execution_id: uuid.UUID) -> None:
        raise NotImplementedError

    def cancel_workflow(self, execution_id: uuid.UUID) -> None:
        raise NotImplementedError
