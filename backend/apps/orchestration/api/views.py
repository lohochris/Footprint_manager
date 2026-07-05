from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from backend.apps.orchestration.dto import PlaybookExecutionParams
from backend.apps.orchestration.services import WorkflowService
from .serializers import PlaybookExecuteSerializer, WorkflowExecutionSerializer
import uuid

class OrchestrationViewSet(viewsets.ViewSet):
    """
    API for managing workflow orchestrations and playbooks.
    """

    @extend_schema(request=PlaybookExecuteSerializer, responses={201: WorkflowExecutionSerializer})
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        serializer = PlaybookExecuteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant_id = getattr(request, 'tenant_id', uuid.uuid4()) # Mocks middleware
        creator_id = request.user.id if request.user.is_authenticated else None

        params = PlaybookExecutionParams(
            tenant_id=tenant_id,
            playbook_version_id=uuid.UUID(pk),
            workspace_id=serializer.validated_data.get('workspace_id'),
            creator_id=creator_id,
            variables=serializer.validated_data.get('variables', {})
        )

        dto = WorkflowService.start_execution(params)

        return Response(WorkflowExecutionSerializer(dto).data, status=status.HTTP_201_CREATED)
