from rest_framework import serializers
from backend.apps.investigations.models import InvestigationTarget


class InvestigationTargetSerializer(serializers.ModelSerializer):
    """Serializer for the InvestigationTarget model."""

    class Meta:
        model = InvestigationTarget
        fields = (
            "id",
            "investigation",
            "target_type",
            "display_name",
            "confidence",
            "notes",
            "metadata",
            "source",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "investigation", "created_at", "updated_at")
