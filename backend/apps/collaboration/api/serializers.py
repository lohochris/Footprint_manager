from rest_framework import serializers
from ..models import Task, Notification

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id", "case_workspace_id", "title", "description",
            "status", "priority", "assignee_id", "creator_id",
            "due_date", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id", "user_id", "category", "priority",
            "title", "body", "is_read", "created_at"
        ]
        read_only_fields = ["id", "user_id", "created_at"]

class AssignTaskSerializer(serializers.Serializer):
    assignee_id = serializers.UUIDField(required=True)
