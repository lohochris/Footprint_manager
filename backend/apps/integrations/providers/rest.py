import requests
from typing import Any, Dict, Optional
from .base import BaseIntegrationProvider

class RESTProvider(BaseIntegrationProvider):
    @property
    def provider_id(self) -> str:
        return "rest"

    def deliver(self, endpoint_url: str, payload: Dict[str, Any], credentials: Optional[str] = None) -> Dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if credentials:
            headers["Authorization"] = f"Bearer {credentials}"

        try:
            response = requests.post(endpoint_url, json=payload, headers=headers, timeout=10)
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
