from django.core.files.base import File
from django.core.files.storage import default_storage

from .base import BaseStorageProvider


class LocalStorageProvider(BaseStorageProvider):
    """Local storage provider implementation using Django's default storage backend."""

    def save(self, file_obj: File, path: str) -> str:
        return default_storage.save(path, file_obj)

    def read(self, storage_key: str) -> bytes:
        with default_storage.open(storage_key, "rb") as f:
            return f.read()

    def delete(self, storage_key: str) -> None:
        if default_storage.exists(storage_key):
            default_storage.delete(storage_key)

    def generate_download_url(self, storage_key: str, ttl_seconds: int = 300) -> str:
        # Returns the default storage URL (or local media file URL)
        return default_storage.url(storage_key)
