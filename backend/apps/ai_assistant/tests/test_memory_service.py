import pytest
import uuid
from django.contrib.auth import get_user_model
from backend.apps.ai_assistant.memory.service import MemoryService
from backend.apps.ai_assistant.models import AssistantSession, AssistantMessage

pytestmark = pytest.mark.django_db

@pytest.fixture
def user():
    User = get_user_model()
    return User.objects.create(username="memuser")

def test_memory_service_retrieval(user):
    tenant_id = uuid.uuid4()
    session = AssistantSession.objects.create(tenant_id=tenant_id, owner=user)
    
    # Create 3 messages
    AssistantMessage.objects.create(session=session, role="user", content="Msg 1")
    AssistantMessage.objects.create(session=session, role="assistant", content="Msg 2")
    AssistantMessage.objects.create(session=session, role="user", content="Msg 3")
    
    service = MemoryService()
    
    # Retrieve all
    history = service.get_session_history(session_id=str(session.id), max_messages=10)
    assert len(history) == 3
    assert history[0].content == "Msg 1"
    assert history[2].content == "Msg 3"
    
    # Retrieve last 2
    history_limited = service.get_session_history(session_id=str(session.id), max_messages=2)
    assert len(history_limited) == 2
    assert history_limited[0].content == "Msg 2"
    assert history_limited[1].content == "Msg 3"
