from rest_framework import serializers

from ...models import GovernancePolicy, ApprovalWorkflow, ApprovalRequest

class GovernancePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = GovernancePolicy
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "updated_by", "workspace", "organization")

class ApprovalWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalWorkflow
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "updated_by", "workspace", "organization")

class ApprovalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalRequest
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "updated_by", "workspace", "organization", "status")
