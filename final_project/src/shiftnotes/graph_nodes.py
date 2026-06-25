from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from langgraph.types import Command, interrupt

from shiftnotes.analysis import analyze_reports, render_weekly_briefing
from shiftnotes.config import load_settings
from shiftnotes.graph_state import ShiftNotesGraphState
from shiftnotes.jotform_client import fetch_form_submissions
from shiftnotes.normalize import normalize_submissions


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DEMO_FIXTURE = ROOT / "final_project" / "data" / "demo" / "jotform_submissions.json"


def append_log(state: ShiftNotesGraphState, message: str) -> list[str]:
    return [*state.get("execution_log", []), message]


def planner_node(state: ShiftNotesGraphState) -> dict[str, Any]:
    mode = state.get("mode", "demo")
    expected_kiosks = state.get("expected_kiosks") or ["Bowls & Buns"]
    max_retries = max(0, int(state.get("max_retries", 2)))
    return {
        "mode": mode,
        "expected_kiosks": expected_kiosks,
        "limit": int(state.get("limit", 100)),
        "max_retries": max_retries,
        "retry_count": int(state.get("retry_count", 0)),
        "status": "planning",
        "route": "ingest",
        "error": "",
        "fallback_reason": "",
        "execution_log": append_log(
            state,
            f"planner: mode={mode}; expected_kiosks={expected_kiosks}; max_retries={max_retries}",
        ),
    }


def ingest_tool_node(state: ShiftNotesGraphState) -> dict[str, Any]:
    attempt = int(state.get("retry_count", 0)) + 1
    simulated_failures = int(state.get("simulate_failures", 0))

    if attempt <= simulated_failures:
        error = f"simulated ingestion failure on attempt {attempt}"
        return {
            "status": "ingesting",
            "route": "evaluate",
            "error": error,
            "tool_result": {
                "success": False,
                "source": "simulated",
                "submission_count": 0,
                "error": error,
            },
            "raw_submissions": {},
            "execution_log": append_log(state, f"ingest_tool: failed; {error}"),
        }

    try:
        if state.get("mode") == "live":
            settings = load_settings()
            raw = fetch_form_submissions(
                settings.jotform_api_key,
                settings.jotform_form_id,
                limit=int(state.get("limit", 100)),
            )
            source = "JotForm API"
        else:
            raw = json.loads(DEFAULT_DEMO_FIXTURE.read_text(encoding="utf-8"))
            source = str(DEFAULT_DEMO_FIXTURE)

        content = raw.get("content", [])
        if not isinstance(content, list):
            raise ValueError("ingestion output content must be a list")

        return {
            "status": "ingesting",
            "route": "evaluate",
            "error": "",
            "tool_result": {
                "success": True,
                "source": source,
                "submission_count": len(content),
                "error": "",
            },
            "raw_submissions": raw,
            "execution_log": append_log(
                state,
                f"ingest_tool: success; source={source}; submissions={len(content)}; attempt={attempt}",
            ),
        }
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        return {
            "status": "ingesting",
            "route": "evaluate",
            "error": error,
            "tool_result": {
                "success": False,
                "source": "JotForm API" if state.get("mode") == "live" else str(DEFAULT_DEMO_FIXTURE),
                "submission_count": 0,
                "error": error,
            },
            "raw_submissions": {},
            "execution_log": append_log(state, f"ingest_tool: failed; {error}"),
        }


def evaluator_node(state: ShiftNotesGraphState) -> dict[str, Any]:
    tool_result = state.get("tool_result", {})
    success = bool(tool_result.get("success"))
    submission_count = int(tool_result.get("submission_count", 0))
    error = str(tool_result.get("error") or state.get("error", ""))
    retry_count = int(state.get("retry_count", 0))
    max_retries = int(state.get("max_retries", 2))

    if success and submission_count > 0:
        return {
            "route": "normalize",
            "status": "processing",
            "execution_log": append_log(state, "evaluator: ingestion output accepted"),
        }

    if retry_count < max_retries:
        next_retry = retry_count + 1
        return {
            "route": "retry",
            "status": "retrying",
            "retry_count": next_retry,
            "execution_log": append_log(
                state,
                f"evaluator: retrying ingestion; retry={next_retry}/{max_retries}; reason={error or 'empty content'}",
            ),
        }

    reason = error or "ingestion returned no submissions"
    return {
        "route": "fallback",
        "status": "failed",
        "fallback_reason": reason,
        "execution_log": append_log(
            state,
            f"evaluator: retry limit reached; routing to fallback; reason={reason}",
        ),
    }


def route_after_evaluation(state: ShiftNotesGraphState) -> str:
    return state.get("route", "fallback")


def normalize_node(state: ShiftNotesGraphState) -> dict[str, Any]:
    reports = normalize_submissions(state.get("raw_submissions", {}))
    valid_count = sum(report.get("parse_status") == "valid" for report in reports)
    review_count = len(reports) - valid_count
    return {
        "reports": reports,
        "execution_log": append_log(
            state,
            f"normalize: reports={len(reports)}; valid={valid_count}; needs_review={review_count}",
        ),
    }


def analysis_node(state: ShiftNotesGraphState) -> dict[str, Any]:
    analysis = analyze_reports(
        state.get("reports", []),
        expected_kiosks=state.get("expected_kiosks"),
    )
    return {
        "analysis": analysis,
        "execution_log": append_log(
            state,
            f"analyze: claims={len(analysis['claims'])}; missing_reports={len(analysis['missing_reports'])}",
        ),
    }


def draft_briefing_node(state: ShiftNotesGraphState) -> dict[str, Any]:
    briefing = render_weekly_briefing(state.get("analysis", {}))
    correction_note = state.get("correction_note", "").strip()
    if correction_note:
        briefing += f"\n## Human Correction\n{correction_note}\n"
    return {
        "draft_briefing": briefing,
        "status": "awaiting_review",
        "execution_log": append_log(
            state,
            "draft_briefing: created source-backed briefing"
            + (" with reviewer correction" if correction_note else ""),
        ),
    }


def human_review_node(
    state: ShiftNotesGraphState,
) -> Command[Literal["draft_briefing", "finalize", "reject"]]:
    response = interrupt(
        {
            "action": "review_weekly_briefing",
            "message": "Approve, correct, or reject the ShiftNotes briefing before finalization.",
            "options": ["approve", "correct", "reject"],
            "briefing": state.get("draft_briefing", ""),
            "thread_id": state.get("thread_id", ""),
        }
    )

    if not isinstance(response, dict):
        response = {"decision": str(response)}

    decision = str(response.get("decision", "")).strip().lower()
    note = str(response.get("note", "")).strip()

    if decision == "approve":
        return Command(
            update={
                "review_decision": "approve",
                "status": "approved",
                "execution_log": append_log(state, "human_review: approved"),
            },
            goto="finalize",
        )
    if decision == "correct" and note:
        return Command(
            update={
                "review_decision": "correct",
                "correction_note": note,
                "execution_log": append_log(state, f"human_review: correction requested; note={note}"),
            },
            goto="draft_briefing",
        )

    return Command(
        update={
            "review_decision": "reject",
            "status": "rejected",
            "execution_log": append_log(
                state,
                "human_review: rejected" + (f"; note={note}" if note else ""),
            ),
        },
        goto="reject",
    )


def finalize_node(state: ShiftNotesGraphState) -> dict[str, Any]:
    return {
        "final_briefing": state.get("draft_briefing", ""),
        "status": "approved",
        "execution_log": append_log(
            state,
            "finalize: briefing approved and finalized; email delivery intentionally disabled",
        ),
    }


def reject_node(state: ShiftNotesGraphState) -> dict[str, Any]:
    return {
        "final_briefing": "",
        "status": "rejected",
        "execution_log": append_log(state, "reject: workflow ended without finalizing briefing"),
    }


def fallback_node(state: ShiftNotesGraphState) -> dict[str, Any]:
    return {
        "status": "failed",
        "final_briefing": "",
        "execution_log": append_log(
            state,
            f"fallback: manual review required; reason={state.get('fallback_reason', 'unknown')}",
        ),
    }
