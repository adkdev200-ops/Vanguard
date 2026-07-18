import os
import smtplib
from email.mime.text import MIMEText
from typing import Union

from dotenv import load_dotenv

load_dotenv()

EMAIL = os.environ.get("SMTP_EMAIL", "")
APP_PASSWORD = os.environ.get("SMTP_APP_PASSWORD", "")


def send_html_email(
    to: Union[str, list[str]],
    subject: str,
    html: str,
) -> None:
    """
    Send an HTML email to one or more recipients.

    Args:
        to: Recipient email or list of recipient emails.
        subject: Email subject.
        html: HTML content.
    """
    if not EMAIL or not APP_PASSWORD:
        raise RuntimeError(
            "SMTP_EMAIL and SMTP_APP_PASSWORD environment variables must be set. "
            "Add them to a .env file in the project root."
        )

    recipients = [to] if isinstance(to, str) else to

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL, APP_PASSWORD)
        
        for recipient in recipients:
            msg = MIMEText(html, "html")
            msg["Subject"] = subject
            msg["From"] = EMAIL
            msg["To"] = recipient
            try:
                server.send_message(msg)
                print(f"Email sent successfully to {recipient}")
            except Exception as e:
                print(f"Failed to send email to {recipient}: {e}")