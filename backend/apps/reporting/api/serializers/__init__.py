from rest_framework import serializers

from ...models import (
    Report,
    ReportExport,
    ReportSection,
    ReportTemplate,
    ReportVersion,
)


class ReportTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportTemplate
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "workspace", "organization")


class ReportSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSection
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "workspace", "organization")


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "workspace", "organization", "version", "published_at")


class ReportVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportVersion
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "workspace", "organization")


class ReportExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportExport
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "workspace", "organization")
