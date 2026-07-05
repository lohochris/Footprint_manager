import pytest
import uuid
from backend.apps.ai_assistant.prompts.service import PromptService
from backend.apps.ai_assistant.models import PromptTemplate
from backend.apps.ai_assistant.dto.rag_dto import RAGContextDTO, RAGSourceDTO

pytestmark = pytest.mark.django_db

def test_prompt_service_assemble_with_db_template():
    tenant_id = uuid.uuid4()
    PromptTemplate.objects.create(
        tenant_id=tenant_id,
        name="test_template",
        version="v1",
        template_text="Hello {user_name}, context is: {rag_context}",
        is_active=True
    )
    
    service = PromptService()
    rag_context = RAGContextDTO(query="test", sources=[RAGSourceDTO(domain="osint", source_id="1", content="some context", relevance_score=1.0)])
    
    result = service.assemble(
        tenant_id=str(tenant_id),
        template_name="test_template",
        template_version="v1",
        rag_context=rag_context,
        user_name="Alice"
    )
    
    assert "Hello Alice" in result
    assert "some context" in result

def test_prompt_service_fallback():
    service = PromptService()
    tenant_id = str(uuid.uuid4())
    
    result = service.assemble(
        tenant_id=tenant_id,
        template_name="default_chat",
        template_version="v1"
    )
    
    assert "You are an AI assistant" in result

def test_prompt_service_missing_variable():
    tenant_id = uuid.uuid4()
    PromptTemplate.objects.create(
        tenant_id=tenant_id,
        name="bad_template",
        version="v1",
        template_text="Hello {missing_var}",
        is_active=True
    )
    
    service = PromptService()
    result = service.assemble(
        tenant_id=str(tenant_id),
        template_name="bad_template",
        template_version="v1"
    )
    
    # It should catch KeyError and return the raw template
    assert result == "Hello {missing_var}"
