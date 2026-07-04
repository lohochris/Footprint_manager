from rest_framework import serializers
from backend.apps.investigations.models import InvestigationMember


class InvestigationMemberSerializer(serializers.ModelSerializer):
    """Serializer for the InvestigationMember model."""

    user_username = serializers.CharField(source="user.username", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = InvestigationMember
        fields = (
            "id",
            "investigation",
            "user",
            "user_username",
            "user_email",
            "role",
            "permission_level",
            "assigned_date",
            "active",
        )
        read_only_fields = ("id", "investigation", "assigned_date")
