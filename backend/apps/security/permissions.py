class SecurityPermissions:
    SECURITY_MANAGE = "security.manage"
    SECURITY_AUDIT = "security.audit"
    API_KEYS_MANAGE = "api_keys.manage"
    MFA_MANAGE = "mfa.manage"
    SESSIONS_MANAGE = "sessions.manage"

    @classmethod
    def get_all(cls):
        return [
            cls.SECURITY_MANAGE,
            cls.SECURITY_AUDIT,
            cls.API_KEYS_MANAGE,
            cls.MFA_MANAGE,
            cls.SESSIONS_MANAGE,
        ]
