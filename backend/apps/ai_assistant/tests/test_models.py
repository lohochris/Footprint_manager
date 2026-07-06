import pytest
import uuid
from django.contrib.auth import get_user_model
from backend.apps.ai_assistant.models import (
    AssistantSession, AssistantMessage, PromptTemplate,
    AIInteractionLog, AIFeedback
)

pytestmark = pytest.mark.django_db

User = get_user_model()

@pytest.fixture
def user():
    return User.objects.create(username="testuser", email="test@example.com")

def test_assistant_session_creation(user):
    tenant_id = uuid.uuid4()
    workspace_id = uuid.uuid4()

    session = AssistantSession.objects.create(
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        owner=user,
        title="Test Session",
        status="active"
    )
    assert session.id is not None
    assert session.title == "Test Session"
    assert session.tenant_id == tenant_id
    assert session.workspace_id == workspace_id
    assert session.owner == user
    assert session.status == "active"

def test_assistant_message_creation(user):
    tenant_id = uuid.uuid4()
    session = AssistantSession.objects.create(
        tenant_id=tenant_id,
        owner=user,
        title="Test Session"
    )

    msg = AssistantMessage.objects.create(
        session=session,
        role="user",
        content="Hello AI",
        tokens_used=10
    )

    assert msg.session == session
    assert msg.role == "user"
    assert msg.content == "Hello AI"
    assert msg.tokens_used == 10

def test_prompt_template_creation():
    tenant_id = uuid.uuid4()
    template = PromptTemplate.objects.create(
        tenant_id=tenant_id,
        name="test_prompt",
        version="v1",
        description="A test prompt",
        template_text="Hello {name}",
        is_active=True
    )

    assert template.name == "test_prompt"
    assert template.version == "v1"
    assert template.template_text == "Hello {name}"
    assert template.is_active is True

def test_ai_interaction_log_creation():
    tenant_id = uuid.uuid4()
    log = AIInteractionLog.objects.create(
        tenant_id=tenant_id,
        provider="MockAIProvider",
        model="mock-model",
        prompt_tokens=10,
        completion_tokens=20,
        cost=0.001,
        status="success"
    )

    assert log.provider == "MockAIProvider"
    assert log.status == "success"

def test_ai_feedback_creation(user):
    tenant_id = uuid.uuid4()
    session = AssistantSession.objects.create(tenant_id=tenant_id, owner=user)
    msg = AssistantMessage.objects.create(session=session, role="assistant", content="AI says hi")

    feedback = AIFeedback.objects.create(
        message=msg,
        is_positive=True,
        comment="Good answer"
    )

    assert feedback.message == msg
    assert feedback.is_positive is True
    assert feedback.comment == "Good answer"
