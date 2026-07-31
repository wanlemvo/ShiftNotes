from __future__ import annotations

import calendar
from datetime import datetime
from pathlib import Path
from typing import Any

from shiftnotes.baseline import (
    build_baseline_analysis,
    deduplicate_reports,
    detect_baseline_events,
    load_schedule,
)
from shiftnotes.semantic_events import semantic_events_from_extractions
from shiftnotes.storage import read_json


EVENT_LABELS = {
    "safety:immediate_review": "safety concern requiring immediate review",
    "food_shortage:kung_pao_chicken": "Kung Pao chicken shortages",
    "waste:high_unclaimed_lunches": "overproduction or elevated unclaimed lunches",
    "guest_theme:dietary_or_allergy_question": "dietary and allergy questions",
    "operational_issue:equipment_failure": "equipment-related disruptions",
    "recognition:maya_chen": "recognition for Maya Chen",
    "inventory:inconsistent_prep": "inventory and prep inconsistencies",
    "cross_kiosk:register_disruption_week_7": "shared register disruption",
    "cross_kiosk:portion_complaints_weeks_9_10": "portion-size concerns",
    "guest_request:beverage_variety": "requests for beverage variety",
    "sensitive_personnel:ambiguous_comment": "an ambiguous personnel note requiring careful review",
    "personnel:coaching_review": "potential coaching or training opportunity requiring review",
}

EVENT_FOLLOW_UPS = {
    "safety:immediate_review": "Inspect the source immediately and follow the applicable workplace safety process.",
    "food_shortage:kung_pao_chicken": "Compare prep levels with lunch-rush demand.",
    "waste:high_unclaimed_lunches": "Review prep quantities and unclaimed-lunch patterns before adjusting production.",
    "guest_theme:dietary_or_allergy_question": "Confirm that dietary and allergen information is easy for staff and guests to access.",
    "operational_issue:equipment_failure": "Review recurring equipment incidents and document maintenance follow-up.",
    "recognition:maya_chen": "Recognize the repeated positive performance and identify practices worth reinforcing.",
    "inventory:inconsistent_prep": "Review inventory handoffs and end-of-shift counts.",
    "cross_kiosk:register_disruption_week_7": "Confirm whether the shared register interruption requires technical follow-up.",
    "cross_kiosk:portion_complaints_weeks_9_10": "Compare portion guidance across kiosks before changing service standards.",
    "guest_request:beverage_variety": "Track whether beverage requests continue before changing the offering.",
    "sensitive_personnel:ambiguous_comment": "Inspect the original report; do not infer misconduct or take personnel action from this note alone.",
    "personnel:coaching_review": "Review the source privately and confirm whether supportive training or clarification is appropriate.",
}

SENSITIVE_CATEGORY = "sensitive_personnel:ambiguous_comment"


def generate_final_briefings(
    reports: list[dict[str, Any]],
    schedule: list[dict[str, str]],
    ground_truth: dict[str, Any],
    output_dir: Path,
    semantic_extractions: list[dict[str, Any]] | None = None,
) -> dict[str, list[Path]]:
    baseline = build_baseline_analysis(reports, schedule, ground_truth)
    unique_reports, _ = deduplicate_reports(reports)
    valid_reports = [
        report for report in unique_reports
        if report.get("parse_status") == "valid"
    ]
    events = (
        semantic_events_from_extractions(semantic_extractions, valid_reports)
        if semantic_extractions is not None
        else detect_baseline_events(valid_reports)
    )

    weekly_dir = output_dir / "weekly"
    monthly_dir = output_dir / "monthly"
    weekly_dir.mkdir(parents=True, exist_ok=True)
    monthly_dir.mkdir(parents=True, exist_ok=True)

    weekly_paths: list[Path] = []
    for index, summary in enumerate(baseline["weekly_summaries"]):
        previous = baseline["weekly_summaries"][index - 1] if index else None
        content = render_weekly_briefing(
            summary,
            previous,
            valid_reports,
            schedule,
            events,
        )
        path = weekly_dir / f"{summary['period'].replace('-', '_')}.md"
        path.write_text(content, encoding="utf-8")
        weekly_paths.append(path)

    monthly_paths: list[Path] = []
    for index, summary in enumerate(baseline["monthly_summaries"]):
        previous = baseline["monthly_summaries"][index - 1] if index else None
        content = render_monthly_briefing(
            summary,
            previous,
            valid_reports,
            schedule,
            events,
        )
        path = monthly_dir / f"{summary['period']}.md"
        path.write_text(content, encoding="utf-8")
        monthly_paths.append(path)

    return {"weekly": weekly_paths, "monthly": monthly_paths}


def render_weekly_briefing(
    summary: dict[str, Any],
    previous: dict[str, Any] | None,
    reports: list[dict[str, Any]],
    schedule: list[dict[str, str]],
    events: dict[str, list[dict[str, Any]]],
) -> str:
    week = int(summary["period"].split("-")[1])
    period_schedule = [row for row in schedule if int(row["week"]) == week]
    dates = sorted({row["date"] for row in period_schedule})
    period_reports = reports_for_week(reports, schedule, week)
    period_events = events_for_reports(events, period_reports)
    missing_rows = [
        row for row in period_schedule
        if row["status"] == "missing"
    ]
    invalid_rows = [
        row for row in period_schedule
        if row["status"] == "malformed"
    ]
    attention = weekly_attention_items(summary, previous, period_events)

    lines = [
        "# ShiftNotes Weekly Operations Briefing",
        "",
        f"Week {week}: {friendly_date(dates[0])} - {friendly_date(dates[-1], include_year=True)}",
        "",
        "## Week at a Glance",
        f"- Reporting: {summary['valid_reports']}/{summary['expected_reports']} valid reports",
        f"- Average food quality: {rating(summary['overall']['average_food_quality_rating'])}",
        f"- Average food quantity: {rating(summary['overall']['average_food_quantity_rating'])}",
        f"- Unclaimed lunches: {summary['overall']['total_unclaimed_lunches']}",
        f"- Missing reports: {len(missing_rows)}",
        f"- Reports requiring data review: {len(invalid_rows)}",
        "",
        "## Management Summary",
    ]
    lines.extend(f"- {item}" for item in attention)

    lines.extend(["", "## Kiosk-by-Kiosk Review"])
    for kiosk in sorted({row["kiosk"] for row in period_schedule}):
        kiosk_schedule = [row for row in period_schedule if row["kiosk"] == kiosk]
        kiosk_reports = [report for report in period_reports if report["kiosk"] == kiosk]
        kiosk_summary = summary["kiosks"].get(kiosk, empty_summary())
        previous_summary = (
            previous["kiosks"].get(kiosk)
            if previous
            else None
        )
        kiosk_events = filter_events(period_events, kiosk=kiosk)
        lines.extend(
            render_weekly_kiosk(
                kiosk,
                kiosk_summary,
                previous_summary,
                kiosk_schedule,
                kiosk_reports,
                kiosk_events,
            )
        )

    lines.extend(["", "## Reporting Exceptions"])
    if not missing_rows and not invalid_rows:
        lines.append("- No missing or malformed reports this week.")
    for row in missing_rows:
        lines.append(f"- Missing: {row['kiosk']} on {row['date']}")
    for row in invalid_rows:
        lines.append(
            f"- Data review: {row['kiosk']} on {row['date']} ({row['issue']})"
        )

    lines.extend(
        [
            "",
            "## Interpretation Note",
            "Menu-specific findings are based only on dishes explicitly named in shift reports. "
            "ShiftNotes does not currently receive the rotating weekly menu schedule.",
            "",
            "Supporting report IDs are provided for inspection. A future source view will allow Ted "
            "to open the reports and challenge a claim in ordinary language.",
            "",
        ]
    )
    return "\n".join(lines)


def render_weekly_kiosk(
    kiosk: str,
    summary: dict[str, Any],
    previous: dict[str, Any] | None,
    schedule_rows: list[dict[str, str]],
    reports: list[dict[str, Any]],
    events: dict[str, list[dict[str, Any]]],
) -> list[str]:
    valid_count = summary["report_count"]
    expected_count = len(schedule_rows)
    lines = [
        "",
        f"### {kiosk}",
        f"- Reports: {valid_count}/{expected_count}",
        f"- Food quality: {rating(summary['average_food_quality_rating'])}"
        f"{change_text(summary['average_food_quality_rating'], previous, 'average_food_quality_rating')}",
        f"- Food quantity: {rating(summary['average_food_quantity_rating'])}"
        f"{change_text(summary['average_food_quantity_rating'], previous, 'average_food_quantity_rating')}",
        f"- Unclaimed lunches: {summary['total_unclaimed_lunches']} "
        f"({report_rate(summary['total_unclaimed_lunches'], valid_count)} per valid report)"
        f"{rate_change_text(summary, previous)}",
        "",
        "**Weekly summary**",
        kiosk_week_summary(summary, events),
        "",
        "**Trends noticed**",
    ]

    visible_events = [
        (category, records)
        for category, records in events.items()
        if records
    ]
    if not visible_events:
        lines.append("- No repeated source-backed issue met the current weekly threshold.")
    else:
        for category, records in visible_events:
            sources = ", ".join(record["source_submission_id"] for record in records)
            lines.append(
                f"- {event_label(category, records)}: {len(records)} "
                f"{'report' if len(records) == 1 else 'reports'}. Sources: {sources}"
            )

    lines.extend(["", "**Suggested follow-up**"])
    follow_ups = [
        event_follow_up(category, records)
        for category, records in visible_events
        if records
    ]
    if not follow_ups:
        if summary["average_food_quantity_rating"] is not None and summary[
            "average_food_quantity_rating"
        ] < 3:
            follow_ups.append("Review quantity planning and prep handoffs.")
        else:
            follow_ups.append("No immediate follow-up identified from the submitted reports.")
    for follow_up in dict.fromkeys(follow_ups):
        lines.append(f"- {follow_up}")

    source_ids = [report["source_submission_id"] for report in reports]
    lines.extend(
        [
            "",
            f"Supporting reports: {', '.join(source_ids) if source_ids else 'None available'}",
            "Challenge this summary: available through the future source-inspection workflow.",
        ]
    )
    return lines


def render_monthly_briefing(
    summary: dict[str, Any],
    previous: dict[str, Any] | None,
    reports: list[dict[str, Any]],
    schedule: list[dict[str, str]],
    events: dict[str, list[dict[str, Any]]],
) -> str:
    month = summary["period"]
    period_schedule = [row for row in schedule if row["date"].startswith(month)]
    period_reports = [report for report in reports if report["date"].startswith(month)]
    period_events = events_for_reports(events, period_reports)
    missing_rows = [row for row in period_schedule if row["status"] == "missing"]
    invalid_rows = [row for row in period_schedule if row["status"] == "malformed"]
    waste_by_kiosk = {
        kiosk: values["total_unclaimed_lunches"]
        for kiosk, values in summary["kiosks"].items()
    }
    waste_per_report = {
        kiosk: round(
            values["total_unclaimed_lunches"] / values["report_count"],
            2,
        )
        for kiosk, values in summary["kiosks"].items()
        if values["report_count"]
    }
    highest_waste = max(waste_per_report, key=waste_per_report.get)
    month_name = datetime.strptime(month, "%Y-%m").strftime("%B %Y")

    lines = [
        "# ShiftNotes Monthly Operations Briefing",
        "",
        month_name,
        "",
        "## Executive Summary",
        f"- Reporting: {summary['valid_reports']}/{summary['expected_reports']} valid reports",
        f"- Average food quality: {rating(summary['overall']['average_food_quality_rating'])}"
        f"{month_change_text(summary, previous, 'average_food_quality_rating')}",
        f"- Average food quantity: {rating(summary['overall']['average_food_quantity_rating'])}"
        f"{month_change_text(summary, previous, 'average_food_quantity_rating')}",
        f"- Unclaimed lunches per valid report: "
        f"{round(summary['overall']['total_unclaimed_lunches'] / summary['valid_reports'], 2)}"
        f"{month_rate_change(summary, previous)}",
        f"- Highest unclaimed-lunch rate: {highest_waste} "
        f"({waste_per_report[highest_waste]} per valid report)",
        f"- Missing reports: {len(missing_rows)}",
    ]
    if is_partial_month(period_schedule):
        lines.append(
            f"- Coverage note: this is a partial month through {friendly_date(max(row['date'] for row in period_schedule), include_year=True)}. "
            "Month comparisons emphasize per-report rates rather than raw totals."
        )
    lines.extend(
        [
            "",
            "## Cost and Waste Signals",
            f"- {highest_waste} recorded {waste_by_kiosk[highest_waste]} unclaimed lunches "
            f"across {summary['kiosks'][highest_waste]['report_count']} valid reports.",
            "- Possible impact: repeated unclaimed lunches may indicate an overproduction opportunity. "
            "Actual dollar savings cannot be calculated without meal-cost and volume data.",
        ]
    )

    waste_records = period_events.get("waste:high_unclaimed_lunches", [])
    if waste_records:
        lines.append(
            f"- Source-backed overproduction language appeared in {len(waste_records)} reports. "
            f"Sources: {source_list(waste_records)}"
        )

    lines.extend(["", "## Month-over-Month Direction"])
    if previous is None:
        lines.append("- This is the first reporting month, so no previous-month comparison is available.")
    else:
        lines.extend(month_direction_lines(summary, previous))

    lines.extend(["", "## Kiosk Comparison"])
    for kiosk, values in sorted(summary["kiosks"].items()):
        previous_values = previous["kiosks"].get(kiosk) if previous else None
        lines.append(
            f"- **{kiosk}:** quality {rating(values['average_food_quality_rating'])}, "
            f"quantity {rating(values['average_food_quantity_rating'])}, "
            f"{waste_per_report[kiosk]} unclaimed lunches per report"
            f"{kiosk_month_direction(values, previous_values)}."
        )

    lines.extend(["", "## Recurring Trends"])
    recurring = [
        (category, records)
        for category, records in period_events.items()
        if records and not event_is_sensitive(category, records)
    ]
    if not recurring:
        lines.append("- No recurring source-backed trend met the current monthly threshold.")
    else:
        for category, records in recurring:
            lines.append(
                f"- {event_label(category, records)}: {len(records)} reports. "
                f"Sources: {source_list(records)}"
            )

    lines.extend(["", "## Workflow Efficiency Indicators"])
    operational_records = [
        record
        for category in (
            "operational_issue:equipment_failure",
            "inventory:inconsistent_prep",
            "cross_kiosk:register_disruption_week_7",
        )
        for record in period_events.get(category, [])
    ]
    if operational_records:
        lines.append(
            f"- {len(operational_records)} reports described equipment, register, inventory, "
            "or prep friction that may have affected workflow."
        )
        lines.append(f"- Sources: {source_list(operational_records)}")
    else:
        lines.append("- No repeated workflow-friction signal met the current threshold.")
    lines.append(
        "- These are operational-efficiency indicators, not confirmed productivity measurements; "
        "labor hours, transaction volume, and service-time data are not available."
    )

    lines.extend(["", "## Team Recognition"])
    recognition = period_events.get("recognition:maya_chen", [])
    if recognition:
        lines.append(
            f"- Maya Chen was positively recognized in {len(recognition)} reports. "
            f"Sources: {source_list(recognition)}"
        )
    else:
        lines.append("- No repeated named recognition trend met the current threshold.")

    lines.extend(["", "## Reporting Compliance"])
    lines.append(
        f"- Valid report rate: {round((summary['valid_reports'] / summary['expected_reports']) * 100, 2)}%"
    )
    for row in missing_rows:
        lines.append(f"- Missing: {row['kiosk']} on {row['date']}")
    for row in invalid_rows:
        lines.append(f"- Data review: {row['kiosk']} on {row['date']} ({row['issue']})")

    lines.extend(["", "## Management Priorities"])
    priorities = monthly_priorities(
        highest_waste,
        period_events,
        summary,
    )
    lines.extend(f"- {priority}" for priority in priorities)

    sensitive = [
        record
        for category, records in period_events.items()
        if event_is_sensitive(category, records)
        for record in records
    ]
    if sensitive:
        lines.extend(
            [
                "",
                "## Sensitive Note Requiring Inspection",
                "- An ambiguous personnel note was detected. It must not be treated as evidence "
                "of misconduct or used for autonomous personnel action.",
                f"- Inspect source: {source_list(sensitive)}",
            ]
        )

    lines.extend(
        [
            "",
            "## Interpretation and Data Limits",
            "- Menu-specific findings reflect only dishes explicitly named in shift reports; "
            "the rotating weekly menu schedule is not an input.",
            "- Financial impact is described as a possible opportunity because food-cost, revenue, "
            "transaction-volume, and labor-hour data are unavailable.",
            "- Ted can inspect supporting reports and challenge a claim through the planned "
            "post-delivery correction workflow.",
            "",
        ]
    )
    return "\n".join(lines)


def reports_for_week(
    reports: list[dict[str, Any]],
    schedule: list[dict[str, str]],
    week: int,
) -> list[dict[str, Any]]:
    slots = {
        (row["kiosk"], row["date"])
        for row in schedule
        if int(row["week"]) == week
    }
    return [
        report
        for report in reports
        if (report["kiosk"], report["date"]) in slots
    ]


def events_for_reports(
    events: dict[str, list[dict[str, Any]]],
    reports: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    source_ids = {report["source_submission_id"] for report in reports}
    return {
        category: [
            record
            for record in records
            if record["source_submission_id"] in source_ids
        ]
        for category, records in events.items()
    }


def filter_events(
    events: dict[str, list[dict[str, Any]]],
    kiosk: str,
) -> dict[str, list[dict[str, Any]]]:
    return {
        category: [record for record in records if record["kiosk"] == kiosk]
        for category, records in events.items()
    }


def weekly_attention_items(
    summary: dict[str, Any],
    previous: dict[str, Any] | None,
    events: dict[str, list[dict[str, Any]]],
) -> list[str]:
    items: list[str] = []
    if summary["missing_or_invalid_reports"]:
        report_word = (
            "report"
            if summary["missing_or_invalid_reports"] == 1
            else "reports"
        )
        items.append(
            f"{summary['missing_or_invalid_reports']} expected {report_word} "
            f"{'was' if report_word == 'report' else 'were'} missing or invalid."
        )
    lowest_quantity = min(
        summary["kiosks"],
        key=lambda kiosk: summary["kiosks"][kiosk]["average_food_quantity_rating"],
    )
    items.append(
        f"{lowest_quantity} had the lowest average food-quantity rating "
        f"({summary['kiosks'][lowest_quantity]['average_food_quantity_rating']}/5)."
    )
    highest_waste = max(
        summary["kiosks"],
        key=lambda kiosk: summary["kiosks"][kiosk]["total_unclaimed_lunches"],
    )
    items.append(
        f"{highest_waste} recorded the most unclaimed lunches "
        f"({summary['kiosks'][highest_waste]['total_unclaimed_lunches']})."
    )
    event_counts = [
        (category, len(records))
        for category, records in events.items()
        if records
        and not event_is_sensitive(category, records)
        and "other_operational_issue" not in category
    ]
    if event_counts:
        category, count = max(event_counts, key=lambda item: item[1])
        items.append(
            f"The most repeated source-backed signal was {event_label(category, events[category])} "
            f"({count} reports)."
        )
    if previous:
        quality_delta = metric_delta(
            summary["overall"]["average_food_quality_rating"],
            previous["overall"]["average_food_quality_rating"],
        )
        items.append(
            f"System-wide food quality {direction_phrase(quality_delta)} from the previous week."
        )
    return items


def kiosk_week_summary(
    summary: dict[str, Any],
    events: dict[str, list[dict[str, Any]]],
) -> str:
    phrases: list[str] = []
    if summary["average_food_quality_rating"] is None:
        return "No valid reports were available for this kiosk."
    if summary["average_food_quality_rating"] >= 4:
        phrases.append("Food quality remained positive")
    elif summary["average_food_quality_rating"] < 3:
        phrases.append("Food quality requires attention")
    else:
        phrases.append("Food quality was mixed")
    if summary["average_food_quantity_rating"] < 3:
        phrases.append("quantity and prep consistency were the main concern")
    elif summary["average_food_quantity_rating"] >= 4:
        phrases.append("reported quantity levels were generally stable")
    else:
        phrases.append("quantity performance was moderate")
    categories = [category for category, records in events.items() if records]
    if categories:
        phrases.append(
            f"reports also noted {event_label(categories[0], events[categories[0]])}"
        )
    return "; ".join(phrases) + "."


def monthly_priorities(
    highest_waste: str,
    events: dict[str, list[dict[str, Any]]],
    summary: dict[str, Any],
) -> list[str]:
    priorities = [
        f"Review prep and unclaimed-lunch patterns at {highest_waste}; validate against meal volume before reducing production."
    ]
    for category in (
        "food_shortage:kung_pao_chicken",
        "operational_issue:equipment_failure",
        "inventory:inconsistent_prep",
        "guest_theme:dietary_or_allergy_question",
    ):
        if events.get(category):
            priorities.append(event_follow_up(category, events[category]))
    if summary["missing_or_invalid_reports"]:
        priorities.append("Follow up on missing and malformed reports to improve management visibility.")
    return list(dict.fromkeys(priorities))[:5]


def event_label(category: str, records: list[dict[str, Any]] | None = None) -> str:
    if records:
        label = records[0].get("label")
        if label:
            return str(label)
    return EVENT_LABELS.get(category, category.replace(":", " - ").replace("_", " "))


def event_follow_up(category: str, records: list[dict[str, Any]] | None = None) -> str:
    if records:
        follow_up = records[0].get("follow_up")
        if follow_up:
            return str(follow_up)
    return EVENT_FOLLOW_UPS.get(
        category,
        "Inspect source reports and decide whether follow-up is needed.",
    )


def event_is_sensitive(
    category: str,
    records: list[dict[str, Any]] | None = None,
) -> bool:
    if category == SENSITIVE_CATEGORY:
        return True
    return any(bool(record.get("sensitive")) for record in records or [])


def month_direction_lines(
    summary: dict[str, Any],
    previous: dict[str, Any],
) -> list[str]:
    return [
        f"- Food quality {direction_phrase(metric_delta(summary['overall']['average_food_quality_rating'], previous['overall']['average_food_quality_rating']))}.",
        f"- Food quantity {direction_phrase(metric_delta(summary['overall']['average_food_quantity_rating'], previous['overall']['average_food_quantity_rating']))}.",
        f"- Unclaimed lunches per valid report {direction_phrase(metric_delta(waste_rate(summary), waste_rate(previous)))}.",
        f"- Valid reporting rate {direction_phrase(metric_delta(valid_rate(summary), valid_rate(previous)))}.",
    ]


def kiosk_month_direction(
    values: dict[str, Any],
    previous: dict[str, Any] | None,
) -> str:
    if not previous:
        return ""
    quality = direction_word(
        metric_delta(
            values["average_food_quality_rating"],
            previous["average_food_quality_rating"],
        )
    )
    quantity = direction_word(
        metric_delta(
            values["average_food_quantity_rating"],
            previous["average_food_quantity_rating"],
        )
    )
    return f"; quality {quality}, quantity {quantity} versus the previous month"


def source_list(records: list[dict[str, Any]]) -> str:
    return ", ".join(record["source_submission_id"] for record in records)


def rating(value: float | int | None) -> str:
    return "N/A" if value is None else f"{value}/5"


def metric_delta(current: float | int | None, previous: float | int | None) -> float:
    if current is None or previous is None:
        return 0.0
    return round(float(current) - float(previous), 2)


def change_text(
    current: float | int | None,
    previous: dict[str, Any] | None,
    field: str,
    *,
    points: bool = True,
) -> str:
    if not previous or current is None or previous.get(field) is None:
        return ""
    delta = metric_delta(current, previous[field])
    unit = " points" if points else ""
    sign = "+" if delta > 0 else ""
    return f" ({sign}{delta}{unit} vs prior week)"


def rate_change_text(
    summary: dict[str, Any],
    previous: dict[str, Any] | None,
) -> str:
    if not previous:
        return ""
    current_rate = report_rate(
        summary["total_unclaimed_lunches"],
        summary["report_count"],
    )
    previous_rate = report_rate(
        previous["total_unclaimed_lunches"],
        previous["report_count"],
    )
    delta = metric_delta(current_rate, previous_rate)
    sign = "+" if delta > 0 else ""
    return f" ({sign}{delta} per report vs prior week)"


def month_change_text(
    summary: dict[str, Any],
    previous: dict[str, Any] | None,
    field: str,
) -> str:
    if not previous:
        return ""
    delta = metric_delta(summary["overall"][field], previous["overall"][field])
    sign = "+" if delta > 0 else ""
    return f" ({sign}{delta} vs prior month)"


def month_rate_change(
    summary: dict[str, Any],
    previous: dict[str, Any] | None,
) -> str:
    if not previous:
        return ""
    delta = metric_delta(waste_rate(summary), waste_rate(previous))
    sign = "+" if delta > 0 else ""
    return f" ({sign}{delta} vs prior month)"


def waste_rate(summary: dict[str, Any]) -> float:
    return round(
        summary["overall"]["total_unclaimed_lunches"] / summary["valid_reports"],
        2,
    )


def report_rate(total: int, report_count: int) -> float:
    if not report_count:
        return 0.0
    return round(total / report_count, 2)


def valid_rate(summary: dict[str, Any]) -> float:
    return round((summary["valid_reports"] / summary["expected_reports"]) * 100, 2)


def direction_phrase(delta: float) -> str:
    if delta > 0.05:
        return f"increased by {delta}"
    if delta < -0.05:
        return f"decreased by {abs(delta)}"
    return "remained approximately stable"


def direction_word(delta: float) -> str:
    if delta > 0.05:
        return "improved"
    if delta < -0.05:
        return "declined"
    return "was stable"


def friendly_date(value: str, include_year: bool = False) -> str:
    parsed = datetime.strptime(value, "%Y-%m-%d")
    if include_year:
        return f"{parsed.strftime('%B')} {parsed.day}, {parsed.year}"
    return f"{parsed.strftime('%B')} {parsed.day}"


def is_partial_month(schedule_rows: list[dict[str, str]]) -> bool:
    final_date = datetime.strptime(max(row["date"] for row in schedule_rows), "%Y-%m-%d")
    final_day = calendar.monthrange(final_date.year, final_date.month)[1]
    return final_date.day < final_day


def empty_summary() -> dict[str, Any]:
    return {
        "report_count": 0,
        "average_food_quality_rating": None,
        "average_food_quantity_rating": None,
        "total_unclaimed_lunches": 0,
    }


def load_and_generate(dataset_dir: Path) -> dict[str, list[Path]]:
    reports = read_json(dataset_dir / "normalized_reports.json")
    schedule = load_schedule(dataset_dir / "expected_reporting_schedule.csv")
    ground_truth = read_json(dataset_dir / "ground_truth.json")
    ai_path = dataset_dir / "ai_extractions.json"
    semantic_extractions = read_json(ai_path) if ai_path.exists() else None
    return generate_final_briefings(
        reports,
        schedule,
        ground_truth,
        dataset_dir / "briefings",
        semantic_extractions=semantic_extractions,
    )
