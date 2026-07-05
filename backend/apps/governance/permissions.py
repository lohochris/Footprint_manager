# Governance app permissions

class GovernancePermissions:
    MANAGE_GOVERNANCE = "governance.manage"
    REVIEW_APPROVAL = "approval.review"
    VIEW_COMPLIANCE = "compliance.view"
    MANAGE_COMPLIANCE = "compliance.manage"
    MANAGE_RETENTION = "retention.manage"
    VIEW_TRUST = "trust.view"
    AUDIT_GOVERNANCE = "governance.audit"

    @classmethod
    def get_all(cls):
        return [
            cls.MANAGE_GOVERNANCE,
            cls.REVIEW_APPROVAL,
            cls.VIEW_COMPLIANCE,
            cls.MANAGE_COMPLIANCE,
            cls.MANAGE_RETENTION,
            cls.VIEW_TRUST,
            cls.AUDIT_GOVERNANCE,
        ]
