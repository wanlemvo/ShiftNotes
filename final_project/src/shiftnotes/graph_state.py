from __future__ import annotations

from typing import Any, Literal, TypedDict


RunMode = Literal["demo", "live"]
RunStatus = Literal[
    "planning",
    "ingesting",
    "retrying",
    "processing",
    "awaiting_review",
    "approved",
    "rejected",
    "failed",
]


class ShiftNotesGraphState(TypedDict, total=False):
    thread_id: str
    mode: RunMode
    reporting_period: str
    expected_kiosks: list[str]
    limit: int
    max_retries: int
    retry_count: int
    simulate_failures: int
    status: RunStatus
    route: str
    tool_result: dict[str, Any]
    raw_submissions: dict[str, Any]
    reports: list[dict[str, Any]]
    analysis: dict[str, Any]
    draft_briefing: str
    final_briefing: str
    review_decision: str
    correction_note: str
    error: str
    fallback_reason: str
    execution_log: list[str]
