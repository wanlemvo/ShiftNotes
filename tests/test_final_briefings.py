from scripts.generate_final_mock_dataset import build_dataset
from shiftnotes.briefings import (
    generate_final_briefings,
    render_monthly_briefing,
    render_weekly_briefing,
)
from shiftnotes.baseline import (
    build_baseline_analysis,
    deduplicate_reports,
    detect_baseline_events,
)


def briefing_inputs():
    dataset = build_dataset()
    baseline = build_baseline_analysis(
        dataset["normalized"],
        dataset["schedule"],
        dataset["ground_truth"],
    )
    unique, _ = deduplicate_reports(dataset["normalized"])
    reports = [
        report for report in unique
        if report["parse_status"] == "valid"
    ]
    events = detect_baseline_events(reports)
    return dataset, baseline, reports, events


def test_generates_twelve_weekly_and_three_monthly_briefings(tmp_path):
    dataset, _, _, _ = briefing_inputs()

    generated = generate_final_briefings(
        dataset["normalized"],
        dataset["schedule"],
        dataset["ground_truth"],
        tmp_path,
    )

    assert len(generated["weekly"]) == 12
    assert len(generated["monthly"]) == 3
    assert all(path.exists() for path in generated["weekly"])
    assert all(path.exists() for path in generated["monthly"])


def test_weekly_briefing_is_kiosk_centered_and_source_backed():
    dataset, baseline, reports, events = briefing_inputs()
    content = render_weekly_briefing(
        baseline["weekly_summaries"][0],
        None,
        reports,
        dataset["schedule"],
        events,
    )

    assert "## Kiosk-by-Kiosk Review" in content
    for kiosk in (
        "Bowls & Buns",
        "Market Grill",
        "Verde Kitchen",
        "Coastal Cafe",
        "Hearth & Grain",
        "Street Eats",
    ):
        assert f"### {kiosk}" in content
    assert "Sources: FM-" in content
    assert "Challenge this summary" in content
    assert "rotating weekly menu schedule" in content
    assert "per valid report" in content
    assert "1 expected report was missing or invalid" in content


def test_weekly_briefing_can_render_ai_semantic_events():
    dataset, baseline, reports, _ = briefing_inputs()
    events = {
        "semantic:portion_complaint:portion-looked-smaller": [
            {
                "source_submission_id": "FM-0001",
                "date": "2026-03-02",
                "kiosk": "Bowls & Buns",
                "excerpt": "portion looked smaller",
                "label": "portion-size concerns",
                "follow_up": "Compare portion guidance across kiosks.",
                "sensitive": False,
            }
        ]
    }

    content = render_weekly_briefing(
        baseline["weekly_summaries"][0],
        None,
        reports,
        dataset["schedule"],
        events,
    )

    assert "portion-size concerns" in content
    assert "Compare portion guidance across kiosks." in content


def test_weekly_briefing_includes_previous_week_changes():
    dataset, baseline, reports, events = briefing_inputs()
    content = render_weekly_briefing(
        baseline["weekly_summaries"][1],
        baseline["weekly_summaries"][0],
        reports,
        dataset["schedule"],
        events,
    )

    assert "vs prior week" in content
    assert "from the previous week" in content


def test_monthly_briefing_uses_cost_guardrails_and_efficiency_language():
    dataset, baseline, reports, events = briefing_inputs()
    content = render_monthly_briefing(
        baseline["monthly_summaries"][1],
        baseline["monthly_summaries"][0],
        reports,
        dataset["schedule"],
        events,
    )

    assert "## Cost and Waste Signals" in content
    assert "Actual dollar savings cannot be calculated" in content
    assert "operational-efficiency indicators" in content
    assert "not confirmed productivity measurements" in content
    assert "Sources: FM-" in content


def test_partial_month_is_labeled_and_uses_rate_comparisons():
    dataset, baseline, reports, events = briefing_inputs()
    content = render_monthly_briefing(
        baseline["monthly_summaries"][2],
        baseline["monthly_summaries"][1],
        reports,
        dataset["schedule"],
        events,
    )

    assert "partial month through May 21, 2026" in content
    assert "per-report rates rather than raw totals" in content


def test_sensitive_personnel_note_requires_inspection_not_action():
    dataset, baseline, reports, events = briefing_inputs()
    content = render_monthly_briefing(
        baseline["monthly_summaries"][1],
        baseline["monthly_summaries"][0],
        reports,
        dataset["schedule"],
        events,
    )

    assert "## Sensitive Note Requiring Inspection" in content
    assert "must not be treated as evidence of misconduct" in content
    assert "autonomous personnel action" in content
