from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from statistics import mean
from typing import Any


TEXT_FIELDS = (
    "food_concerns_or_outages",
    "team_members_who_did_well",
    "guest_issues_for_the_day",
    "operational_notes",
)

SIGNAL_KEYWORDS = {
    "food_shortage": ("ran out", "shortage", "short", "ran low", "low", "unavailable"),
    "guest_request": ("asked", "requested", "request", "bring back", "could be offered"),
    "food_quality_issue": ("dry", "overcooked", "cold", "undercooked", "bad", "complaint"),
    "staff_recognition": ("helped", "worked well", "kept", "communicated", "explain"),
    "process_improvement": ("recommend", "review", "consider", "need to", "tracking"),
}

MENU_TERMS = (
    "kung pao chicken",
    "tofu stir-fry",
    "veggie stir-fry",
    "rice",
    "mac salad",
    "green onions",
    "poke",
    "chicken",
    "tofu",
)

OVERLAPPING_TERMS = {
    "chicken": ("kung pao chicken",),
    "tofu": ("tofu stir-fry", "veggie stir-fry"),
}


def analyze_reports(
    reports: list[dict[str, Any]],
    expected_kiosks: list[str] | None = None,
) -> dict[str, Any]:
    valid_reports = [report for report in reports if report.get("parse_status") == "valid"]
    report_dates = [parse_iso_date(report.get("date", "")) for report in valid_reports]
    report_dates = [report_date for report_date in report_dates if report_date]

    start_date = min(report_dates).isoformat() if report_dates else ""
    end_date = max(report_dates).isoformat() if report_dates else ""
    kiosks = expected_kiosks or sorted({str(report.get("kiosk", "")) for report in valid_reports if report.get("kiosk")})

    signals = extract_semantic_signals(valid_reports)
    return {
        "period": {"start_date": start_date, "end_date": end_date},
        "summary": summarize_reports(valid_reports),
        "kiosks": summarize_by_kiosk(valid_reports, kiosks),
        "signals": signals,
        "claims": build_claims(valid_reports, signals),
        "missing_reports": detect_missing_reports(valid_reports, kiosks),
    }


def summarize_reports(reports: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "total_reports": len(reports),
        "average_food_quality_rating": average_rating(reports, "food_quality_rating"),
        "average_food_quantity_rating": average_rating(reports, "food_quantity_rating"),
        "total_unclaimed_lunches": sum_ints(reports, "number_of_unclaimed_lunches"),
    }


def summarize_by_kiosk(reports: list[dict[str, Any]], kiosks: list[str]) -> dict[str, dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = {}
    for kiosk in kiosks:
        kiosk_reports = [report for report in reports if report.get("kiosk") == kiosk]
        summaries[kiosk] = summarize_reports(kiosk_reports)
    return summaries


def extract_semantic_signals(reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    for report in reports:
        for field in TEXT_FIELDS:
            text = str(report.get(field, "") or "")
            lowered = text.lower()
            if not lowered or lowered in {"n/a", "na", "none", "no issues."}:
                continue

            matched_terms = matched_menu_terms(lowered)
            for signal_type, keywords in SIGNAL_KEYWORDS.items():
                if any(keyword in lowered for keyword in keywords):
                    signals.append(
                        {
                            "type": signal_type,
                            "field": field,
                            "kiosk": report.get("kiosk", ""),
                            "date": report.get("date", ""),
                            "source_submission_id": report.get("source_submission_id", ""),
                            "matched_terms": matched_terms,
                            "excerpt": excerpt(text),
                        }
                    )
    return signals


def build_claims(
    reports: list[dict[str, Any]],
    signals: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []

    menu_sources = count_menu_sources(reports)
    for term, source_ids in sorted(menu_sources.items(), key=lambda item: len(item[1]), reverse=True):
        if len(source_ids) >= 2:
            claims.append(
                {
                    "claim": f"{term.title()} was mentioned in {len(source_ids)} reports.",
                    "metric": len(source_ids),
                    "source_submission_ids": sorted(source_ids),
                }
            )

    by_type: dict[str, set[str]] = defaultdict(set)
    for signal in signals:
        by_type[signal["type"]].add(str(signal["source_submission_id"]))

    for signal_type, source_ids in sorted(by_type.items()):
        if len(source_ids) >= 2:
            label = signal_type.replace("_", " ")
            claims.append(
                {
                    "claim": f"{label.title()} appeared in {len(source_ids)} reports.",
                    "metric": len(source_ids),
                    "source_submission_ids": sorted(source_ids),
                }
            )

    return claims


def detect_missing_reports(reports: list[dict[str, Any]], kiosks: list[str]) -> list[dict[str, str]]:
    by_kiosk_date = {(report.get("kiosk"), report.get("date")) for report in reports}
    dates = [parse_iso_date(report.get("date", "")) for report in reports]
    dates = [report_date for report_date in dates if report_date]
    if not dates:
        return []

    missing: list[dict[str, str]] = []
    current = min(dates)
    end = max(dates)
    while current <= end:
        current_text = current.isoformat()
        for kiosk in kiosks:
            if (kiosk, current_text) not in by_kiosk_date:
                missing.append({"kiosk": kiosk, "date": current_text})
        current += timedelta(days=1)
    return missing


def render_weekly_briefing(analysis: dict[str, Any]) -> str:
    period = analysis["period"]
    summary = analysis["summary"]
    lines = [
        "# ShiftNotes Weekly Operations Briefing",
        "",
        f"Period: {period['start_date']} to {period['end_date']}",
        "",
        "## Operational Snapshot",
        f"- Reports analyzed: {summary['total_reports']}",
        f"- Average food quality rating: {summary['average_food_quality_rating']}",
        f"- Average food quantity rating: {summary['average_food_quantity_rating']}",
        f"- Total unclaimed lunches: {summary['total_unclaimed_lunches']}",
        "",
        "## Kiosk Breakdown",
    ]

    for kiosk, kiosk_summary in analysis["kiosks"].items():
        lines.extend(
            [
                f"- {kiosk}: {kiosk_summary['total_reports']} reports, "
                f"quality {kiosk_summary['average_food_quality_rating']}, "
                f"quantity {kiosk_summary['average_food_quantity_rating']}, "
                f"{kiosk_summary['total_unclaimed_lunches']} unclaimed lunches",
            ]
        )

    lines.extend(["", "## Source-Backed Trends"])
    if analysis["claims"]:
        for claim in analysis["claims"]:
            sources = ", ".join(claim["source_submission_ids"])
            lines.append(f"- {claim['claim']} Sources: {sources}")
    else:
        lines.append("- No repeated source-backed trends met the current threshold.")

    lines.extend(["", "## Missing Report Flags"])
    if analysis["missing_reports"]:
        for missing in analysis["missing_reports"]:
            lines.append(f"- {missing['kiosk']} has no report for {missing['date']}.")
    else:
        lines.append("- No missing reports detected for the observed period and kiosk list.")

    lines.extend(["", "## HITL Review Note"])
    lines.append("Every claim above includes source submission IDs so a manager can inspect and correct it.")
    return "\n".join(lines) + "\n"


def count_menu_sources(reports: list[dict[str, Any]]) -> dict[str, set[str]]:
    mentions: dict[str, set[str]] = defaultdict(set)
    for report in reports:
        text = " ".join(str(report.get(field, "") or "") for field in TEXT_FIELDS).lower()
        for term in matched_menu_terms(text):
            mentions[term].add(str(report.get("source_submission_id", "")))
    return mentions


def matched_menu_terms(text: str) -> list[str]:
    terms = [term for term in MENU_TERMS if term in text]
    return [
        term
        for term in terms
        if not any(specific in terms for specific in OVERLAPPING_TERMS.get(term, ()))
    ]


def average_rating(reports: list[dict[str, Any]], field: str) -> float | None:
    values = [report.get(field) for report in reports if isinstance(report.get(field), int)]
    if not values:
        return None
    return round(mean(values), 2)


def sum_ints(reports: list[dict[str, Any]], field: str) -> int:
    return sum(int(report.get(field) or 0) for report in reports)


def parse_iso_date(value: Any) -> date | None:
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        return None


def excerpt(text: str, limit: int = 180) -> str:
    clean = " ".join(text.split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3].rstrip() + "..."
