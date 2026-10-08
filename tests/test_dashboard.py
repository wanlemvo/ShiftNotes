from datetime import date

from scripts.generate_final_mock_dataset import build_dataset
from shiftnotes.dashboard import dashboard_snapshot
from shiftnotes.product import build_claim_catalog


def snapshot_data():
    dataset = build_dataset()
    claims = build_claim_catalog(dataset["normalized"], dataset["schedule"])
    return dataset, claims


def test_full_range_excludes_duplicates_and_separates_missing_from_invalid():
    data, claims = snapshot_data()
    result = dashboard_snapshot(data["normalized"], data["schedule"], claims, date(2026, 3, 1), date(2026, 5, 31))
    summary = result["summary"]
    assert summary["received"] == 270
    assert summary["valid_reports"] == 267
    assert summary["duplicates"] == 3
    assert summary["invalid"] == 3
    assert summary["missing"] == 18
    assert summary["expected"] == 288
    assert sum(r["unclaimed"] for r in result["trends"]) == summary["unclaimed"]


def test_filters_apply_to_sources_metrics_missing_and_comparison():
    data, claims = snapshot_data()
    start, end = date(2026, 3, 2), date(2026, 3, 5)
    result = dashboard_snapshot(data["normalized"], data["schedule"], claims, start, end, "Bowls & Buns")
    for report in result["valid_reports"] + result["missing"]:
        assert report["kiosk"] == "Bowls & Buns"
        assert start.isoformat() <= report["date"] <= end.isoformat()
    ids = {r["source_submission_id"] for r in result["valid_reports"]}
    assert all(set(f["source_ids"]) <= ids for f in result["findings"])
    assert len(result["comparison"]) == 1
    assert result["summary"]["expected"] == 4


def test_weekly_and_monthly_claims_do_not_double_count_and_corrections_apply():
    data, claims = snapshot_data()
    start, end = date(2026, 3, 1), date(2026, 5, 31)
    weekly = [c for c in claims if c["period_type"] == "weekly"]
    full = dashboard_snapshot(data["normalized"], data["schedule"], claims, start, end)
    assert full == dashboard_snapshot(data["normalized"], data["schedule"], weekly, start, end)
    claim = next(c for c in weekly if c["source_count"] > 1)
    removed = claim["source_submission_ids"].pop()
    claim["source_count"] -= 1
    revised = dashboard_snapshot(data["normalized"], data["schedule"], weekly, start, end)
    finding = next(f for f in revised["findings"] if f["category"] == claim["category"] and f["kiosk"] == claim["kiosk"])
    assert removed not in finding["source_ids"]


def test_empty_range_has_no_invented_averages():
    data, claims = snapshot_data()
    result = dashboard_snapshot(data["normalized"], data["schedule"], claims, date(2027, 1, 1), date(2027, 1, 7))
    assert result["summary"]["quality"] is None
    assert result["summary"]["quantity"] is None
    assert result["summary"]["received"] == 0
    assert result["findings"] == []
