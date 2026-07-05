from rest_framework import viewsets

from ....models import GovernancePolicy, ApprovalWorkflow, ApprovalRequest
from ..serializers import GovernancePolicySerializer, ApprovalWorkflowSerializer, ApprovalRequestSerializer

class GovernancePolicyViewSet(viewsets.ModelViewSet):
    queryset = GovernancePolicy.objects.all()
    serializer_class = GovernancePolicySerializer

    def get_queryset(self):
        # Filtering for tenant would happen here based on request.user
        return super().get_queryset()

class ApprovalWorkflowViewSet(viewsets.ModelViewSet):
    queryset = ApprovalWorkflow.objects.all()
    serializer_class = ApprovalWorkflowSerializer

    def get_queryset(self):
        return super().get_queryset()

class ApprovalRequestViewSet(viewsets.ModelViewSet):
    queryset = ApprovalRequest.objects.all()
    serializer_class = ApprovalRequestSerializer

    def get_queryset(self):
        return super().get_queryset()
