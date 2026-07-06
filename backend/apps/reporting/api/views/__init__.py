from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ....models import (
    Report,
    ReportExport,
    ReportSection,
    ReportTemplate,
    ReportVersion,
)
from ..serializers import (
    ReportExportSerializer,
    ReportSectionSerializer,
    ReportSerializer,
    ReportTemplateSerializer,
    ReportVersionSerializer,
)


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        self.get_object()
        # Integration with PublishingService
        return Response({"status": "published"})

    @action(detail=True, methods=["post"])
    def generate_preview(self, request, pk=None):
        self.get_object()
        # Integration with ReportService to assemble content and template provider to render
        return Response({"status": "preview_generated"})


class ReportTemplateViewSet(viewsets.ModelViewSet):
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer


class ReportSectionViewSet(viewsets.ModelViewSet):
    queryset = ReportSection.objects.all()
    serializer_class = ReportSectionSerializer


class ReportVersionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReportVersion.objects.all()
    serializer_class = ReportVersionSerializer

    @action(detail=True, methods=["post"])
    def export(self, request, pk=None):
        self.get_object()
        format = request.data.get("format", "PDF")
        # Integration with ExportService
        return Response({"status": "export_started", "format": format})


class ReportExportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReportExport.objects.all()
    serializer_class = ReportExportSerializer
