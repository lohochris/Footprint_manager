# backend/apps/investigations/selectors/evidence_file_selector.py
"""Selector for read‑only access to EvidenceFile objects.

Provides filtering, searching, ordering and pagination while ensuring tenant isolation.
"""

from ..models.evidence import EvidenceFile
from .base import BaseSelector


class EvidenceFileSelector(BaseSelector):
    """Concrete selector for the EvidenceFile aggregate root."""

    model = EvidenceFile
    # Searchable fields – allow lookup by original or stored filename
    search_fields = ["original_filename", "stored_filename", "mime_type"]

    def _base_qs(self):
        """Eager‑load the related Evidence and the file field for efficiency."""
        return (
            super()
            ._base_qs()
            .select_related("evidence", "file")
        )
