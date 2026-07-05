import pytest
from backend.apps.ai_assistant.rag.retrievers import EvidenceRetriever, GraphRetriever, OSINTRetriever
from backend.apps.ai_assistant.rag.service import RAGService

def test_evidence_retriever():
    retriever = EvidenceRetriever()
    context = retriever.retrieve("tenant1", "workspace1", "test query")
    assert context.query == "test query"
    assert len(context.sources) > 0
    assert context.sources[0].domain == "evidence"

def test_graph_retriever():
    retriever = GraphRetriever()
    context = retriever.retrieve("tenant1", None, "test query")
    assert len(context.sources) > 0
    assert context.sources[0].domain == "graph"

def test_osint_retriever():
    retriever = OSINTRetriever()
    context = retriever.retrieve("tenant1", "workspace1", "test query")
    assert len(context.sources) > 0
    assert context.sources[0].domain == "osint"

def test_rag_service_aggregation():
    service = RAGService()
    context = service.get_context("tenant1", "workspace1", "test query")
    
    assert context.query == "test query"
    # It aggregates from 3 mocked retrievers, each returns at least 1
    assert len(context.sources) >= 3
    
    # Test ordering (relevance_score descending)
    scores = [s.relevance_score for s in context.sources]
    assert scores == sorted(scores, reverse=True)
