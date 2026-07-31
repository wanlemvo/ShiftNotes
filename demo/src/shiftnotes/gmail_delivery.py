from __future__ import annotations

import base64
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


GMAIL_SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"


def authorize_gmail(
    client_secret_path: Path,
    token_path: Path,
) -> Credentials:
    if not client_secret_path.exists():
        raise RuntimeError(
            f"Gmail OAuth credentials were not found at {client_secret_path}. "
            "Download a Desktop app OAuth client from Google Cloud and save it there."
        )

    credentials: Credentials | None = None
    if token_path.exists():
        credentials = Credentials.from_authorized_user_file(
            str(token_path),
            [GMAIL_SEND_SCOPE],
        )

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    elif not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(client_secret_path),
            [GMAIL_SEND_SCOPE],
        )
        credentials = flow.run_local_server(port=0)

    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(credentials.to_json(), encoding="utf-8")
    return credentials


def build_multipart_message(
    *,
    recipient: str,
    subject: str,
    text_body: str,
    html_body: str,
) -> EmailMessage:
    if "@" not in recipient:
        raise ValueError("A valid recipient email address is required.")
    message = EmailMessage()
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")
    return message


def send_briefing(
    *,
    recipient: str,
    subject: str,
    text_body: str,
    html_body: str,
    credentials: Credentials,
    service: Any | None = None,
) -> dict[str, Any]:
    gmail = service or build("gmail", "v1", credentials=credentials)
    message = build_multipart_message(
        recipient=recipient,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")
    return (
        gmail.users()
        .messages()
        .send(userId="me", body={"raw": raw})
        .execute()
    )


def load_email_preview(
    dataset_dir: Path,
    period_type: str,
    period: str,
) -> dict[str, str]:
    normalized_type = period_type.lower()
    if normalized_type not in {"weekly", "monthly"}:
        raise ValueError("Email type must be weekly or monthly.")

    filename = period.replace("-", "_") if normalized_type == "weekly" else period
    preview_dir = dataset_dir / "email_previews" / normalized_type
    html_path = preview_dir / f"{filename}.html"
    text_path = preview_dir / f"{filename}.txt"
    if not html_path.exists() or not text_path.exists():
        raise RuntimeError(
            f"Email preview files were not found for {normalized_type} {period}. "
            "Run the product-assets command first."
        )

    text_content = text_path.read_text(encoding="utf-8")
    first_line, separator, text_body = text_content.partition("\n\n")
    if not first_line.startswith("Subject: ") or not separator:
        raise RuntimeError(f"Email preview has an invalid text format: {text_path}")
    return {
        "subject": first_line.removeprefix("Subject: ").strip(),
        "text": text_body,
        "html": html_path.read_text(encoding="utf-8"),
    }
