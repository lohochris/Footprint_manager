import abc
from django.core.files.base import File


class BaseMalwareScanner(abc.ABC):
    """Abstract base class for malware scanners."""

    @abc.abstractmethod
    def scan(self, file_obj: File) -> tuple[bool, dict]:
        """Scans the file object for malware.

        Args:
            file_obj: Django File object to scan.

        Returns:
            A tuple of (is_malicious, scan_metadata_dict).
        """
        pass
class MalwareScannerError(Exception):
    """Base exception for malware scanning failures."""
    pass
