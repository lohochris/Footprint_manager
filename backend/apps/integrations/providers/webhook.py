import requests
import hmac
import hashlib
import json
from typing import Any, Dict, Optional
from .base import BaseIntegrationProvider

class WebhookProvider(BaseIntegrationProvider):
    @property
    def provider_id(self) -> str:
        return "webhook"

    def deliver(self, endpoint_url: str, payload: Dict[str, Any], credentials: Optional[str] = None) -> Dict[str, Any]:
        headers = {"Content-Type": "application/json"}

        body = json.dumps(payload)
        if credentials:
            # Generate HMAC signature
            signature = hmac.new(credentials.encode(), body.encode(), hashlib.sha256).hexdigest()
            headers["X-Hub-Signature-256"] = f"sha256={signature}"

        try:
            response = requests.post(endpoint_url, data=body, headers=headers, timeout=10)
            response.raise_for_status()
            return {
                "status_code": response.status_code,
                "response_body": response.text,
                "is_successful": True
            }
        except requests.exceptions.RequestException as e:
            return {
                "status_code": getattr(e.response, "status_code", None),
                "response_body": getattr(e.response, "text", str(e)),
                "is_successful": False,
                "error": str(e)
            }
