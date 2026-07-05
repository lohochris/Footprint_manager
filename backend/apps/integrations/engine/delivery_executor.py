import uuid
import time
from typing import Dict, Any, Optional
from ..repositories import DeliveryRepository
from ..providers.registry import integration_provider_registry, secrets_provider
from ..models import IntegrationEndpoint, IntegrationEvent
from .retry_policy import RetryPolicy

class DeliveryExecutor:
    def __init__(self):
        self.retry_policy = RetryPolicy()

    def execute_delivery(self, tenant_id: uuid.UUID, event: IntegrationEvent, endpoint: IntegrationEndpoint, payload: Dict[str, Any]) -> bool:
        provider = integration_provider_registry.get(endpoint.integration.provider)
        if not provider:
            return False

        credentials = None
        if endpoint.integration.credentials_reference:
            credentials = secrets_provider.get_secret(endpoint.integration.credentials_reference)

        attempt = 1
        success = False

        while attempt <= self.retry_policy.max_retries and not success:
            start_time = time.time()
            result = provider.deliver(endpoint.url, payload, credentials)
            latency_ms = int((time.time() - start_time) * 1000)

            success = result.get("is_successful", False)
            status_code = result.get("status_code")

            DeliveryRepository.record_attempt(
                tenant_id=tenant_id,
                event_id=event.id,
                idempotency_key=f"{event.idempotency_key}_{attempt}",
                attempt_number=attempt,
                latency_ms=latency_ms,
                provider_response_code=str(status_code) if status_code else None,
                provider_response_body=result.get("response_body", ""),
                error_message=result.get("error", ""),
                is_successful=success
            )

            if success:
                break

            if not self.retry_policy.should_retry(attempt, str(status_code)):
                break

            delay = self.retry_policy.get_delay(attempt)
            time.sleep(delay)  # In production, this would schedule a celery task
            attempt += 1

        return success
