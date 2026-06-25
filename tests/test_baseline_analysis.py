from scripts.generate_final_mock_dataset import build_dataset
from shiftnotes.baseline import (
    build_baseline_analysis,
    deduplicate_reports,
    render_baseline_briefing,
)


def build_analysis():
    dataset = build_dataset()
    return build_baseline_analysis(
        dataset["normalized"],
        dataset["schedule"],
        dataset["ground_truth"],
    )


def test_duplicate_detection_removes_three_extra_submissions():
    dataset = build_dataset()
    unique, duplicates = deduplicate_reports(dataset["normalized"])

    assert len(dataset["normalized"]) == 273
    assert len(unique) == 270
    assert len(duplicates) == 3
    assert {
        item["duplicate_submission_id"]
        for item in duplicates
    } == {"DUP-001", "DUP-002", "DUP-003"}


def test_completeness_uses_expected_schedule_not_calendar_days():
    analysis = build_analysis()
    completeness = analysis["reporting_completeness"]

    assert completeness["expected_report_count"] == 288
    assert completeness["received_expected_slot_count"] == 270
    assert completeness["missing_report_count"] == 18
    assert completeness["malformed_report_count"] == 3
    assert completeness["duplicate_submission_count"] == 3
    assert completeness["submission_completeness_percent"] == 93.75
    assert completeness["valid_report_percent"] == 92.71
    assert completeness["unexpected_received_slots"] == []


def test_weekly_and_monthly_summaries_cover_full_dataset():
    analysis = build_analysis()

    assert len(analysis["weekly_summaries"]) == 12
    assert len(analysis["monthly_summaries"]) == 3
    assert sum(
        period["expected_reports"]
        for period in analysis["weekly_summaries"]
    ) == 288
    assert sum(
        period["valid_reports"]
        for period in analysis["weekly_summaries"]
    ) == 267


def test_baseline_finds_expected_operational_winners():
    analysis = build_analysis()
    findings = analysis["operational_findings"]

    assert findings["highest_waste_kiosk"] == "Market Grill"
    assert findings["lowest_quantity_kiosk"] == "Bowls & Buns"
    assert analysis["benchmark"]["highest_waste_kiosk"]["correct"] is True
    assert analysis["benchmark"]["missing_report_detection"]["exact_match"] is True
    assert analysis["benchmark"]["waste_spike_weeks_7_8"]["detected"] is True


def test_deterministic_event_detectors_match_ground_truth():
    analysis = build_analysis()
    benchmark = analysis["benchmark"]

    assert benchmark["summary"]["event_categories_scored"] == 10
    assert benchmark["summary"]["exact_event_category_matches"] == 10
    for result in benchmark["event_detection"].values():
        assert result["precision"] == 100.0
        assert result["recall"] == 100.0
    unavailable = {
        source_id
        for result in benchmark["event_detection"].values()
        for source_id in result["unavailable_source_ids"]
    }
    assert unavailable == {"FM-0154", "FM-0240"}


def test_baseline_briefing_contains_required_sections_and_sources():
    analysis = build_analysis()
    briefing = render_baseline_briefing(analysis)

    assert "## Reporting Health" in briefing
    assert "## Operational Snapshot" in briefing
    assert "## Source-Backed Baseline Findings" in briefing
    assert "## Missing Kiosk/Date Reports" in briefing
    assert "## Data Quality Review" in briefing
    assert "Sources: FM-" in briefing
