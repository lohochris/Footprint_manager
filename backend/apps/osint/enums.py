# backend/apps/osint/enums.py
"""Enumeration types for the OSINT Discovery bounded context.

All enumerations use ``django.db.models.TextChoices`` so they are
directly usable in ``CharField(choices=...)`` declarations and carry
human-readable labels.
"""

from django.db import models


class DiscoveryJobStatus(models.TextChoices):
    """Lifecycle state of a DiscoveryJob execution."""

    PENDING = "pending", "Pending"
    QUEUED = "queued", "Queued"
    RUNNING = "running", "Running"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"

    @classmethod
    def terminal_states(cls) -> frozenset[str]:
        """Return the set of states from which no further transition is valid."""
        return frozenset({cls.COMPLETED, cls.FAILED, cls.CANCELLED})


class DiscoveryJobTrigger(models.TextChoices):
    """What initiated a DiscoveryJob."""

    MANUAL = "manual", "Manual"
    SCHEDULED = "scheduled", "Scheduled"
    WEBHOOK = "webhook", "Webhook"
    API = "api", "API"


class DiscoveryResultType(models.TextChoices):
    """Semantic category of a DiscoveryResult finding."""

    PROFILE = "profile", "Profile"
    RELATIONSHIP = "relationship", "Relationship"
    ASSET = "asset", "Asset"
    INDICATOR = "indicator", "Indicator"
    DOCUMENT = "document", "Document"
    RAW = "raw", "Raw"


class DiscoveryProviderStatus(models.TextChoices):
    """Operational readiness state of a DiscoveryProvider."""

    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    DEGRADED = "degraded", "Degraded"
    DEPRECATED = "deprecated", "Deprecated"


class DiscoveryCapability(models.TextChoices):
    """Named capability that a DiscoveryProvider may declare.

    These values are stored in ``DiscoveryProvider.capabilities`` (a
    JSONField list) and in ``DiscoveryJob.capabilities_requested``.
    """

    PERSON_LOOKUP = "person_lookup", "Person Lookup"
    DOMAIN_LOOKUP = "domain_lookup", "Domain Lookup"
    EMAIL_LOOKUP = "email_lookup", "Email Lookup"
    PHONE_LOOKUP = "phone_lookup", "Phone Lookup"
    USERNAME_LOOKUP = "username_lookup", "Username Lookup"
    CRYPTO_LOOKUP = "crypto_lookup", "Crypto Wallet Lookup"
    IP_LOOKUP = "ip_lookup", "IP Address Lookup"
    SOCIAL_MEDIA = "social_media", "Social Media"
    CORPORATE_REGISTRY = "corporate_registry", "Corporate Registry"
    COURT_RECORDS = "court_records", "Court Records"
    CUSTOM = "custom", "Custom"
