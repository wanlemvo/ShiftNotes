from __future__ import annotations

import base64
from email import message_from_bytes
from pathlib import Path

import pytest

from shiftnotes.gmail_delivery import (
    build_multipart_message,
    load_email_preview,
    send_briefing,
)


class FakeSendRequest:
    def __init__(self, result):
        self.result = result

    def execute(self):
        return self.result


class FakeMessages:
    def __init__(self):
        self.call = None

    def send(self, *, userId, body):
        self.call = {"userId": userId, "body": body}
        return FakeSendRequest({"id": "gmail-message-123", "threadId": "thread-1"})


class FakeUsers:
    def __init__(self, messages):
        self._messages = messages

    def messages(self):
        return self._messages


class FakeGmailService:
    def __init__(self):
        self.messages_api = FakeMessages()

    def users(self):
        return FakeUsers(self.messages_api)


def test_builds_html_and_plain_text_multipart_message():
    message = build_multipart_message(
        recipient="manager@example.com",
        subject="Weekly briefing",
        text_body="Plain briefing",
        html_body="<strong>HTML briefing</strong>",
    )

    assert message["To"] == "manager@example.com"
    assert message["Subject"] == "Weekly briefing"
    assert message.is_multipart()
    assert message.get_body(preferencelist=("plain",)).get_content().strip() == "Plain briefing"
    assert "HTML briefing" in message.get_body(preferencelist=("html",)).get_content()


def test_send_uses_gmail_messages_send_with_encoded_mime():
    service = FakeGmailService()

    result = send_briefing(
        recipient="manager@example.com",
        subject="Monthly briefing",
        text_body="Plain",
        html_body="<p>HTML</p>",
        credentials=None,
        service=service,
    )

    assert result["id"] == "gmail-message-123"
    assert service.messages_api.call["userId"] == "me"
    raw = service.messages_api.call["body"]["raw"]
    decoded = base64.urlsafe_b64decode(raw.encode("ascii"))
    message = message_from_bytes(decoded)
    assert message["To"] == "manager@example.com"
    assert message["Subject"] == "Monthly briefing"


def test_loads_generated_preview_pair(tmp_path: Path):
    preview_dir = tmp_path / "email_previews" / "weekly"
    preview_dir.mkdir(parents=True)
    (preview_dir / "week_01.html").write_text("<p>Briefing</p>", encoding="utf-8")
    (preview_dir / "week_01.txt").write_text(
        "Subject: Weekly briefing\n\nPlain briefing",
        encoding="utf-8",
    )

    preview = load_email_preview(tmp_path, "weekly", "week-01")

    assert preview == {
        "subject": "Weekly briefing",
        "text": "Plain briefing",
        "html": "<p>Briefing</p>",
    }


def test_rejects_invalid_recipient():
    with pytest.raises(ValueError, match="valid recipient"):
        build_multipart_message(
            recipient="not-an-email",
            subject="Briefing",
            text_body="Plain",
            html_body="<p>HTML</p>",
        )
