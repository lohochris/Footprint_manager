"""
Storage backend abstraction for Footprint Manager.

Defines the ``StorageBackend`` protocol and supporting data structures for
file storage operations.  Concrete implementations are registered in
``apps/integrations/storage/``.

Planned backends:
- Local filesystem (development)
- Amazon S3 (production default)
- MinIO (self-hosted / on-premise)
- Azure Blob Storage (enterprise)

Usage::

    from backend.shared.storage import StorageBackend, StoredFile

    def upload_evidence(backend: StorageBackend, name: str, data: bytes) -> str:
        stored = backend.upload(name, data, content_type="image/png")
        return stored.url
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class StoredFile:
    """
    Metadata describing a file that has been stored.

    Attributes:
        key: Backend-specific storage path / object key.
        url: Publicly or pre-signed accessible URL.
        size_bytes: File size in bytes.
        content_type: MIME type of the stored file.
        etag: Content hash / ETag returned by the backend (optional).
        metadata: Arbitrary backend-specific metadata.
    """

    key: str
    url: str
    size_bytes: int
    content_type: str
    etag: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class StorageBackend(abc.ABC):
    """
    Abstract interface for file storage backends.

    All methods operate on byte streams and string keys.  Implementations
    handle provider-specific connection pooling and credential management.
    """

    @abc.abstractmethod
    def upload(
        self,
        key: str,
        data: bytes,
        *,
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
    ) -> StoredFile:
        """
        Upload *data* to the storage backend under *key*.

        Args:
            key: Destination path / object key.
            data: Raw bytes to store.
            content_type: MIME type of the content.
            metadata: Optional key-value metadata to attach.

        Returns:
            ``StoredFile`` describing the stored object.
        """

    @abc.abstractmethod
    def download(self, key: str) -> bytes:
        """
        Download and return the raw bytes stored at *key*.

        Args:
            key: Storage path / object key to retrieve.

        Returns:
            Raw file bytes.

        Raises:
            shared.exceptions.NotFoundError: If *key* does not exist.
        """

    @abc.abstractmethod
    def delete(self, key: str) -> None:
        """
        Delete the object stored at *key*.

        Args:
            key: Storage path / object key to remove.
        """

    @abc.abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check whether an object exists at *key*.

        Args:
            key: Storage path / object key to check.

        Returns:
            True if the object exists.
        """

    @abc.abstractmethod
    def generate_url(self, key: str, *, expires_in: int = 3600) -> str:
        """
        Generate a pre-signed URL for *key* valid for *expires_in* seconds.

        Args:
            key: Storage path / object key.
            expires_in: URL validity period in seconds (default: 3600).

        Returns:
            Pre-signed URL string.
        """

    @abc.abstractmethod
    def list_keys(self, prefix: str = "") -> list[str]:
        """
        List all object keys matching *prefix*.

        Args:
            prefix: Key prefix filter (empty string = all objects).

        Returns:
            Ordered list of matching key strings.
        """


__all__ = [
    "StoredFile",
    "StorageBackend",
]
