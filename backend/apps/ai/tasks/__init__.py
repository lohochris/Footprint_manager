"""
AI Celery task definitions for Footprint Manager.

Defines the task signatures for asynchronous AI operations.  Task
implementations will be added in future sprints when the AI feature flag
is enabled.  This module establishes the task naming conventions and
parameter contracts used across the platform.

All AI tasks must:
- Accept serialisable parameters only (no model instances).
- Return serialisable results.
- Implement retry logic with exponential backoff.
- Emit structured log events on start, success, and failure.
"""

from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name="ai.complete_prompt",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    acks_late=True,
)
def complete_prompt(
    _self: object,
    prompt: str,
    *,
    provider: str | None = None,
    model: str | None = None,
    session_id: str | None = None,
    context: dict | None = None,
) -> dict:
    """
    Asynchronously execute an AI completion request.

    Args:
        prompt: The user prompt to complete.
        provider: Optional provider name override.
        model: Optional model name override.
        session_id: Conversation session ID for memory continuity.
        context: Additional context injected into the prompt template.

    Returns:
        Serialisable dict containing the completion result.
    """
    logger.info(
        "ai_complete_prompt_task_received",
        extra={
            "prompt_length": len(prompt),
            "provider": provider,
            "model": model,
            "session_id": session_id,
            "context_keys": sorted(context.keys()) if context else [],
        },
    )
    return {
        "status": "pending",
        "message": "AI completion task received. Provider not yet configured.",
    }


@shared_task(
    name="ai.generate_embeddings",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    acks_late=True,
)
def generate_embeddings(
    _self: object,
    texts: list[str],
    *,
    model: str | None = None,
    index: str | None = None,
    document_ids: list[str] | None = None,
) -> dict:
    """
    Asynchronously generate and optionally store embeddings.

    Args:
        texts: List of text strings to embed.
        model: Optional embedding model name override.
        index: Target search index for storing embeddings.
        document_ids: Document identifiers corresponding to each text.

    Returns:
        Serialisable dict with task status and count of processed items.
    """
    logger.info(
        "ai_generate_embeddings_task_received",
        extra={
            "text_count": len(texts),
            "model": model,
            "index": index,
            "document_id_count": len(document_ids) if document_ids else 0,
        },
    )
    return {
        "status": "pending",
        "text_count": len(texts),
        "message": "Embedding task received. Provider not yet configured.",
    }


__all__ = [
    "complete_prompt",
    "generate_embeddings",
]
