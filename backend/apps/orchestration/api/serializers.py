from rest_framework import serializers

class PlaybookExecuteSerializer(serializers.Serializer):
    workspace_id = serializers.UUIDField(required=False, allow_null=True)
    variables = serializers.DictField(required=False, default=dict)

class WorkflowExecutionSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    playbook_version_id = serializers.UUIDField()
    status = serializers.CharField()
    outputs = serializers.DictField()
