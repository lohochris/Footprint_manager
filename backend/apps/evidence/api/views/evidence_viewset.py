from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiParameter, inline_serializer

from backend.apps.organizations.api.pagination import StandardResultsSetPagination
from backend.apps.organizations.models import Organization, OrganizationMember
from backend.apps.evidence.models import Evidence
from backend.apps.evidence.selectors import EvidenceSelector
from backend.apps.evidence.services import EvidenceService
from backend.apps.evidence.api.serializers import (
    EvidenceSerializer,
    EvidenceCreateSerializer,
    EvidenceCustodyEventSerializer,
    CustodyTransferSerializer,
)
from backend.apps.evidence.api.permissions import (
    CanUploadEvidence,
    CanViewEvidence,
    CanManageEvidence,
)


@extend_schema_view(
    list=extend_schema(
        summary="List Evidence",
        description="Retrieve a paginated list of evidence records for the resolved organization.",
        responses={200: EvidenceSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Retrieve Evidence Detail",
        description="Retrieve complete detailed representation of an evidence record.",
        responses={200: EvidenceSerializer},
    ),
    create=extend_schema(
        summary="Upload/Register Evidence",
        description="Upload a new evidence file. Runs through the validation, authorization, storage, and hash stages.",
        request=EvidenceCreateSerializer,
        responses={201: EvidenceSerializer},
    ),
    destroy=extend_schema(
        summary="Soft Delete Evidence",
        description="Soft delete an evidence record. Must be the active custodian.",
        responses={204: None},
    ),
)
class EvidenceViewSet(viewsets.ModelViewSet):
    """ViewSet for exposing the Evidence bounded context REST API."""

    queryset = Evidence.objects.all()
    serializer_class = EvidenceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "title"]

    def get_tenant(self):
        """Derive the tenant (Organization) from the request context."""
        user = self.request.user
        if not user.is_authenticated:
            return None

        # Check if they are admin or superuser to allow explicit selection
        is_privileged = user.is_superuser or user.is_staff
        org_id = None
        if is_privileged:
            org_id = self.request.query_params.get("organization_id") or self.request.data.get("organization_id")

        if org_id:
            try:
                return Organization.objects.get(id=org_id)
            except (Organization.DoesNotExist, ValueError):
                pass

        member = OrganizationMember.objects.filter(user=user, status="active").first()
        return member.organization if member else None

    def get_queryset(self):
        tenant = self.get_tenant()
        if not tenant:
            return Evidence.objects.none()
        return EvidenceSelector.base_queryset(tenant)

    def get_permissions(self):
        if self.action == "create":
            return [CanUploadEvidence()]
        elif self.action in ["list", "retrieve", "custody_history"]:
            return [CanViewEvidence()]
        elif self.action in ["update", "partial_update", "destroy", "transfer", "download"]:
            return [CanManageEvidence()]
        elif self.action == "verify":
            return [CanViewEvidence()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        tenant = self.get_tenant()
        if not tenant:
            raise DRFValidationError("A valid tenant organization context is required.")

        serializer = EvidenceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        file_obj = validated_data.pop("file")
        investigation_id = validated_data.pop("investigation_id", None)

        try:
            workspace_obj = validated_data.get("workspace")
            evidence = EvidenceService.upload_evidence(
                user=request.user,
                organization=tenant,
                workspace_id=workspace_obj.id if workspace_obj else None,
                title=validated_data.get("title"),
                description=validated_data.get("description", ""),
                classification=validated_data.get("classification", "restricted"),
                file_obj=file_obj,
                investigation_id=investigation_id,
            )
        except DjangoValidationError as exc:
            raise DRFValidationError(exc.message_dict if hasattr(exc, "message_dict") else str(exc))

        response_serializer = EvidenceSerializer(evidence, context=self.get_serializer_context())
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

    @extend_schema(
        summary="Secure Download URL",
        description="Generates a temporary signed download URL for the evidence file. Enforces active custodian lock.",
        responses={
            200: inline_serializer(
                name="EvidenceDownloadResponse",
                fields={
                    "download_url": serializers.CharField(),
                    "checksum_sha256": serializers.CharField(),
                    "original_filename": serializers.CharField(),
                },
            )
        },
    )
    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        evidence = self.get_object()
        if not hasattr(evidence, "file_meta") or not evidence.file_meta:
            return Response(
                {"detail": "No file associated with this evidence."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Generate download URL using LocalStorageProvider
        from backend.apps.evidence.services.pipeline_stages import storage_provider
        url = storage_provider.generate_download_url(evidence.file_meta.file.name)

        return Response(
            {
                "download_url": url,
                "checksum_sha256": evidence.file_meta.checksum_sha256,
                "original_filename": evidence.file_meta.original_filename,
            },
            status=status.HTTP_200_RESPONSE if hasattr(status, "HTTP_200_RESPONSE") else status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Transfer Custody",
        description="Transfer custody of the evidence item to another user. Only active custodian can transfer.",
        request=CustodyTransferSerializer,
        responses={200: EvidenceSerializer},
    )
    @action(detail=True, methods=["post"])
    def transfer(self, request, pk=None):
        evidence = self.get_object()
        serializer = CustodyTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant = self.get_tenant()
        try:
            updated_evidence = EvidenceService.transfer_custody(
                user=request.user,
                organization=tenant,
                evidence=evidence,
                new_custodian=serializer.validated_data["new_custodian"],
                notes=serializer.validated_data["notes"],
            )
        except (DjangoValidationError, PermissionDenied) as exc:
            raise DRFValidationError(str(exc))

        response_serializer = EvidenceSerializer(updated_evidence, context=self.get_serializer_context())
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Verify File Integrity",
        description="Triggers the integrity verification pipeline (storage read and SHA-256 compare).",
        responses={
            200: inline_serializer(
                name="EvidenceVerifyResponse",
                fields={
                    "status": serializers.CharField(),
                    "passed": serializers.BooleanField(),
                },
            )
        },
    )
    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        evidence = self.get_object()
        tenant = self.get_tenant()
        try:
            updated_evidence = EvidenceService.verify_integrity(
                user=request.user,
                organization=tenant,
                evidence=evidence,
            )
        except DjangoValidationError as exc:
            raise DRFValidationError(str(exc))

        passed = (updated_evidence.status == "verified")
        return Response(
            {
                "status": updated_evidence.status,
                "passed": passed,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Custody History",
        description="Retrieves a list of all custody transfer events for this evidence record.",
        responses={200: EvidenceCustodyEventSerializer(many=True)},
    )
    @action(detail=True, methods=["get"], url_path="custody-history")
    def custody_history(self, request, pk=None):
        evidence = self.get_object()
        events = EvidenceSelector.get_custody_history(evidence)
        serializer = EvidenceCustodyEventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
