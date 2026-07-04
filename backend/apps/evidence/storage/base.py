import abc
from django.core.files.base import File


class BaseStorageProvider(abc.ABC):
    """Abstract base class for evidence file storage providers."""

    @abc.abstractmethod
    def save(self, file_obj: File, path: str) -> str:
        """Saves a file to storage and returns the storage key/path.

        Args:
            file_obj: The file to save.
            path: Target storage path.
        """
        pass

    @abc.abstractmethod
    def read(self, storage_key: str) -> bytes:
        """Reads a file from storage and returns its raw bytes.

        Args:
            storage_key: The storage key of the file.
        """
        pass

    @abc.abstractmethod
    def delete(self, storage_key: str) -> None:
        """Deletes a file from storage.

        Args:
            storage_key: The storage key of the file.
        """
        pass

    @abc.abstractmethod
    def generate_download_url(self, storage_key: str, ttl_seconds: int = 300) -> str:
        """Generates a temporary pre-signed download URL.

        Args:
            storage_key: The storage key of the file.
            ttl_seconds: Time to live in seconds.
        """
        pass
