from rest_framework.throttling import UserRateThrottle


class SensitiveActionThrottle(UserRateThrottle):
    """Throttle for sensitive actions such as invitation resend or ownership transfer.

    Rate: 5 requests per minute per user.
    """

    rate = "5/min"
