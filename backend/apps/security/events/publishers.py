from backend.shared.event_bus import event_bus


class SecurityEventPublisher:
    @staticmethod
    def publish_mfa_enabled(payload: dict) -> None:
        event_bus.publish("MFAEnabled", payload)

    @staticmethod
    def publish_mfa_challenge_completed(payload: dict) -> None:
        event_bus.publish("MFAChallengeCompleted", payload)

    @staticmethod
    def publish_api_key_created(payload: dict) -> None:
        event_bus.publish("APIKeyCreated", payload)

    @staticmethod
    def publish_api_key_revoked(payload: dict) -> None:
        event_bus.publish("APIKeyRevoked", payload)

    @staticmethod
    def publish_session_created(payload: dict) -> None:
        event_bus.publish("SessionCreated", payload)

    @staticmethod
    def publish_session_revoked(payload: dict) -> None:
        event_bus.publish("SessionRevoked", payload)

    @staticmethod
    def publish_security_policy_changed(payload: dict) -> None:
        event_bus.publish("SecurityPolicyChanged", payload)

    @staticmethod
    def publish_security_alert_generated(payload: dict) -> None:
        event_bus.publish("SecurityAlertGenerated", payload)

__all__ = ["SecurityEventPublisher"]
