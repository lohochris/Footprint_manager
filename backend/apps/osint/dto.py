# backend/apps/osint/dto.py
"""Transport Data Transfer Objects for the OSINT Discovery domain.

All DTOs in this module are pure-Python frozen dataclasses.  They contain
NO Django ORM types, NO ``FileField``, NO ``SimpleUploadedFile``, and no
model imports.  This keeps the OSINT domain cleanly bounded and prevents
accidental coupling to Django internals or to sibling bounded contexts.

DTOs
----
DiscoveryRequest
    Input payload for a single discovery operation submitted by the caller.

DiscoveryResultDTO
    Normalised finding produced by a provider — ready for persistence as a
    ``DiscoveryResult`` model row.  No ORM types.

EvidenceUploadRequest
    Anti-corruption transport object representing a file that should be
    ingested by the Evidence bounded context.  OSINT produces only the
    ``storage_key``; the Evidence context owns the concrete upload logic.
    This DTO deliberately excludes ``SimpleUploadedFile`` and Django file
    primitives to enforce bounded-context isolation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class DiscoveryRequest:
    """Input payload for a single discovery operation.

    Created by the API layer or a scheduled task and passed to
    ``DiscoveryJobService.create_job()``.

    Attributes
    ----------
    provider_name:
        Slug of the target ``DiscoveryProvider`` (must match
        ``DiscoveryProvider.name``).
    capabilities:
        List of ``DiscoveryCapability`` value strings requested from the
        provider.
    input_data:
        Provider-specific query payload (e.g. ``{"email": "alice@..."}``).
    triggered_by:
        ``DiscoveryJobTrigger`` value string describing the initiating
        mechanism.
    investigation_id:
        Optional UUID string of the parent ``Investigation``.
    target_id:
        Optional UUID string of the parent ``InvestigationTarget``.
    metadata:
        Arbitrary key-value bag for tracing correlation IDs and caller
        context.
    """

    provider_name: str
    capabilities: list[str]
    input_data: dict[str, Any]
    triggered_by: str
    investigation_id: str | None = None
    target_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DiscoveryResultDTO:
    """Normalised finding produced by a provider.

    Returned by ``DiscoveryJobService.run()`` before being persisted as a
    ``DiscoveryResult`` model row.  Contains no ORM types so it is safely
    transportable across layer boundaries and serialisable without Django.

    Attributes
    ----------
    result_type:
        ``DiscoveryResultType`` value string.
    title:
        Short human-readable label for the finding.
    confidence:
        Normalised confidence in ``[0.0000, 1.0000]`` as a ``Decimal``.
    raw_data:
        Verbatim provider response fragment.
    normalised_data:
        Canonical representation after ``provider.normalize()`` has been
        applied.
    storage_key:
        Storage-agnostic key for any associated file artefact.  Empty when
        no artefact was produced.
    source_url:
        Canonical URL of the data source.
    summary:
        Prose description suitable for report generation.
    tags:
        Free-form label list for faceted filtering.
    """

    result_type: str
    title: str
    confidence: Decimal
    raw_data: dict[str, Any]
    normalised_data: dict[str, Any]
    storage_key: str = ""
    source_url: str = ""
    summary: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class EvidenceUploadRequest:
    """Transport object for cross-context evidence file ingestion.

    The OSINT domain produces this DTO after storing a file via the
    ``StorageBackend``.  The Evidence bounded context consumes it and
    creates the appropriate ``Evidence`` and ``EvidenceFile`` records.

    Crucially, this DTO contains NO Django file primitives
    (``SimpleUploadedFile``, ``InMemoryUploadedFile``, ``FileField``).
    The OSINT domain is therefore decoupled from Django's upload
    implementation; the Evidence context owns that responsibility.

    Attributes
    ----------
    storage_key:
        Opaque key referencing the already-stored file in the configured
        ``StorageBackend`` (e.g. S3 object key).
    original_filename:
        The filename as supplied by the originating caller or provider.
    mime_type:
        MIME type of the file content.
    size_bytes:
        File size in bytes.
    checksum_sha256:
        Hex-encoded SHA-256 digest of the raw file bytes for integrity
        verification.
    discovery_result_id:
        Optional UUID string of the ``DiscoveryResult`` that produced this
        file artefact, enabling cross-context traceability.
    metadata:
        Arbitrary key-value bag for additional provenance information.
    """

    storage_key: str
    original_filename: str
    mime_type: str
    size_bytes: int
    checksum_sha256: str
    discovery_result_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


__all__ = [
    "DiscoveryRequest",
    "DiscoveryResultDTO",
    "EvidenceUploadRequest",
]
