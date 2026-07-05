import uuid
import logging
import json
from typing import Dict, Any, Optional
from .base import BaseLoggingProvider

logger = logging.getLogger("footprint_manager.observability")

class StructuredLoggingProvider(BaseLoggingProvider):
    """
    Outputs structured JSON logs for external ingestion (e.g., Elasticsearch, Loki).
    """
    def log(self, tenant_id: uuid.UUID, level: str, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        log_entry = {
            "tenant_id": str(tenant_id),
            "level": level,
            "message": message,
            "context": context or {}
        }

        # In a real app, you'd use python-json-logger, but we use a simple json dump for Sprint 15.
        if level.upper() == "ERROR":
            logger.error(json.dumps(log_entry))
        elif level.upper() == "WARNING":
            logger.warning(json.dumps(log_entry))
        elif level.upper() == "INFO":
            logger.info(json.dumps(log_entry))
        else:
            logger.debug(json.dumps(log_entry))
