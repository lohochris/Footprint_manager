from django.db import models


class GraphNodeType(models.TextChoices):
    IDENTITY = "identity", "Identity"
    INVESTIGATION = "investigation", "Investigation"
    EVIDENCE = "evidence", "Evidence"
    OSINT = "osint", "OSINT Discovery"
    ORGANIZATION = "organization", "Organization"
    WORKSPACE = "workspace", "Workspace"
    CUSTOM = "custom", "Custom Node"


class GraphRelationshipType(models.TextChoices):
    MEMBER_OF = "member_of", "Member Of"
    RESOLVES_TO = "resolves_to", "Resolves To"
    CORRELATES_WITH = "correlates_with", "Correlates With"
    DISCOVERED_BY = "discovered_by", "Discovered By"
    REFERENCES = "references", "References"
    CONTAINS = "contains", "Contains"
    CUSTOM = "custom", "Custom Relationship"
