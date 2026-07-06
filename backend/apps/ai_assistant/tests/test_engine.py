import pytest
import uuid
from django.contrib.auth import get_user_model
from backend.apps.ai_assistant.services.engine import AIIntelligenceEngine
from backend.apps.ai_assistant.models import AssistantSession, AssistantMessage, AIInteractionLog
from django.conf import settings

pytestmark = pytest.mark.django_db

@pytest.fixture
def user():
    User = get_user_model()
    return User.objects.create(username="engineuser")

def test_engine_chat_flow(user):
    # Set default provider to mock
    settings.DEFAULT_AI_PROVIDER = "mock"

    tenant_id = uuid.uuid4()
    session = AssistantSession.objects.create(tenant_id=tenant_id, owner=user, title="Engine Test")

    engine = AIIntelligenceEngine()
    response = engine.chat(session_id=str(session.id), user_message="What is the capital of France?")

    assert "mock response" in response.lower()

    # Verify persistence
    messages = AssistantMessage.objects.filter(session=session).order_by("created_at")
    assert messages.count() == 2
    assert messages[0].role == "user"
    assert messages[0].content == "What is the capital of France?"

    assert messages[1].role == "assistant"
    assert "mock response" in messages[1].content.lower()

    # Verify Logging
    logs = AIInteractionLog.objects.filter(tenant_id=tenant_id)
    assert logs.count() == 1
    assert logs[0].provider == "MockAIProvider"
    assert logs[0].status == "success"
