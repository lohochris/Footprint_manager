# backend/apps/osint/tests/test_providers.py
"""Unit tests for the OSINT provider interface and registry.

All tests run entirely offline — no database, no network, no Django ORM.
Verifies:
  - BaseDiscoveryProvider ABC cannot be instantiated directly.
  - NoOpDiscoveryProvider satisfies the full contract.
  - DiscoveryProviderRegistry enforces uniqueness and priority ordering.
  - Free-function wrappers delegate to the singleton registry.
  - EvidenceUploadRequest DTO contains no Django file primitives.
"""

import inspect
import sys
import uuid

import pytest

from backend.apps.osint.dto import EvidenceUploadRequest
from backend.apps.osint.providers.base import BaseDiscoveryProvider
from backend.apps.osint.providers.noop_provider import NoOpDiscoveryProvider
from backend.apps.osint.providers.provider_metadata import DiscoveryHealthStatus
from backend.apps.osint.providers.registry import (
    DiscoveryProviderRegistry,
)


# ---------------------------------------------------------------------------
# BaseDiscoveryProvider ABC
# ---------------------------------------------------------------------------

class TestBaseDiscoveryProvider:
    def test_cannot_instantiate_abstract_class(self):
        with pytest.raises(TypeError):
            BaseDiscoveryProvider()  # type: ignore[abstract]

    def test_has_all_seven_abstract_methods(self):
        abstract_methods = {
            name
            for name, member in inspect.getmembers(BaseDiscoveryProvider)
            if getattr(member, "__isabstractmethod__", False)
        }
        expected = {
            "initialize",
            "health_check",
            "capabilities",
            "supports",
            "validate_target",
            "discover",
            "normalize",
        }
        assert expected <= abstract_methods, (
            f"Missing abstract methods: {expected - abstract_methods}"
        )


# ---------------------------------------------------------------------------
# NoOpDiscoveryProvider
# ---------------------------------------------------------------------------

class TestNoOpDiscoveryProvider:
    def setup_method(self):
        self.provider = NoOpDiscoveryProvider()

    def test_is_concrete_subclass(self):
        assert isinstance(self.provider, BaseDiscoveryProvider)

    def test_initialize_is_noop(self):
        # Must not raise
        self.provider.initialize()

    def test_health_check_returns_healthy(self):
        status = self.provider.health_check()
        assert isinstance(status, DiscoveryHealthStatus)
        assert status.healthy is True
        assert "NoOp" in status.message

    def test_unhealthy_scenario(self):
        provider = NoOpDiscoveryProvider(healthy=False)
        status = provider.health_check()
        assert status.healthy is False

    def test_capabilities_returns_list_of_strings(self):
        caps = self.provider.capabilities()
        assert isinstance(caps, list)
        assert all(isinstance(c, str) for c in caps)

    def test_supports_declared_capabilities(self):
        for cap in self.provider.capabilities():
            assert self.provider.supports(cap) is True

    def test_supports_returns_false_for_unknown(self):
        assert self.provider.supports("unknown_capability_xyz") is False

    def test_validate_target_accepts_any_dict(self):
        # Should not raise for any input
        self.provider.validate_target({})
        self.provider.validate_target({"email": "test@example.com"})

    def test_discover_returns_list_of_dicts(self):
        results = self.provider.discover({"email": "test@example.com"})
        assert isinstance(results, list)
        assert all(isinstance(r, dict) for r in results)

    def test_discover_result_count_matches_constructor(self):
        provider_0 = NoOpDiscoveryProvider(result_count=0)
        provider_3 = NoOpDiscoveryProvider(result_count=3)
        assert len(provider_0.discover({})) == 0
        assert len(provider_3.discover({})) == 3

    def test_normalize_returns_dict_with_title(self):
        raw = self.provider.discover({})[0]
        normalised = self.provider.normalize(raw)
        assert isinstance(normalised, dict)
        assert "title" in normalised

    def test_priority_is_9999(self):
        """NoOp must have lowest priority to avoid production selection."""
        assert NoOpDiscoveryProvider.priority == 9999

    def test_name_is_noop(self):
        assert NoOpDiscoveryProvider.name == "noop"


# ---------------------------------------------------------------------------
# DiscoveryProviderRegistry
# ---------------------------------------------------------------------------

class TestDiscoveryProviderRegistry:
    """Registry tests use a fresh local instance, not the singleton."""

    def setup_method(self):
        self.registry = DiscoveryProviderRegistry()

    def _make_provider(self, name: str, priority: int = 100):
        """Create a minimal concrete provider class for testing."""

        class _Provider(BaseDiscoveryProvider):
            def initialize(self): return
            def health_check(self): return DiscoveryHealthStatus(healthy=True, message="ok")
            def capabilities(self): return []
            def supports(self, cap): return False
            def validate_target(self, d): return
            def discover(self, d): return []
            def normalize(self, r): return {}

        _Provider.name = name
        _Provider.priority = priority

        return _Provider

    def test_register_and_get(self):
        cls = self._make_provider("alpha")
        self.registry.register(cls)
        assert self.registry.get("alpha") is cls

    def test_duplicate_registration_raises(self):
        cls = self._make_provider("beta")
        self.registry.register(cls)
        with pytest.raises(ValueError, match="already registered"):
            self.registry.register(cls)

    def test_unregister_removes_provider(self):
        cls = self._make_provider("gamma")
        self.registry.register(cls)
        self.registry.unregister("gamma")
        assert self.registry.get("gamma") is None

    def test_list_returns_providers_in_priority_order(self):
        low = self._make_provider("low", priority=200)
        high = self._make_provider("high", priority=10)
        self.registry.register(low)
        self.registry.register(high)
        ordered = self.registry.list()
        assert ordered[0].name == "high"
        assert ordered[1].name == "low"

    def test_default_returns_highest_priority(self):
        a = self._make_provider("a_prio50", priority=50)
        b = self._make_provider("b_prio10", priority=10)
        self.registry.register(a)
        self.registry.register(b)
        assert self.registry.default().name == "b_prio10"

    def test_default_returns_none_when_empty(self):
        assert self.registry.default() is None

    def test_len_tracks_registrations(self):
        assert len(self.registry) == 0
        self.registry.register(self._make_provider("p1"))
        assert len(self.registry) == 1

    def test_empty_name_raises(self):
        cls = self._make_provider("")
        with pytest.raises(ValueError, match="non-empty"):
            self.registry.register(cls)


# ---------------------------------------------------------------------------
# EvidenceUploadRequest DTO — anti-corruption layer check
# ---------------------------------------------------------------------------

class TestEvidenceUploadRequestDTO:
    def test_is_frozen_dataclass(self):
        dto = EvidenceUploadRequest(
            storage_key="evidence/tenantid/file.pdf",
            original_filename="file.pdf",
            mime_type="application/pdf",
            size_bytes=1024,
            checksum_sha256="abc123",
        )
        with pytest.raises((AttributeError, TypeError)):
            dto.storage_key = "mutated"  # type: ignore[misc]

    def test_no_django_file_primitives_in_module(self):
        """Assert the dto module does not IMPORT any Django file upload types."""
        import backend.apps.osint.dto as dto_module
        import ast

        source = inspect.getsource(dto_module)
        tree = ast.parse(source)
        forbidden = {
            "SimpleUploadedFile",
            "InMemoryUploadedFile",
            "TemporaryUploadedFile",
            "UploadedFile",
        }
        # Collect all names that appear in import statements
        imported_names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom | ast.Import):
                for alias in node.names:
                    imported_names.add(alias.asname or alias.name)
        actual_imports = imported_names & forbidden
        assert not actual_imports, (
            f"Forbidden Django file primitive(s) {actual_imports} imported in dto.py"
        )

    def test_fields_are_all_plain_python_types(self):
        dto = EvidenceUploadRequest(
            storage_key="k",
            original_filename="fn.txt",
            mime_type="text/plain",
            size_bytes=10,
            checksum_sha256="deadbeef",
            discovery_result_id=str(uuid.uuid4()),
            metadata={"source": "noop"},
        )
        assert isinstance(dto.storage_key, str)
        assert isinstance(dto.size_bytes, int)
        assert isinstance(dto.metadata, dict)
