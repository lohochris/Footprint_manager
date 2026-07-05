import pytest
from backend.apps.ai_assistant.dto.ai_provider_dto import (
    AIChatMessageDTO, AICompletionRequestDTO, AICompletionResponseDTO
)
from backend.apps.ai_assistant.dto.rag_dto import RAGSourceDTO, RAGContextDTO

def test_ai_chat_message_dto():
    msg = AIChatMessageDTO(role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"

def test_ai_completion_request_dto():
    msg = AIChatMessageDTO(role="user", content="Test")
    req = AICompletionRequestDTO(
        messages=[msg],
        model="gpt-4",
        tenant_id="tenant-123",
        workspace_id="workspace-123",
        temperature=0.7,
        max_tokens=100
    )
    assert len(req.messages) == 1
    assert req.model == "gpt-4"
    assert req.tenant_id == "tenant-123"
    assert req.temperature == 0.7
    assert req.max_tokens == 100

def test_ai_completion_response_dto():
    res = AICompletionResponseDTO(
        content="Response text",
        model_used="gpt-4",
        prompt_tokens=10,
        completion_tokens=20,
        total_cost=0.002
    )
    assert res.content == "Response text"
    assert res.prompt_tokens == 10
    assert res.completion_tokens == 20
    assert res.total_cost == 0.002

def test_rag_source_dto():
    source = RAGSourceDTO(
        domain="evidence",
        source_id="123",
        content="Evidence text",
        relevance_score=0.95
    )
    assert source.domain == "evidence"
    assert source.source_id == "123"
    assert source.content == "Evidence text"
    assert source.relevance_score == 0.95

def test_rag_context_dto():
    source = RAGSourceDTO(domain="osint", source_id="1", content="OSINT hit", relevance_score=0.8)
    context = RAGContextDTO(
        query="Who is John?",
        sources=[source]
    )
    assert context.query == "Who is John?"
    assert len(context.sources) == 1
    assert "Domain: osint" in context.formatted_text
    assert "OSINT hit" in context.formatted_text
