"""Base exception for service layer errors.

All services raise ``ServiceError`` which can be caught by API views to
translate into appropriate HTTP responses (e.g., 400 Bad Request, 403
Forbidden)."""

class ServiceError(Exception):
    """Exception representing a business‑logic error in a service.

    Attributes
    ----------
    message: str
        Human‑readable error description.
    status_code: int
        HTTP status code that should be used when this error is surfaced via
        the API. Defaults to 400.
    """

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
