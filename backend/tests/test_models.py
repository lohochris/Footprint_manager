"""Test model mixin definitions."""

from backend.common.models import BaseModel, SoftDeleteModel, TenantAwareMixin, TimestampMixin, UUIDMixin
from backend.core.models import BaseModel as CoreBaseModel
from django.db import models


class TestMixins:
    def test_uuid_mixin_has_uuid_primary_key(self):
        class Sample(UUIDMixin):
            class Meta:
                app_label = "common"

        field = Sample._meta.get_field("id")
        assert isinstance(field, models.UUIDField)
        assert field.primary_key is True

    def test_timestamp_mixin_fields(self):
        class Sample(TimestampMixin):
            class Meta:
                app_label = "common"

        field_names = [f.name for f in Sample._meta.get_fields()]
        assert "created_at" in field_names
        assert "updated_at" in field_names

    def test_base_model_combines_uuid_and_timestamps(self):
        class Sample(BaseModel):
            class Meta:
                app_label = "common"

        field_names = [f.name for f in Sample._meta.get_fields()]
        assert "id" in field_names
        assert "created_at" in field_names
        assert "updated_at" in field_names

    def test_common_model_exports_remain_core_compatible(self):
        assert BaseModel is CoreBaseModel

    def test_tenant_aware_mixin_has_organization_id(self):
        class Sample(TenantAwareMixin):
            class Meta:
                app_label = "common"

        field = Sample._meta.get_field("organization_id")
        assert isinstance(field, models.UUIDField)

    def test_soft_delete_methods_exist(self):
        class Sample(SoftDeleteModel):
            class Meta:
                app_label = "common"

        assert hasattr(Sample, "soft_delete")
        assert hasattr(Sample, "restore")
