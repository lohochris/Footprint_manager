from django.core.files.base import File

from .base import BaseMalwareScanner


class NoOpMalwareScanner(BaseMalwareScanner):
    """A no-op malware scanner that always returns clean/safe results."""

    def scan(self, file_obj: File) -> tuple[bool, dict]:
        return False, {"status": "skipped", "reason": "no-op"}
