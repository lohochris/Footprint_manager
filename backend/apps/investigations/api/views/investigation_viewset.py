from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response

from ..models.investigation import Investigation
from ..permissions.investigation_permission import (
    CanArchiveRestore,
    IsInvestigationOwnerOrLeadOrAdmin,
)
from ..serializers.investigation_create_update import InvestigationCreateUpdateSerializer
from ..serializers.investigation_detail import InvestigationDetailSerializer
from ..services.investigation_service import InvestigationService
from ..validators.investigation_validator import validate_status_transition


class InvestigationViewSet(viewsets.ModelViewSet):
    """ViewSet for Investigation CRUD and custom actions.
    Business logic is delegated to the service layer; this class only orchestrates.
    """

    queryset = Investigation.objects.all()
    serializer_class = InvestigationDetailSerializer
    permission_classes = [IsInvestigationOwnerOrLeadOrAdmin]

    def get_queryset(self):
        # Scope to tenant (organization) from request; assuming request.user.org attribute
        organization = getattr(self.request.user, "organization", None)
        if not organization:
            return Investigation.objects.none()
        return Investigation.objects.filter(organization=organization, is_deleted=False)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return InvestigationCreateUpdateSerializer
        return InvestigationDetailSerializer

    def perform_create(self, serializer):
        user = self.request.user
        organization = user.organization
        workspace = getattr(user, "workspace", None)
        data = serializer.validated_data
        investigation = InvestigationService.create_investigation(user, organization, workspace, data)
        serializer.instance = investigation

    def perform_update(self, serializer):
        user = self.request.user
        investigation = self.get_object()
        data = serializer.validated_data
        InvestigationService.update_investigation(user, investigation, data)
        serializer.instance = investigation

    @action(detail=True, methods=["post"], permission_classes=[IsInvestigationOwnerOrLeadOrAdmin])
    def assign(self, request, pk=None):
        investigation = self.get_object()
        ids = request.data.get("investigator_ids", [])
        InvestigationService.assign_investigators(request.user, investigation, ids)
        return Response({"detail": "Investigators assigned."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsInvestigationOwnerOrLeadOrAdmin])
    def transfer_ownership(self, request, pk=None):
        investigation = self.get_object()
        new_owner_id = request.data.get("new_owner_id")
        new_owner = get_object_or_404(Investigation._meta.get_field('owner').related_model, pk=new_owner_id)
        InvestigationService.transfer_ownership(request.user, investigation, new_owner)
        return Response({"detail": "Ownership transferred."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[CanArchiveRestore])
    def archive(self, request, pk=None):
        investigation = self.get_object()
        InvestigationService.archive(request.user, investigation)
        return Response({"detail": "Investigation archived."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[CanArchiveRestore])
    def restore(self, request, pk=None):
        investigation = self.get_object()
        InvestigationService.restore(request.user, investigation)
        return Response({"detail": "Investigation restored."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsInvestigationOwnerOrLeadOrAdmin])
    def change_status(self, request, pk=None):
        investigation = self.get_object()
        new_status = request.data.get("status")
        try:
            validate_status_transition(investigation.status, new_status)
        except DRFValidationError as exc:
            raise DRFValidationError(str(exc))
        InvestigationService.change_status(request.user, investigation, new_status)
        return Response({"detail": f"Status changed to {new_status}."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsInvestigationOwnerOrLeadOrAdmin])
    def change_priority(self, request, pk=None):
        investigation = self.get_object()
        new_priority = request.data.get("priority")
        # Re‑use validator
        from ..validators.investigation_validator import validate_priority
        try:
            validate_priority(new_priority)
        except DRFValidationError as exc:
            raise DRFValidationError(str(exc))
        InvestigationService.update_investigation(request.user, investigation, {"priority": new_priority})
        return Response({"detail": f"Priority changed to {new_priority}."}, status=status.HTTP_200_OK)
