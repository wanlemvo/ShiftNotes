from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from statistics import mean
from typing import Any, Callable

from shiftnotes.analysis import TEXT_FIELDS, excerpt


REPORT_FINGERPRINT_FIELDS = (
    "date",
    "kiosk",
    "lead_name",
    "food_quality_rating",
    "food_quantity_rating",
    "food_concerns_or_outages",
    "team_members_who_did_well",
    "guest_issues_for_the_day",
    "operational_notes",
    "number_of_unclaimed_lunches",
)


def load_schedule(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def report_fingerprint(report: dict[str, Any]) -> str:
    canonical = {
        field: report.get(field)
        for field in REPORT_FINGERPRINT_FIELDS
    }
    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def deduplicate_reports(
    reports: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    unique: list[dict[str, Any]] = []
    first_by_fingerprint: dict[str, str] = {}
    duplicates: list[dict[str, str]] = []

    for report in reports:
        fingerprint = report_fingerprint(report)
        source_id = str(report.get("source_submission_id", ""))
        original_id = first_by_fingerprint.get(fingerprint)
        if original_id:
            duplicates.append(
                {
                    "duplicate_submission_id": source_id,
                    "original_submission_id": original_id,
                    "fingerprint": fingerprint,
                }
            )
            continue

        first_by_fingerprint[fingerprint] = source_id
        unique.append(report)

    return unique, duplicates


def build_reporting_completeness(
    reports: list[dict[str, Any]],
    schedule: list[dict[str, str]],
    duplicates: list[dict[str, str]],
) -> dict[str, Any]:
    received_slots = {
        (str(report.get("kiosk", "")), str(report.get("date", "")))
        for report in reports
        if report.get("kiosk") and report.get("date")
    }
    expected_slots = {
        (row["kiosk"], row["date"])
        for row in schedule
    }
    missing = [
        {
            "expected_report_id": row["expected_report_id"],
            "kiosk": row["kiosk"],
            "date": row["date"],
            "week": int(row["week"]),
        }
        for row in schedule
        if (row["kiosk"], row["date"]) not in received_slots
    ]
    malformed = [
        {
            "source_submission_id": str(report.get("source_submission_id", "")),
            "kiosk": str(report.get("kiosk", "")),
            "date": str(report.get("date", "")),
            "validation_errors": report.get("validation_errors", []),
        }
        for report in reports
        if report.get("parse_status") != "valid"
    ]
    unexpected_slots = sorted(received_slots - expected_slots)

    expected_count = len(schedule)
    received_count = expected_count - len(missing)
    valid_unique_count = sum(report.get("parse_status") == "valid" for report in reports)
    return {
        "expected_report_count": expected_count,
        "received_expected_slot_count": received_count,
        "valid_unique_report_count": valid_unique_count,
        "missing_report_count": len(missing),
        "malformed_report_count": len(malformed),
        "duplicate_submission_count": len(duplicates),
        "submission_completeness_percent": percentage(received_count, expected_count),
        "valid_report_percent": percentage(valid_unique_count, expected_count),
        "missing_reports": missing,
        "malformed_reports": malformed,
        "duplicates": duplicates,
        "unexpected_received_slots": [
            {"kiosk": kiosk, "date": report_date}
            for kiosk, report_date in unexpected_slots
        ],
    }


def build_period_summaries(
    reports: list[dict[str, Any]],
    schedule: list[dict[str, str]],
    period: str,
) -> list[dict[str, Any]]:
    if period not in {"week", "month"}:
        raise ValueError("period must be 'week' or 'month'")

    valid_reports = [
        report for report in reports
        if report.get("parse_status") == "valid"
    ]
    schedule_by_slot = {
        (row["kiosk"], row["date"]): row
        for row in schedule
    }
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for report in valid_reports:
        report_date = str(report.get("date", ""))
        if period == "week":
            row = schedule_by_slot.get((str(report.get("kiosk", "")), report_date))
            key = f"week-{int(row['week']):02d}" if row else "week-unknown"
        else:
            key = report_date[:7]
        grouped[key].append(report)

    expected_by_period: Counter[str] = Counter()
    for row in schedule:
        key = (
            f"week-{int(row['week']):02d}"
            if period == "week"
            else row["date"][:7]
        )
        expected_by_period[key] += 1

    summaries: list[dict[str, Any]] = []
    for key in sorted(expected_by_period):
        period_reports = grouped.get(key, [])
        summaries.append(
            {
                "period": key,
                "expected_reports": expected_by_period[key],
                "valid_reports": len(period_reports),
                "missing_or_invalid_reports": expected_by_period[key] - len(period_reports),
                "overall": summarize(period_reports),
                "kiosks": summarize_by_kiosk(period_reports),
            }
        )
    return summaries


def summarize(reports: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "report_count": len(reports),
        "average_food_quality_rating": average(reports, "food_quality_rating"),
        "average_food_quantity_rating": average(reports, "food_quantity_rating"),
        "total_unclaimed_lunches": sum(
            int(report.get("number_of_unclaimed_lunches") or 0)
            for report in reports
        ),
    }


def summarize_by_kiosk(
    reports: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    kiosks = sorted(
        {
            str(report.get("kiosk", ""))
            for report in reports
            if report.get("kiosk")
        }
    )
    return {
        kiosk: summarize(
            [report for report in reports if report.get("kiosk") == kiosk]
        )
        for kiosk in kiosks
    }


def detect_baseline_events(
    reports: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    detectors: dict[str, Callable[[dict[str, Any]], bool]] = {
        "food_shortage:kung_pao_chicken": lambda report: contains_any(
            report,
            (
                "kung pao chicken ran low",
                "kung pao chicken sold out",
                "chicken prep was below demand",
            ),
        ),
        "waste:high_unclaimed_lunches": lambda report: contains_any(
            report,
            (
                "unclaimed lunches were above target",
                "production exceeded afternoon demand",
                "prepared meals remained after service",
            ),
        ),
        "guest_theme:dietary_or_allergy_question": lambda report: contains_any(
            report,
            (
                "was vegan",
                "gluten-free",
                "allergy information",
                "contained dairy",
                "allergen labels",
            ),
        ),
        "operational_issue:equipment_failure": lambda report: contains_any(
            report,
            (
                "register froze during lunch",
                "receipt printer failed",
                "warming unit required a reset",
            ),
        ),
        "recognition:maya_chen": lambda report: (
            "maya chen" in str(report.get("team_members_who_did_well", "")).lower()
        ),
        "inventory:inconsistent_prep": lambda report: contains_any(
            report,
            (
                "cilantro rice ran low",
                "tofu taco prep did not match demand",
                "inventory counts did not match",
            ),
        ),
        "cross_kiosk:register_disruption_week_7": lambda report: contains_any(
            report,
            ("shared register connection dropped",),
        ),
        "cross_kiosk:portion_complaints_weeks_9_10": lambda report: contains_any(
            report,
            (
                "portions looked smaller",
                "serving size had changed",
                "portion did not match",
            ),
        ),
        "guest_request:beverage_variety": lambda report: contains_any(
            report,
            ("more beverage variety",),
        ),
        "sensitive_personnel:ambiguous_comment": lambda report: contains_any(
            report,
            ("does not establish misconduct",),
        ),
        "safety:immediate_review": lambda report: contains_any(
            report,
            (
                "safety concern",
                "unsafe condition",
                "slip hazard",
                "burn injury",
                "smoke from",
                "exposed wire",
                "gas smell",
            ),
        ),
        "personnel:coaching_review": lambda report: contains_any(
            report,
            (
                "needs additional training",
                "needed a process reminder",
                "requested more training",
                "needs clarification on",
            ),
        ),
    }

    events: dict[str, list[dict[str, Any]]] = {}
    for category, detector in detectors.items():
        matches = []
        for report in reports:
            if report.get("parse_status") != "valid" or not detector(report):
                continue
            matches.append(
                {
                    "source_submission_id": report.get("source_submission_id", ""),
                    "date": report.get("date", ""),
                    "kiosk": report.get("kiosk", ""),
                    "excerpt": matching_excerpt(report),
                }
            )
        events[category] = matches
    return events


def build_baseline_benchmark(
    reports: list[dict[str, Any]],
    completeness: dict[str, Any],
    schedule: list[dict[str, str]],
    ground_truth: dict[str, Any],
) -> dict[str, Any]:
    detected_events = detect_baseline_events(reports)
    event_results: dict[str, dict[str, Any]] = {}
    analyzable_source_ids = {
        str(report.get("source_submission_id", ""))
        for report in reports
    }

    for category, truth in ground_truth.get("events", {}).items():
        if category == "cross_kiosk:waste_spike_weeks_7_8":
            continue
        total_expected_ids = {
            record["source_submission_id"]
            for record in truth["source_records"]
        }
        expected_ids = total_expected_ids & analyzable_source_ids
        unavailable_ids = total_expected_ids - analyzable_source_ids
        detected_ids = {
            record["source_submission_id"]
            for record in detected_events.get(category, [])
        }
        true_positive_ids = expected_ids & detected_ids
        false_positive_ids = detected_ids - expected_ids
        missed_ids = expected_ids - detected_ids
        event_results[category] = {
            "total_ground_truth_count": len(total_expected_ids),
            "analyzable_expected_count": len(expected_ids),
            "unavailable_due_data_quality_count": len(unavailable_ids),
            "detected_count": len(detected_ids),
            "true_positive_count": len(true_positive_ids),
            "false_positive_count": len(false_positive_ids),
            "missed_count": len(missed_ids),
            "precision": percentage(len(true_positive_ids), len(detected_ids)),
            "recall": percentage(len(true_positive_ids), len(expected_ids)),
            "overall_recall_including_unavailable": percentage(
                len(true_positive_ids),
                len(total_expected_ids),
            ),
            "detected_source_ids": sorted(detected_ids),
            "missed_source_ids": sorted(missed_ids),
            "unavailable_source_ids": sorted(unavailable_ids),
            "false_positive_source_ids": sorted(false_positive_ids),
        }

    expected_missing = {
        (record["kiosk"], record["date"])
        for record in completeness["missing_reports"]
    }
    truth_missing = {
        (row["kiosk"], row["date"])
        for row in schedule
        if row.get("status") == "missing"
    }
    waste_totals = kiosk_waste_totals(reports)
    detected_highest_waste = max(waste_totals, key=waste_totals.get)
    expected_highest_waste = dominant_event_kiosk(
        ground_truth["events"]["waste:high_unclaimed_lunches"]["source_records"]
    )
    waste_spike = detect_waste_spike(reports)

    exact_event_matches = sum(
        result["precision"] == 100.0 and result["recall"] == 100.0
        for result in event_results.values()
    )
    return {
        "missing_report_detection": {
            "expected_count": len(truth_missing),
            "detected_count": len(expected_missing),
            "exact_match": expected_missing == truth_missing,
            "detected_kiosk_dates": [
                {"kiosk": kiosk, "date": report_date}
                for kiosk, report_date in sorted(expected_missing)
            ],
        },
        "highest_waste_kiosk": {
            "expected": expected_highest_waste,
            "detected": detected_highest_waste,
            "correct": detected_highest_waste == expected_highest_waste,
            "totals": waste_totals,
        },
        "waste_spike_weeks_7_8": waste_spike,
        "event_detection": event_results,
        "summary": {
            "event_categories_scored": len(event_results),
            "exact_event_category_matches": exact_event_matches,
            "missing_reports_exact_match": expected_missing == truth_missing,
            "highest_waste_kiosk_correct": detected_highest_waste == expected_highest_waste,
        },
        "detected_events": detected_events,
    }


def build_baseline_analysis(
    reports: list[dict[str, Any]],
    schedule: list[dict[str, str]],
    ground_truth: dict[str, Any],
) -> dict[str, Any]:
    unique_reports, duplicates = deduplicate_reports(reports)
    completeness = build_reporting_completeness(
        unique_reports,
        schedule,
        duplicates,
    )
    valid_reports = [
        report for report in unique_reports
        if report.get("parse_status") == "valid"
    ]
    weekly = build_period_summaries(unique_reports, schedule, "week")
    monthly = build_period_summaries(unique_reports, schedule, "month")
    benchmark = build_baseline_benchmark(
        valid_reports,
        completeness,
        schedule,
        ground_truth,
    )
    waste_totals = kiosk_waste_totals(valid_reports)
    kiosk_summaries = summarize_by_kiosk(valid_reports)

    return {
        "dataset": {
            "start_date": min(row["date"] for row in schedule),
            "end_date": max(row["date"] for row in schedule),
            "expected_reports": len(schedule),
            "input_submissions": len(reports),
            "unique_submissions": len(unique_reports),
            "valid_unique_reports": len(valid_reports),
        },
        "cleaning": {
            "duplicates_removed": len(duplicates),
            "malformed_reports_excluded_from_metrics": completeness[
                "malformed_report_count"
            ],
        },
        "reporting_completeness": completeness,
        "overall": summarize(valid_reports),
        "kiosks": kiosk_summaries,
        "weekly_summaries": weekly,
        "monthly_summaries": monthly,
        "operational_findings": {
            "highest_waste_kiosk": max(waste_totals, key=waste_totals.get),
            "waste_totals_by_kiosk": waste_totals,
            "lowest_quantity_kiosk": min(
                kiosk_summaries,
                key=lambda kiosk: kiosk_summaries[kiosk][
                    "average_food_quantity_rating"
                ],
            ),
        },
        "benchmark": benchmark,
    }


def render_baseline_briefing(analysis: dict[str, Any]) -> str:
    dataset = analysis["dataset"]
    completeness = analysis["reporting_completeness"]
    findings = analysis["operational_findings"]
    benchmark = analysis["benchmark"]
    event_results = benchmark["event_detection"]

    lines = [
        "# ShiftNotes Baseline Operations Briefing",
        "",
        f"Period: {dataset['start_date']} to {dataset['end_date']}",
        "",
        "## Reporting Health",
        f"- Expected reports: {completeness['expected_report_count']}",
        f"- Received expected kiosk/date reports: {completeness['received_expected_slot_count']}",
        f"- Valid unique reports analyzed: {completeness['valid_unique_report_count']}",
        f"- Missing reports: {completeness['missing_report_count']}",
        f"- Malformed reports requiring review: {completeness['malformed_report_count']}",
        f"- Duplicate submissions excluded: {completeness['duplicate_submission_count']}",
        f"- Submission completeness: {completeness['submission_completeness_percent']}%",
        "",
        "## Operational Snapshot",
        f"- Highest unclaimed-lunch total: {findings['highest_waste_kiosk']} "
        f"({findings['waste_totals_by_kiosk'][findings['highest_waste_kiosk']]})",
        f"- Lowest average food-quantity rating: {findings['lowest_quantity_kiosk']}",
        "",
        "## Source-Backed Baseline Findings",
    ]

    for category, result in event_results.items():
        if result["detected_count"] == 0:
            continue
        label = category.replace(":", " - ").replace("_", " ").title()
        sources = ", ".join(result["detected_source_ids"])
        report_word = "report" if result["detected_count"] == 1 else "reports"
        lines.append(
            f"- {label}: {result['detected_count']} {report_word}. Sources: {sources}"
        )

    lines.extend(["", "## Missing Kiosk/Date Reports"])
    for missing in completeness["missing_reports"]:
        lines.append(f"- {missing['kiosk']}: {missing['date']}")

    lines.extend(
        [
            "",
            "## Data Quality Review",
            f"- Malformed source IDs: {', '.join(item['source_submission_id'] for item in completeness['malformed_reports'])}",
            f"- Duplicate source IDs: {', '.join(item['duplicate_submission_id'] for item in completeness['duplicates'])}",
            "",
            "## Baseline Benchmark",
            f"- Missing-report detection exact match: {benchmark['missing_report_detection']['exact_match']}",
            f"- Highest-waste kiosk correct: {benchmark['highest_waste_kiosk']['correct']}",
            f"- Event categories matched exactly: "
            f"{benchmark['summary']['exact_event_category_matches']}/"
            f"{benchmark['summary']['event_categories_scored']}",
            "",
            "This is a controlled deterministic baseline over planted synthetic language. "
            "AI-assisted semantic extraction will be measured against it for broader wording and ambiguity.",
            "",
        ]
    )
    return "\n".join(lines)


def contains_any(report: dict[str, Any], phrases: tuple[str, ...]) -> bool:
    text = " ".join(
        str(report.get(field, "") or "")
        for field in TEXT_FIELDS
    ).lower()
    return any(phrase in text for phrase in phrases)


def matching_excerpt(report: dict[str, Any]) -> str:
    text = " ".join(
        str(report.get(field, "") or "")
        for field in TEXT_FIELDS
        if report.get(field)
    )
    return excerpt(text, limit=240)


def average(reports: list[dict[str, Any]], field: str) -> float | None:
    values = [
        int(report[field])
        for report in reports
        if isinstance(report.get(field), int)
    ]
    return round(mean(values), 2) if values else None


def percentage(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


def kiosk_waste_totals(reports: list[dict[str, Any]]) -> dict[str, int]:
    totals: dict[str, int] = defaultdict(int)
    for report in reports:
        totals[str(report.get("kiosk", ""))] += int(
            report.get("number_of_unclaimed_lunches") or 0
        )
    return dict(sorted(totals.items()))


def dominant_event_kiosk(records: list[dict[str, Any]]) -> str:
    counts = Counter(record["kiosk"] for record in records)
    return counts.most_common(1)[0][0]


def detect_waste_spike(reports: list[dict[str, Any]]) -> dict[str, Any]:
    market_reports = [
        report for report in reports
        if report.get("kiosk") == "Market Grill"
    ]
    weekly: dict[int, list[int]] = defaultdict(list)
    start = date(2026, 3, 2)
    for report in market_reports:
        report_date = datetime.strptime(report["date"], "%Y-%m-%d").date()
        week = ((report_date - start).days // 7) + 1
        weekly[week].append(int(report["number_of_unclaimed_lunches"]))
    averages = {
        f"week-{week:02d}": round(mean(values), 2)
        for week, values in sorted(weekly.items())
    }
    baseline_values = [
        value
        for week, values in weekly.items()
        if week not in {7, 8}
        for value in values
    ]
    spike_values = [
        value
        for week, values in weekly.items()
        if week in {7, 8}
        for value in values
    ]
    baseline_average = round(mean(baseline_values), 2)
    spike_average = round(mean(spike_values), 2)
    return {
        "baseline_average_excluding_weeks_7_8": baseline_average,
        "weeks_7_8_average": spike_average,
        "increase": round(spike_average - baseline_average, 2),
        "detected": spike_average > baseline_average,
        "weekly_averages": averages,
    }
