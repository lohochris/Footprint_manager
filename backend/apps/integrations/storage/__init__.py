"""
Storage integration for Footprint Manager.

Re-exports ``shared.storage`` types for use within the integrations layer
and provides a factory for obtaining the configured storage backend.

The active backend is determined by the ``STORAGE_BACKEND`` setting:
- ``"local"``  → local filesystem (development only)
- ``"s3"``     → Amazon S3
- ``"minio"``  → MinIO (self-hosted S3-compatible)
- ``"azure"``  → Azure Blob Storage

Concrete backend implementations will be added in future sprints.
"""

from __future__ import annotations

from shared.storage import StorageBackend, StoredFile

__all__ = [
    "StorageBackend",
    "StoredFile",
]
