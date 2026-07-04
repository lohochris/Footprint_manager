from django.db import models


class IdentityType(models.TextChoices):
    PERSON = "person", "Person"
    ORGANIZATION = "organization", "Organization"
    DOMAIN = "domain", "Domain"
    EMAIL = "email", "Email Address"
    PHONE = "phone", "Phone Number"
    USERNAME = "username", "Username"
    IP_ADDRESS = "ip_address", "IP Address"
    CRYPTO_WALLET = "crypto_wallet", "Cryptocurrency Wallet"
    DEVICE = "device", "Device"
    VEHICLE = "vehicle", "Vehicle"
    CUSTOM = "custom", "Custom Entity"


class RelationshipType(models.TextChoices):
    OWNS = "owns", "Owns"
    MANAGES = "manages", "Manages"
    EMPLOYED_BY = "employed_by", "Employed By"
    REGISTERED_TO = "registered_to", "Registered To"
    COMMUNICATES_WITH = "communicates_with", "Communicates With"
    ASSOCIATED_WITH = "associated_with", "Associated With"
    CONTROLS = "controls", "Controls"
    USES = "uses", "Uses"
    MEMBER_OF = "member_of", "Member Of"


class MatchingStrategy(models.TextChoices):
    EXACT = "exact", "Exact Match"
    NORMALIZED = "normalized", "Normalized String Match"
    FUZZY = "fuzzy", "Fuzzy String Similarity"
    EMAIL_NORM = "email_normalization", "Email Normalization"
    PHONE_NORM = "phone_normalization", "Phone Normalization"
    USERNAME_NORM = "username_normalization", "Username Normalization"
    DOMAIN_NORM = "domain_normalization", "Domain Normalization"
    COMPOSITE = "composite", "Composite Attribute Matching"


class ReviewStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    REQUIRES_REVIEW = "requires_review", "Requires Review"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class MergeAction(models.TextChoices):
    MERGE = "merge", "Merge"
    SPLIT = "split", "Split"
    ROLLBACK = "rollback", "Rollback"


class IdentitySource(models.TextChoices):
    OSINT = "osint", "OSINT Discovery"
    MANUAL = "manual", "Manual Entry"
    IMPORT = "import", "Data Import"
    API = "api", "API Integration"
    MERGE = "merge", "Merged Provenance"
    AI = "ai", "AI-assisted Extraction"
