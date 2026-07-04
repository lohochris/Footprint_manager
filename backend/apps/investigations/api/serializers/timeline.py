from rest_framework import serializers
from backend.apps.investigations.models import InvestigationTimelineEvent


class InvestigationTimelineEventSerializer(serializers.ModelSerializer):
    """Serializer for the InvestigationTimelineEvent model (Read-only)."""

    class Meta:
        model = InvestigationTimelineEvent
        fields = (
            "id",
            "investigation",
            "event_type",
            "description",
            "timestamp",
            "metadata",
        )
        read_only_fields = fields
