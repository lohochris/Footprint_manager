from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from backend.apps.ai_assistant.models import AssistantSession, AssistantMessage
from backend.apps.ai_assistant.api.serializers import (
    AssistantSessionSerializer,
    AssistantMessageSerializer,
    ChatRequestSerializer,
    ChatResponseSerializer,
)
from backend.apps.ai_assistant.services.engine import AIIntelligenceEngine

class AssistantSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Assistant Sessions and chatting."""
    serializer_class = AssistantSessionSerializer
    queryset = AssistantSession.objects.all()

    def get_queryset(self):
        # Tenant isolation would be enforced by a middleware/mixin in production
        tenant_id = self.request.tenant_id if hasattr(self.request, "tenant_id") else None
        if tenant_id:
            return self.queryset.filter(tenant_id=tenant_id)
        return self.queryset

    @action(detail=True, methods=["post"])
    def chat(self, request, pk=None):
        """Send a message to the AI Assistant."""
        session = self.get_object()
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_message = serializer.validated_data["message"]

        # In a real DRF app, we would resolve tenant_id/workspace_id from request.
        engine = AIIntelligenceEngine()
        response_text = engine.chat(session_id=str(session.id), user_message=user_message)

        return Response(
            ChatResponseSerializer({"response": response_text, "session_id": session.id}).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        """Retrieve history of messages for a session."""
        session = self.get_object()
        messages = AssistantMessage.objects.filter(session=session).order_by("created_at")
        serializer = AssistantMessageSerializer(messages, many=True)
        return Response(serializer.data)
