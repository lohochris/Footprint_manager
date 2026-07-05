import pytest
import uuid
from django.contrib.auth import get_user_model
from backend.apps.orchestration.models import Playbook, PlaybookVersion, WorkflowExecution

pytestmark = pytest.mark.django_db

@pytest.fixture
def user():
    User = get_user_model()
    return User.objects.create(username="orchestration_user")

def test_playbook_creation(user):
    tenant_id = uuid.uuid4()
    playbook = Playbook.objects.create(
        tenant_id=tenant_id,
        name="Test Playbook",
        owner=user,
        description="A test playbook"
    )

    assert playbook.id is not None
    assert playbook.name == "Test Playbook"
    assert playbook.is_active is True

def test_workflow_execution_creation(user):
    tenant_id = uuid.uuid4()
    workspace_id = uuid.uuid4()

    playbook = Playbook.objects.create(tenant_id=tenant_id, name="Test PB", owner=user)
    version = PlaybookVersion.objects.create(playbook=playbook, version="1.0", definition={"steps": []})

    execution = WorkflowExecution.objects.create(
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        playbook_version=version,
        creator=user
    )

    assert execution.status == WorkflowExecution.Status.PENDING
    assert execution.tenant_id == tenant_id
    assert execution.workspace_id == workspace_id
