from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from backend.apps.accounts.models import User
from backend.apps.accounts.serializers import UserSerializer

class UserViewSet(viewsets.GenericViewSet):
    """
    API endpoints for current user retrieval.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"])
    def me(self, request):
        """
        Return the currently authenticated user's profile.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
