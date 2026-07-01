# backend/apps/investigations/selectors/evidence_selector.py
"""Selector for read‑only access to Evidence objects.

Provides filtering, searching, ordering and pagination while ensuring tenant isolation.
"""

from ..models.evidence import Evidence
from .base import BaseSelector


class EvidenceSelector(BaseSelector):
    """Concrete selector for the Evidence aggregate root."""

    model = Evidence
    # Fields that are searchable via the ``search`` argument
    search_fields = ["title", "description"]

    def _base_qs(self):
        # Eager‑load the attached file
        return super()._base_qs().select_related("file")
