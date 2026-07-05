import pytest
import uuid
from backend.shared.events.bus import DomainEventBus
from backend.apps.collaboration.services.task_service import TaskService
from backend.apps.collaboration.models import CaseWorkspace

@pytest.fixture
def event_bus():
    return DomainEventBus()

@pytest.fixture
def task_service(event_bus):
    return TaskService(event_bus)

@pytest.mark.django_db
def test_create_task(task_service):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create(email="test@test.com", username="testuser")

    tenant_id = uuid.uuid4()
    workspace = CaseWorkspace.objects.create(tenant_id=tenant_id, name="Test Workspace")
    creator_id = user.id

    task_dto = task_service.create_task(
        tenant_id=tenant_id,
        workspace_id=workspace.id,
        creator_id=creator_id,
        title="Test Task",
        description="Test Desc",
        priority="high"
    )

    assert task_dto.title == "Test Task"
    assert task_dto.priority == "high"
    assert task_dto.case_workspace_id == workspace.id
