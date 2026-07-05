from rest_framework import serializers
from backend.apps.ai_assistant.models import AssistantSession, AssistantMessage, AIFeedback

class AssistantSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantSession
        fields = ["id", "title", "status", "workspace_id", "investigation_id", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

class AssistantMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantMessage
        fields = ["id", "session_id", "role", "content", "created_at"]
        read_only_fields = ["id", "created_at"]

class AIFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIFeedback
        fields = ["id", "message_id", "is_positive", "comment", "created_at"]
        read_only_fields = ["id", "created_at"]

class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)

class ChatResponseSerializer(serializers.Serializer):
    response = serializers.CharField()
    session_id = serializers.UUIDField()
