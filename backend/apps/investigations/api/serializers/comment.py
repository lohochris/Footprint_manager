from rest_framework import serializers
from backend.apps.investigations.models import InvestigationComment


class InvestigationCommentSerializer(serializers.ModelSerializer):
    """Serializer for the InvestigationComment model."""

    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = InvestigationComment
        fields = (
            "id",
            "investigation",
            "author",
            "author_username",
            "rich_content",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "investigation", "author", "created_at", "updated_at")
