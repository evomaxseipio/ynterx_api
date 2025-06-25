import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .config import settings

log = logging.getLogger(__name__)


async def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Send an email using SMTP configuration from settings.

    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body content (plain text)

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Create message container
        msg = MIMEMultipart()
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject

        # Add body to email
        msg.attach(MIMEText(body, "plain"))

        # Create SMTP session
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)

        if settings.SMTP_TLS:
            server.starttls()

        # Login if credentials are provided
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)

        # Send email
        server.send_message(msg)
        server.quit()

        log.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        log.error(f"Failed to send email to {to_email}: {e!s}")
        return False
