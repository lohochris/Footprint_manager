import time
from typing import Optional

class RetryPolicy:
    def __init__(self, max_retries: int = 3, base_delay: int = 2):
        self.max_retries = max_retries
        self.base_delay = base_delay

    def get_delay(self, attempt: int) -> int:
        """Exponential backoff with base_delay"""
        return self.base_delay ** attempt

    def should_retry(self, attempt: int, error_code: Optional[str] = None) -> bool:
        """Determines if a retry is allowed"""
        if attempt >= self.max_retries:
            return False

        # Optional logic: don't retry on 400 Bad Request
        if error_code and str(error_code).startswith("40") and error_code not in ("408", "429"):
            return False

        return True
