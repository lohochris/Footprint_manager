import uuid
from typing import List, Dict, Any
from backend.apps.orchestration.models import Playbook, WorkflowExecution

class PlaybookSelector:
    @staticmethod
    def list_playbooks(tenant_id: uuid.UUID, is_active: bool = True) -> List[Dict[str, Any]]:
        # Returning dictionary for DTO mapping
        qs = Playbook.objects.filter(tenant_id=tenant_id, is_active=is_active).values(
            "id", "name", "description", "created_at"
        )
        return list(qs) # type: ignore

class ExecutionSelector:
    @staticmethod
    def list_executions(tenant_id: uuid.UUID, workspace_id: uuid.UUID | None = None) -> List[Dict[str, Any]]:
        qs = WorkflowExecution.objects.filter(tenant_id=tenant_id)
        if workspace_id:
            qs = qs.filter(workspace_id=workspace_id)

        return list(qs.values("id", "status", "started_at", "completed_at", "playbook_version_id")) # type: ignore
