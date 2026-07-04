from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiParameter, inline_serializer

from backend.apps.organizations.api.pagination import StandardResultsSetPagination
from backend.apps.organizations.models import Organization, OrganizationMember
from ...models import (
    Investigation,
    InvestigationMember,
    InvestigationTarget,
    EvidenceReference,
    InvestigationTimelineEvent,
    InvestigationComment,
    InvestigationStatus,
)
from ...selectors.investigation_selector import InvestigationSelector
from ...services.investigation_service import InvestigationService
from ...validators.investigation_validator import validate_status_transition
from ..serializers import (
    InvestigationSerializer,
    InvestigationCreateSerializer,
    InvestigationUpdateSerializer,
    InvestigationDetailSerializer,
    InvestigationMemberSerializer,
    InvestigationTargetSerializer,
    EvidenceReferenceSerializer,
    InvestigationTimelineEventSerializer,
    InvestigationCommentSerializer,
)
from ..permissions import (
    CanCreateInvestigation,
    CanViewInvestigation,
    CanUpdateInvestigation,
    CanAssignMembers,
    CanChangeStatus,
    CanArchiveInvestigation,
    CanRestoreInvestigation,
    CanManageEvidence,
    CanComment,
)
from ..filters import InvestigationFilter


@extend_schema_view(
    list=extend_schema(
        summary="List Investigations",
        description="Retrieve a paginated list of investigations for the resolved organization.",
        responses={200: InvestigationSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Retrieve Investigation Detail",
        description="Retrieve complete detailed representation of an investigation, including nested members, targets, evidence, timeline, and comments.",
        responses={200: InvestigationDetailSerializer},
    ),
    create=extend_schema(
        summary="Create Investigation",
        description="Create a new investigation. Delegates to the service pipeline.",
        request=InvestigationCreateSerializer,
        responses={201: InvestigationSerializer},
        examples=[
            OpenApiExample(
                "Create Request Example",
                value={
                    "title": "Credential Stuffing Campaign",
                    "description": "Investigating brute force logins from subnet 192.0.2.0/24",
                    "workspace": None,
                    "investigation_type": "cybercrime",
                    "priority": "high",
                    "classification": "internal",
                    "tags": ["brute-force", "subnet-block"],
                    "metadata": {"source_ip": "192.0.2.1"},
                },
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        summary="Update Investigation",
        description="Modify mutable fields of an investigation. Delegates to the service pipeline.",
        request=InvestigationUpdateSerializer,
        responses={200: InvestigationSerializer},
    ),
    partial_update=extend_schema(
        summary="Patch Investigation",
        description="Partially modify mutable fields of an investigation. Delegates to the service pipeline.",
        request=InvestigationUpdateSerializer,
        responses={200: InvestigationSerializer},
    ),
    destroy=extend_schema(
        summary="Delete Investigation",
        description="Soft-delete an investigation. Delegates to the service pipeline.",
        responses={204: None},
    ),
)
class InvestigationViewSet(viewsets.ModelViewSet):
    """ViewSet for exposing the Investigation bounded context REST API.

    Delegates all persistence operations to the certified InvestigationService
    and reads to the InvestigationSelector. Strictly orchestrates requests and
    enforces authorization/tenant isolation.
    """

    queryset = Investigation.objects.all()
    serializer_class = InvestigationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = InvestigationFilter
    search_fields = ["title", "description", "case_number"]
    ordering_fields = ["created_at", "updated_at", "title"]

    def get_tenant(self):
        """Derive the tenant (Organization) from the request context.

        Allows explicit selection for privileged admins/superusers,
        but strictly derives from authenticated context for normal users.
        """
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
            return Investigation.objects.none()
        # Soft deleted items are excluded
        return Investigation.objects.filter(organization=tenant, is_deleted=False)

    def get_serializer_class(self):
        if self.action == "create":
            return InvestigationCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return InvestigationUpdateSerializer
        elif self.action == "retrieve":
            return InvestigationDetailSerializer
        return InvestigationSerializer

    def get_permissions(self):
        if self.action == "create":
            return [CanCreateInvestigation()]
        elif self.action in ["retrieve", "list", "timeline"]:
            return [CanViewInvestigation()]
        elif self.action in ["update", "partial_update"]:
            return [CanUpdateInvestigation()]
        elif self.action == "destroy":
            return [CanArchiveInvestigation()]
        elif self.action == "assign":
            return [CanAssignMembers()]
        elif self.action in ["status", "change_status"]:
            return [CanChangeStatus()]
        elif self.action == "archive":
            return [CanArchiveInvestigation()]
        elif self.action == "restore":
            return [CanRestoreInvestigation()]
        elif self.action == "targets":
            if self.request.method == "POST":
                return [CanUpdateInvestigation()]
            return [CanViewInvestigation()]
        elif self.action == "evidence":
            if self.request.method == "POST":
                return [CanManageEvidence()]
            return [CanViewInvestigation()]
        elif self.action == "comments":
            if self.request.method == "POST":
                return [CanComment()]
            return [CanViewInvestigation()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response_serializer = InvestigationSerializer(
            serializer.instance,
            context=self.get_serializer_context()
        )
        headers = self.get_success_headers(serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        response_serializer = InvestigationSerializer(
            serializer.instance,
            context=self.get_serializer_context()
        )
        return Response(response_serializer.data)

    def perform_create(self, serializer):
        user = self.request.user
        organization = self.get_tenant()
        if not organization:
            raise DRFValidationError("Organization could not be resolved from your context.")

        # Pop workspace from data to avoid duplicate argument unpacking in service layer
        data = dict(serializer.validated_data)
        workspace = data.pop("workspace", None)

        try:
            investigation = InvestigationService.create_investigation(
                user=user,
                organization=organization,
                workspace=workspace,
                data=data,
            )
            serializer.instance = investigation
        except (DjangoValidationError, ValueError) as exc:
            raise DRFValidationError(str(exc))

    def perform_update(self, serializer):
        user = self.request.user
        investigation = self.get_object()
        data = serializer.validated_data

        try:
            investigation = InvestigationService.update_investigation(
                user=user,
                investigation=investigation,
                data=data,
            )
            serializer.instance = investigation
        except (DjangoValidationError, ValueError) as exc:
            raise DRFValidationError(str(exc))

    def perform_destroy(self, instance):
        user = self.request.user
        try:
            InvestigationService.soft_delete(user=user, investigation=instance)
        except (DjangoValidationError, ValueError) as exc:
            raise DRFValidationError(str(exc))

    @extend_schema(
        summary="Assign Investigators",
        description="Assign a list of investigator IDs to the investigation. Delegates to the service pipeline.",
        request=inline_serializer(
            name="AssignInvestigatorsRequest",
            fields={
                "investigator_ids": serializers.ListField(
                    child=serializers.IntegerField(),
                    help_text="List of User IDs to assign as investigators",
                )
            },
        ),
        responses={200: None},
        examples=[
            OpenApiExample(
                "Assign Example",
                value={"investigator_ids": [1, 2]},
                request_only=True,
            )
        ],
    )
    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        investigation = self.get_object()
        investigator_ids = request.data.get("investigator_ids", [])
        try:
            InvestigationService.assign_investigators(request.user, investigation, investigator_ids)
            return Response({"detail": "Investigators assigned successfully."}, status=status.HTTP_200_OK)
        except (DjangoValidationError, ValueError) as exc:
            raise DRFValidationError(str(exc))

    @extend_schema(
        summary="Change Status",
        description="Update the status of the investigation with status transition validations. Delegates to the service pipeline.",
        request=None,
        responses={200: None},
        parameters=[
            OpenApiParameter(
                name="status",
                type=str,
                description="The target status (e.g. active, completed, suspended)",
                required=True,
            )
        ],
        examples=[
            OpenApiExample(
                "Status Change Example",
                value={"status": "active"},
                request_only=True,
            )
        ],
    )
    @action(detail=True, methods=["post"])
    def status(self, request, pk=None):
        investigation = self.get_object()
        new_status = request.data.get("status")
        try:
            validate_status_transition(investigation.status, new_status)
            InvestigationService.change_status(request.user, investigation, new_status)
            return Response({"detail": f"Status updated to {new_status}."}, status=status.HTTP_200_OK)
        except (DjangoValidationError, ValueError) as exc:
            raise DRFValidationError(str(exc))

    @extend_schema(
        summary="Archive Investigation",
        description="Archive the investigation. Delegates to the service pipeline.",
        request=None,
        responses={200: None},
    )
    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        investigation = self.get_object()
        try:
            InvestigationService.archive(request.user, investigation)
            return Response({"detail": "Investigation archived successfully."}, status=status.HTTP_200_OK)
        except (DjangoValidationError, ValueError) as exc:
            raise DRFValidationError(str(exc))

    @extend_schema(
        summary="Restore Investigation",
        description="Restore an archived investigation. Delegates to the service pipeline.",
        request=None,
        responses={200: None},
    )
    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        investigation = self.get_object()
        try:
            InvestigationService.restore_investigation(request.user, investigation)
            return Response({"detail": "Investigation restored successfully."}, status=status.HTTP_200_OK)
        except (DjangoValidationError, ValueError) as exc:
            raise DRFValidationError(str(exc))

    @extend_schema(
        summary="Manage Targets",
        description="Add a target (POST) or retrieve all targets (GET) associated with this investigation.",
        request=InvestigationTargetSerializer,
        responses={
            200: InvestigationTargetSerializer(many=True),
            201: InvestigationTargetSerializer,
        },
    )
    @action(detail=True, methods=["get", "post"])
    def targets(self, request, pk=None):
        investigation = self.get_object()
        if request.method == "POST":
            serializer = InvestigationTargetSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            try:
                target = serializer.save(investigation=investigation, created_by=request.user)
                out_serializer = InvestigationTargetSerializer(target)
                return Response(out_serializer.data, status=status.HTTP_201_CREATED)
            except DjangoValidationError as exc:
                raise DRFValidationError(str(exc))
        else:
            targets = InvestigationSelector.get_targets(investigation)
            serializer = InvestigationTargetSerializer(targets, many=True)
            return Response(serializer.data)

    @extend_schema(
        summary="Manage Evidence",
        description="Add an evidence reference (POST) or retrieve all evidence references (GET) associated with this investigation.",
        request=EvidenceReferenceSerializer,
        responses={
            200: EvidenceReferenceSerializer(many=True),
            201: EvidenceReferenceSerializer,
        },
    )
    @action(detail=True, methods=["get", "post"])
    def evidence(self, request, pk=None):
        investigation = self.get_object()
        if request.method == "POST":
            serializer = EvidenceReferenceSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            try:
                evidence = serializer.save(investigation=investigation, linked_by=request.user, created_by=request.user)
                out_serializer = EvidenceReferenceSerializer(evidence)
                return Response(out_serializer.data, status=status.HTTP_201_CREATED)
            except DjangoValidationError as exc:
                raise DRFValidationError(str(exc))
        else:
            evidence_refs = EvidenceReference.objects.filter(investigation=investigation)
            serializer = EvidenceReferenceSerializer(evidence_refs, many=True)
            return Response(serializer.data)

    @extend_schema(
        summary="Manage Comments",
        description="Add a comment (POST) or retrieve all comments (GET) associated with this investigation.",
        request=InvestigationCommentSerializer,
        responses={
            200: InvestigationCommentSerializer(many=True),
            201: InvestigationCommentSerializer,
        },
    )
    @action(detail=True, methods=["get", "post"])
    def comments(self, request, pk=None):
        investigation = self.get_object()
        if request.method == "POST":
            serializer = InvestigationCommentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            try:
                comment = serializer.save(investigation=investigation, author=request.user, created_by=request.user)
                out_serializer = InvestigationCommentSerializer(comment)
                return Response(out_serializer.data, status=status.HTTP_201_CREATED)
            except DjangoValidationError as exc:
                raise DRFValidationError(str(exc))
        else:
            comments = InvestigationSelector.get_comments(investigation)
            serializer = InvestigationCommentSerializer(comments, many=True)
            return Response(serializer.data)

    @extend_schema(
        summary="Retrieve Timeline",
        description="Retrieve the chronological list of timeline events for the investigation.",
        responses={200: InvestigationTimelineEventSerializer(many=True)},
    )
    @action(detail=True, methods=["get"])
    def timeline(self, request, pk=None):
        investigation = self.get_object()
        timeline = InvestigationSelector.get_timeline(investigation)
        serializer = InvestigationTimelineEventSerializer(timeline, many=True)
        return Response(serializer.data)
