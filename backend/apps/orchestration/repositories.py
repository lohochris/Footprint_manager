import uuid
from typing import Optional, List, Any
from django.db import transaction
from django.utils import timezone
from backend.apps.orchestration.models import Playbook, PlaybookVersion, WorkflowExecution, StepExecution

class PlaybookRepository:
    @staticmethod
    def create_playbook(tenant_id: uuid.UUID, owner_id: Any, name: str, description: str = "") -> Playbook:
        return Playbook.objects.create(
            tenant_id=tenant_id,
            owner_id=owner_id,
            name=name,
            description=description
        )

    @staticmethod
    def get_playbook(tenant_id: uuid.UUID, playbook_id: uuid.UUID) -> Optional[Playbook]:
        return Playbook.objects.filter(tenant_id=tenant_id, id=playbook_id).first()

    @staticmethod
    def create_version(playbook: Playbook, version: str, definition: dict) -> PlaybookVersion:
        return PlaybookVersion.objects.create(
            playbook=playbook,
            version=version,
            definition=definition
        )

class WorkflowExecutionRepository:
    @staticmethod
    def create_execution(
        tenant_id: uuid.UUID,
        playbook_version_id: uuid.UUID,
        creator_id: Any | None = None,
        workspace_id: Optional[uuid.UUID] = None
    ) -> WorkflowExecution:
        return WorkflowExecution.objects.create(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            playbook_version_id=playbook_version_id,
            creator_id=creator_id,
            status=WorkflowExecution.Status.PENDING
        )

    @staticmethod
    def update_status(execution_id: uuid.UUID, status: str, outputs: Optional[dict] = None) -> None:
        update_fields: dict[str, Any] = {"status": status}
        if outputs is not None:
            update_fields["outputs"] = outputs
        if status in [WorkflowExecution.Status.COMPLETED, WorkflowExecution.Status.FAILED, WorkflowExecution.Status.CANCELLED]:
            update_fields["completed_at"] = timezone.now()
            
        WorkflowExecution.objects.filter(id=execution_id).update(**update_fields)

    @staticmethod
    def get_execution(tenant_id: uuid.UUID, execution_id: uuid.UUID) -> Optional[WorkflowExecution]:
        return WorkflowExecution.objects.filter(tenant_id=tenant_id, id=execution_id).first()
