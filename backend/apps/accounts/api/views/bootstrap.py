from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from backend.apps.accounts.serializers import UserSerializer
from backend.apps.organizations.services import OrganizationService
from backend.apps.organizations.serializers.organization import OrganizationSerializer
from backend.apps.organizations.serializers.workspace import WorkspaceSerializer

class BootstrapAPIView(APIView):
    """
    Returns the initial state required to bootstrap the frontend application:
    - Current authenticated user
    - Organizations the user belongs to
    - Workspaces within those organizations
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        # 1. Serialize User
        user_data = UserSerializer(user).data

        # 2. Fetch and Serialize Organizations
        organizations = OrganizationService.list_user_organizations(user.id)
        org_data = OrganizationSerializer(organizations, many=True).data

        # 3. Fetch Workspaces (Workspaces linked to those organizations)
        # Assuming the simplest approach is to fetch workspaces per organization.
        # If WorkspaceService.list_user_workspaces exists we would use it,
        # but let's safely extract them from the user's organizations if they are prefetched,
        # or just fetch them by iterating if necessary.
        # A more robust backend might have a `WorkspaceService.list_user_workspaces(user.id)`.
        # Let's check if the orgs have `workspaces` related name.
        all_workspaces = []
        for org in organizations:
            # Safely fetch active workspaces for each org
            for workspace in org.workspaces.filter(is_archived=False):
                all_workspaces.append(workspace)

        workspace_data = WorkspaceSerializer(all_workspaces, many=True).data

        return Response({
            "user": user_data,
            "organizations": org_data,
            "workspaces": workspace_data,
            "permissions": [] # RBAC integration placeholder
        })
