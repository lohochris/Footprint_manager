"""
Email integration interface for Footprint Manager.

Defines the ``EmailBackend`` abstract interface for transactional email
delivery.  Concrete implementations (SMTP, SendGrid, AWS SES, Mailgun)
are registered via Django settings and selected at runtime.

Usage::

    from backend.apps.integrations.email import EmailBackend, EmailMessage

    class MyView:
        def __init__(self, email: EmailBackend) -> None:
            self.email = email

        def notify(self, to: str, subject: str, body: str) -> None:
            msg = EmailMessage(to=[to], subject=subject, html_body=body)
            self.email.send(msg)
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field


@dataclass
class EmailMessage:
    """
    Represents a transactional email to be sent.

    Attributes:
        to: List of recipient email addresses.
        subject: Email subject line.
        html_body: HTML version of the email body.
        text_body: Plain-text fallback version (auto-stripped from html_body if omitted).
        from_address: Sender address (defaults to ``settings.DEFAULT_FROM_EMAIL``).
        reply_to: Optional reply-to address.
        cc: Carbon-copy recipients.
        bcc: Blind carbon-copy recipients.
        attachments: List of ``(filename, data_bytes, content_type)`` tuples.
        headers: Custom email headers.
        tags: Provider-specific tags for analytics.
        template_id: Provider template identifier (overrides html/text body when set).
        template_data: Variables passed to the provider template.
    """

    to: list[str]
    subject: str
    html_body: str = ""
    text_body: str = ""
    from_address: str | None = None
    reply_to: str | None = None
    cc: list[str] = field(default_factory=list)
    bcc: list[str] = field(default_factory=list)
    attachments: list[tuple[str, bytes, str]] = field(default_factory=list)
    headers: dict[str, str] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    template_id: str | None = None
    template_data: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class EmailDeliveryResult:
    """
    Outcome of an email send operation.

    Attributes:
        success: Whether the provider accepted the message.
        message_id: Provider-assigned message identifier.
        error: Error description if *success* is False.
    """

    success: bool
    message_id: str | None = None
    error: str | None = None


class EmailBackend(abc.ABC):
    """
    Abstract transactional email backend.

    Implementations must be thread-safe and stateless.
    """

    @abc.abstractmethod
    def send(self, message: EmailMessage) -> EmailDeliveryResult:
        """
        Send a single email message.

        Args:
            message: The email to send.

        Returns:
            ``EmailDeliveryResult`` indicating success or failure.
        """

    def send_many(self, messages: list[EmailMessage]) -> list[EmailDeliveryResult]:
        """
        Send multiple email messages.

        The default implementation calls ``send`` in a loop.  Backends with
        bulk-send APIs should override this for efficiency.

        Args:
            messages: List of email messages to send.

        Returns:
            List of results, one per input message, in the same order.
        """
        return [self.send(msg) for msg in messages]

    @abc.abstractmethod
    def health_check(self) -> bool:
        """
        Verify the backend can reach the email provider.

        Returns:
            True if the provider is reachable.
        """


__all__ = [
    "EmailMessage",
    "EmailDeliveryResult",
    "EmailBackend",
]
