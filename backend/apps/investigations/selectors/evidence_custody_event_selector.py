# backend/apps/investigations/selectors/evidence_custody_event_selector.py
"""Selector for read‑only access to EvidenceCustodyEvent objects.

Provides filtering, searching, ordering and pagination while ensuring tenant isolation.
"""

from ..models.evidence import EvidenceCustodyEvent
from .base import BaseSelector


class EvidenceCustodyEventSelector(BaseSelector):
    """Concrete selector for the EvidenceCustodyEvent aggregate root."""

    model = EvidenceCustodyEvent
    # Searchable fields – holder username and notes
    search_fields = ["holder__username", "notes"]

    def _base_qs(self):
        """Eager‑load related evidence and holder for efficiency."""
        return (
            super()
            ._base_qs()
            .select_related("evidence", "holder")
        )
