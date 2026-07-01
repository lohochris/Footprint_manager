from rest_framework import serializers

from ..models.investigation import Investigation


class InvestigationDetailSerializer(serializers.ModelSerializer):
    """Read‑only representation of an Investigation, including nested activities."""

    activities = serializers.SerializerMethodField()

    class Meta:
        model = Investigation
        fields = (
            "id",
            "case_number",
            "title",
            "description",
            "status",
            "priority",
            "classification",
            "visibility",
            "risk_level",
            "tags",
            "metadata",
            "owner",
            "lead_investigator",
            "assigned_investigators",
            "created_at",
            "updated_at",
            "is_archived",
            "is_deleted",
            "activities",
        )
        read_only_fields = fields

    def get_activities(self, obj):
        # Return activity list serialized minimally
        return [
            {
                "action_type": act.action_type,
                "actor": act.actor.id if act.actor else None,
                "timestamp": act.timestamp,
                "metadata": act.metadata,
            }
            for act in obj.activities.all()
        ]
