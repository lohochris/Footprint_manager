import pytest
import uuid
from backend.apps.orchestration.services import WorkflowService
from backend.apps.orchestration.dto import PlaybookExecutionParams
from backend.apps.orchestration.models import Playbook, PlaybookVersion, WorkflowExecution
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db

@pytest.fixture
def user():
    User = get_user_model()
    return User.objects.create(username="service_user")

def test_workflow_service_start_execution(user):
    tenant_id = uuid.uuid4()
    playbook = Playbook.objects.create(tenant_id=tenant_id, name="PB", owner=user)
    version = PlaybookVersion.objects.create(playbook=playbook, version="1.0", definition={})

    # We need to make sure the executors used in the mock service def exist
    from backend.apps.orchestration.engine.executors import register_executors
    register_executors()

    params = PlaybookExecutionParams(
        tenant_id=tenant_id,
        playbook_version_id=version.id,
        creator_id=user.id
    )

    dto = WorkflowService.start_execution(params)

    assert dto.status == "completed"

    # Verify DB state
    execution = WorkflowExecution.objects.get(id=dto.id)
    assert execution.status == WorkflowExecution.Status.COMPLETED
