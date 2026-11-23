import logging

from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class LogAndDropBackend(BaseEmailBackend):
    """Used in production when no mail server is configured.

    Email here is only workflow notices, so a missing mail server must not
    stop anyone publishing. Each message is noted in the logs and dropped.
    """

    def send_messages(self, email_messages):
        for message in email_messages:
            logger.warning(
                "Email not sent, no mail server configured: %r to %d "
                "recipient(s)",
                message.subject,
                len(message.recipients()),
            )
        return len(email_messages)
