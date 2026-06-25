from pathlib import Path

from langgraph.types import Command

from scripts.generate_final_mock_dataset import build_dataset
from shiftnotes.correction_graph import build_test_correction_graph
from shiftnotes.email_preview import render_monthly_email, render_weekly_email
from shiftnotes.product import (
    apply_correction_history,
    build_claim_catalog,
    build_source_bundle,
    load_correction_history,
    propose_correction,
)
from shiftnotes.scheduling import (
    PACIFIC,
    monthly_inventory_briefing_date,
    next_weekly_run,
)


def product_data():
    dataset = build_dataset()
    claims = build_claim_catalog(dataset["normalized"], dataset["schedule"])
    return dataset, claims


def pick_claim(claims, category, period_type="weekly"):
    return next(
        claim
        for claim in claims
        if claim["category"] == category
        and claim["period_type"] == period_type
    )


def config(thread_id):
    return {"configurable": {"thread_id": thread_id}}


def test_claim_catalog_and_source_bundle_are_traceable():
    dataset, claims = product_data()
    claim = pick_claim(claims, "food_shortage:kung_pao_chicken")
    sources = build_source_bundle(claim, dataset["normalized"])

    assert claim["source_count"] == len(claim["source_submission_ids"])
    assert len(sources) == claim["source_count"]
    assert {
        source["source_submission_id"] for source in sources
    } == set(claim["source_submission_ids"])


def test_claim_catalog_can_use_ai_semantic_extractions():
    dataset, _ = product_data()
    extraction = [
        {
            "source_submission_id": "FM-0001",
            "semantic_provider": "openai/gpt-oss-20b",
            "signals": [
                {
                    "category": "portion_complaint",
                    "subject": "portion looked smaller",
                    "severity": "medium",
                    "confidence": 0.86,
                    "evidence_field": "guest_issues_for_the_day",
                    "evidence_excerpt": "portion looked smaller",
                    "sensitive": False,
                    "rationale": "Guest mentioned portion size.",
                }
            ],
        }
    ]

    claims = build_claim_catalog(
        dataset["normalized"],
        dataset["schedule"],
        semantic_extractions=extraction,
    )
    claim = next(
        item
        for item in claims
        if item["category"] == "semantic:portion_complaint:portion-complaint"
    )

    assert claim["label"] == "portion-size concerns"
    assert claim["source_submission_ids"] == ["FM-0001"]


def test_plain_english_challenge_creates_confirmation_proposal():
    dataset, claims = product_data()
    claim = pick_claim(claims, "cross_kiosk:register_disruption_week_7")
    source_id = claim["source_submission_ids"][0]

    proposal = propose_correction(
        claim,
        f"This is wrong. Remove {source_id}; it should not support this claim.",
        dataset["normalized"],
    )

    assert proposal["status"] == "pending_confirmation"
    assert proposal["requires_confirmation"] is True
    assert source_id in proposal["removed_source_ids"]
    assert source_id not in proposal["proposed_source_ids"]


def test_unsafe_personnel_action_is_refused():
    dataset, claims = product_data()
    claim = pick_claim(
        claims,
        "sensitive_personnel:ambiguous_comment",
        period_type="monthly",
    )

    proposal = propose_correction(
        claim,
        "Email everyone that Tony is stealing and should be fired.",
        dataset["normalized"],
    )

    assert proposal["status"] == "refused"
    assert proposal["safety_refusal"] is True
    assert proposal["requires_confirmation"] is False


def test_correction_graph_waits_for_confirmation_then_saves(tmp_path: Path):
    dataset, claims = product_data()
    claim = pick_claim(claims, "food_shortage:kung_pao_chicken")
    source_id = claim["source_submission_ids"][0]
    history_path = tmp_path / "history.json"
    graph = build_test_correction_graph()
    thread_id = "confirm-correction"

    paused = graph.invoke(
        {
            "thread_id": thread_id,
            "claim": claim,
            "challenge_text": f"Remove {source_id}. This is wrong.",
            "reports": dataset["normalized"],
            "history_path": str(history_path),
            "execution_log": [],
        },
        config(thread_id),
    )

    assert paused["status"] == "pending_confirmation"
    assert paused["__interrupt__"]
    assert not history_path.exists()

    completed = graph.invoke(
        Command(resume={"decision": "confirm"}),
        config(thread_id),
    )
    history = load_correction_history(history_path)

    assert completed["status"] == "confirmed"
    assert len(history) == 1
    assert history[0]["decision"] == "confirm"
    resolved = apply_correction_history([claim], history)
    assert resolved[0]["status"] == "corrected"
    assert source_id not in resolved[0]["source_submission_ids"]


def test_email_previews_are_polished_and_source_linked():
    dataset, claims = product_data()
    weekly_claims = [
        claim for claim in claims
        if claim["period_type"] == "weekly" and claim["period"] == "week-01"
    ]
    monthly_claims = [
        claim for claim in claims
        if claim["period_type"] == "monthly" and claim["period"] == "2026-05"
    ]
    weekly_markdown = (
        "# ShiftNotes Weekly Operations Briefing\n\n"
        "Week 1: March 2 - March 5, 2026\n\n"
        "- Reporting: 23/24 valid reports\n"
        "- Average food quality: 4.43/5\n"
        "- Average food quantity: 3.43/5\n"
        "- Unclaimed lunches: 122\n"
    )
    monthly_markdown = (
        "# ShiftNotes Monthly Operations Briefing\n\nMay 2026\n\n"
        "- Reporting: 65/72 valid reports\n"
        "- Average food quality: 4.23/5\n"
        "- Average food quantity: 3.75/5\n"
        "- Unclaimed lunches per valid report: 4.42\n"
        "- Possible impact: validate production before changing inventory.\n"
        "- Food quality decreased by 0.13.\n"
        "- Unclaimed lunches per valid report decreased by 0.69.\n"
    )

    weekly = render_weekly_email(weekly_markdown, weekly_claims)
    monthly = render_monthly_email(monthly_markdown, monthly_claims)

    assert "View sources" in weekly["html"]
    assert "Challenge this claim" in weekly["html"]
    assert "Open full briefing" in monthly["html"]
    assert "Actual dollar" not in monthly["html"]
    assert "possible opportunity" in monthly["html"].lower()


def test_schedule_uses_pacific_thursday_and_inventory_timing():
    after = next_weekly_run(
        # Monday, June 22, 2026 at noon Pacific.
        __import__("datetime").datetime(2026, 6, 22, 12, tzinfo=PACIFIC)
    )

    assert after.weekday() == 3
    assert (after.hour, after.minute) == (15, 30)
    assert monthly_inventory_briefing_date(2026, 6).isoformat() == "2026-06-29"
