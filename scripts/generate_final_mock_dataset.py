from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from random import Random
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "final_project" / "src"))

from shiftnotes.normalize import normalize_submissions


OUTPUT_DIR = ROOT / "final_project" / "data" / "final_mock"
START_DATE = date(2026, 3, 2)
WEEKS = 12
SERVICE_WEEKDAYS = (0, 1, 2, 3)  # Monday through Thursday
SEED = 20260621


@dataclass(frozen=True)
class KioskProfile:
    name: str
    leads: tuple[str, ...]
    employees: tuple[str, ...]
    menu_items: tuple[str, ...]
    baseline_quality: tuple[int, int]
    baseline_quantity: tuple[int, int]
    baseline_waste: tuple[int, int]
    primary_pattern: str


PROFILES = (
    KioskProfile(
        "Bowls & Buns",
        ("Maria Santos", "Dominick Bavilacqua", "Chris Taylor"),
        ("Dom", "Maria", "Chris", "Iris"),
        ("Kung Pao chicken", "tofu stir-fry", "rice", "mac salad"),
        (3, 5),
        (2, 4),
        (0, 6),
        "chicken_shortage",
    ),
    KioskProfile(
        "Market Grill",
        ("Nina Rivera", "Sam Kim", "Jordan Lee"),
        ("Nina", "Sam", "Jordan", "Elena"),
        ("grilled chicken", "turkey burger", "roasted potatoes", "seasonal vegetables"),
        (4, 5),
        (3, 5),
        (7, 12),
        "high_waste",
    ),
    KioskProfile(
        "Verde Kitchen",
        ("Priya Nair", "Taylor Morgan", "Jules Adams"),
        ("Priya", "Taylor", "Jules", "Avery"),
        ("tofu bowl", "black bean bowl", "quinoa", "avocado salsa"),
        (4, 5),
        (3, 5),
        (1, 5),
        "dietary_questions",
    ),
    KioskProfile(
        "Coastal Cafe",
        ("Omar Lewis", "Anika Jones", "Lee Vaughn"),
        ("Omar", "Anika", "Lee", "Noah"),
        ("fish sandwich", "clam chowder", "side salad", "fruit cup"),
        (3, 5),
        (3, 5),
        (2, 7),
        "equipment_friction",
    ),
    KioskProfile(
        "Hearth & Grain",
        ("Grace Hall", "Mina Chen", "Andre Price"),
        ("Grace", "Mina", "Andre", "Luis"),
        ("roasted chicken", "farro bowl", "seasonal soup", "herb vegetables"),
        (4, 5),
        (4, 5),
        (0, 4),
        "employee_recognition",
    ),
    KioskProfile(
        "Street Eats",
        ("Ben Walker", "Iris Quinn", "Maya Ross"),
        ("Ben", "Iris", "Maya", "Devin"),
        ("beef tacos", "tofu tacos", "cilantro rice", "street corn"),
        (3, 5),
        (2, 5),
        (2, 8),
        "inventory_inconsistency",
    ),
)


QUIET_FOOD = (
    "Food held well throughout service and prep levels matched demand.",
    "No food concerns today; quality and quantity remained consistent.",
    "All menu items stayed available and presentation was strong.",
)
QUIET_GUEST = (
    "No major guest issues today.",
    "Guests were positive and service moved smoothly.",
    "One guest complimented the team and no concerns were reported.",
)
QUIET_OPERATIONS = (
    "No major operational concerns.",
    "Opening, service, and closing procedures ran normally.",
    "The shift stayed organized with no unusual delays.",
)
GENERAL_RECOGNITION = (
    "{employee} communicated clearly and helped the line recover during the rush.",
    "{employee} kept the station organized and supported teammates throughout service.",
    "{employee} handled guest questions professionally and maintained a steady pace.",
)
GUEST_VARIETY = (
    "A guest requested a lower-sodium option.",
    "Two guests asked for a spicier sauce.",
    "A guest asked whether a beverage option could be added.",
    "Several guests complimented the food quality.",
    "One guest said the portion felt small for the price.",
    "A guest asked when a previous seasonal item might return.",
)


MISSING_SLOTS = {
    ("Bowls & Buns", "2026-03-18"),
    ("Bowls & Buns", "2026-04-20"),
    ("Bowls & Buns", "2026-05-14"),
    ("Market Grill", "2026-03-10"),
    ("Market Grill", "2026-04-08"),
    ("Market Grill", "2026-05-05"),
    ("Verde Kitchen", "2026-03-26"),
    ("Verde Kitchen", "2026-04-13"),
    ("Verde Kitchen", "2026-05-19"),
    ("Coastal Cafe", "2026-03-03"),
    ("Coastal Cafe", "2026-04-23"),
    ("Coastal Cafe", "2026-05-11"),
    ("Hearth & Grain", "2026-03-31"),
    ("Hearth & Grain", "2026-04-27"),
    ("Hearth & Grain", "2026-05-21"),
    ("Street Eats", "2026-03-12"),
    ("Street Eats", "2026-04-06"),
    ("Street Eats", "2026-05-20"),
}

MALFORMED_SLOTS = {
    ("Bowls & Buns", "2026-03-24"): "missing lead name",
    ("Coastal Cafe", "2026-04-14"): "missing food quantity rating",
    ("Street Eats", "2026-05-07"): "missing unclaimed lunch count",
}

DUPLICATE_SOURCE_IDS = ("FM-0031", "FM-0117", "FM-0229")


def scheduled_dates() -> list[date]:
    dates: list[date] = []
    for week in range(WEEKS):
        week_start = START_DATE + timedelta(days=week * 7)
        dates.extend(week_start + timedelta(days=offset) for offset in SERVICE_WEEKDAYS)
    return dates


def week_number(report_date: date) -> int:
    return ((report_date - START_DATE).days // 7) + 1


def make_answer(text: str, answer: Any) -> dict[str, Any]:
    return {"text": text, "answer": answer}


def build_report_content(
    profile: KioskProfile,
    report_date: date,
    day_index: int,
    rng: Random,
) -> tuple[dict[str, Any], list[str]]:
    week = week_number(report_date)
    quality = rng.randint(*profile.baseline_quality)
    quantity = rng.randint(*profile.baseline_quantity)
    waste = rng.randint(*profile.baseline_waste)
    employee = profile.employees[(week + day_index) % len(profile.employees)]
    food = rng.choice(QUIET_FOOD)
    guest = rng.choice((*QUIET_GUEST, *GUEST_VARIETY))
    operations = rng.choice(QUIET_OPERATIONS)
    recognition = rng.choice(GENERAL_RECOGNITION).format(employee=employee)
    tags: list[str] = []

    if profile.primary_pattern == "chicken_shortage" and (
        day_index == 0 or (week % 2 == 0 and day_index == 2)
    ):
        food = rng.choice(
            (
                "Kung Pao chicken ran low during the lunch rush and backup prep was started.",
                "Kung Pao chicken sold out near 1 PM while tofu stir-fry remained available.",
                "Chicken prep was below demand and the final pan ran close to shortage.",
            )
        )
        operations = "Recommend increasing Kung Pao chicken prep before peak service."
        quantity = rng.randint(2, 3)
        tags.append("food_shortage:kung_pao_chicken")

    if profile.primary_pattern == "high_waste":
        operations = rng.choice(
            (
                "Unclaimed lunches were above target and closing waste should be reviewed.",
                "Production exceeded afternoon demand; reduce backup prep on slower days.",
                "Several prepared meals remained after service despite steady quality.",
            )
        )
        tags.append("waste:high_unclaimed_lunches")
        if week in (7, 8):
            waste += 4
            tags.append("cross_kiosk:waste_spike_weeks_7_8")

    if profile.primary_pattern == "dietary_questions" and day_index in (1, 3):
        guest = rng.choice(
            (
                "Three guests asked whether the tofu bowl was vegan.",
                "Guests asked about gluten-free ingredients and possible cross-contact.",
                "Two guests requested clearer allergy information for the avocado salsa.",
                "A guest asked whether the black bean bowl contained dairy.",
            )
        )
        tags.append("guest_theme:dietary_or_allergy_question")

    if profile.primary_pattern == "equipment_friction" and day_index == 1:
        operations = rng.choice(
            (
                "The register froze during lunch and slowed the line for several minutes.",
                "The receipt printer failed twice and orders had to be called manually.",
                "The warming unit required a reset and created a pickup bottleneck.",
            )
        )
        tags.append("operational_issue:equipment_failure")

    if profile.primary_pattern == "employee_recognition" and day_index in (0, 2):
        recognition = rng.choice(
            (
                "Maya Chen kept the line moving and coached a newer employee during the rush.",
                "Maya Chen noticed a prep issue early and coordinated a quick recovery.",
                "Maya Chen received positive guest feedback for patient, clear service.",
            )
        )
        tags.append("recognition:maya_chen")

    if profile.primary_pattern == "inventory_inconsistency" and (
        day_index == 3 or (week % 2 == 1 and day_index == 1)
    ):
        food = rng.choice(
            (
                "Cilantro rice ran low while extra street corn remained at closing.",
                "Tofu taco prep did not match demand and beef tacos were overprepared.",
                "Inventory counts did not match the remaining taco portions near closing.",
            )
        )
        operations = "The handoff should include clearer remaining-inventory counts."
        quantity = rng.randint(2, 3)
        tags.append("inventory:inconsistent_prep")

    if week == 7 and day_index == 2:
        operations = (
            f"{operations} "
            "The shared register connection dropped briefly and delayed service."
        )
        tags.append("cross_kiosk:register_disruption_week_7")

    if week in (9, 10) and day_index == 0:
        guest = rng.choice(
            (
                "Several guests said portions looked smaller than earlier in the month.",
                "Two guests questioned whether the serving size had changed.",
                "A guest complained that the portion did not match the listed value.",
            )
        )
        tags.append("cross_kiosk:portion_complaints_weeks_9_10")

    if week == 11 and day_index == 3:
        guest = (
            f"{guest} "
            "Guests asked for more beverage variety, including unsweetened options."
        )
        tags.append("guest_request:beverage_variety")

    if week == 12 and day_index == 1 and profile.name in ("Bowls & Buns", "Verde Kitchen"):
        guest = "A guest asked for clearer allergen labels before choosing a meal."
        tags.append("guest_theme:dietary_or_allergy_question")

    if week == 8 and day_index == 2 and profile.name == "Coastal Cafe":
        operations = (
            "Tony seemed frustrated and stepped away twice, but the report does not establish "
            "misconduct or a performance conclusion."
        )
        tags.append("sensitive_personnel:ambiguous_comment")

    return (
        {
            "lead_name": profile.leads[(week + day_index) % len(profile.leads)],
            "food_quality_rating": quality,
            "food_quantity_rating": quantity,
            "food_concerns_or_outages": food,
            "team_members_who_did_well": recognition,
            "guest_issues_for_the_day": guest,
            "operational_notes": operations,
            "number_of_unclaimed_lunches": waste,
        },
        tags,
    )


def make_submission(
    source_id: str,
    profile: KioskProfile,
    report_date: date,
    content: dict[str, Any],
) -> dict[str, Any]:
    submitted_at = datetime.combine(report_date, time(18, 15)).isoformat(sep=" ")
    return {
        "id": source_id,
        "created_at": submitted_at,
        "answers": {
            "1": make_answer("Date", report_date.isoformat()),
            "2": make_answer("Kiosk / Station", profile.name),
            "3": make_answer("Lead Name", content["lead_name"]),
            "4": make_answer("Food Quality Rating", str(content["food_quality_rating"])),
            "5": make_answer("Food Quantity Rating", str(content["food_quantity_rating"])),
            "6": make_answer(
                "Food Concerns or Outages",
                content["food_concerns_or_outages"],
            ),
            "7": make_answer(
                "Team Members Who Did Well",
                content["team_members_who_did_well"],
            ),
            "8": make_answer(
                "Guest Issues for the Day",
                content["guest_issues_for_the_day"],
            ),
            "9": make_answer("Operational Notes", content["operational_notes"]),
            "10": make_answer(
                "Number of Unclaimed Lunches",
                str(content["number_of_unclaimed_lunches"]),
            ),
        },
    }


def apply_malformed_case(submission: dict[str, Any], reason: str) -> None:
    answer_key = {
        "missing lead name": "3",
        "missing food quantity rating": "5",
        "missing unclaimed lunch count": "10",
    }[reason]
    submission["answers"].pop(answer_key)


def build_dataset() -> dict[str, Any]:
    rng = Random(SEED)
    submissions: list[dict[str, Any]] = []
    schedule: list[dict[str, Any]] = []
    events: dict[str, list[dict[str, str]]] = defaultdict(list)
    source_lookup: dict[str, dict[str, Any]] = {}
    sequence = 1

    for report_date in scheduled_dates():
        day_index = SERVICE_WEEKDAYS.index(report_date.weekday())
        week = week_number(report_date)
        for profile in PROFILES:
            source_id = f"FM-{sequence:04d}"
            sequence += 1
            slot = (profile.name, report_date.isoformat())

            if slot in MISSING_SLOTS:
                schedule.append(
                    {
                        "expected_report_id": source_id,
                        "date": report_date.isoformat(),
                        "week": week,
                        "kiosk": profile.name,
                        "status": "missing",
                        "submission_id": "",
                        "issue": "expected report was not submitted",
                    }
                )
                continue

            content, tags = build_report_content(profile, report_date, day_index, rng)
            submission = make_submission(source_id, profile, report_date, content)
            status = "valid"
            issue = ""

            if slot in MALFORMED_SLOTS:
                status = "malformed"
                issue = MALFORMED_SLOTS[slot]
                apply_malformed_case(submission, issue)

            submissions.append(submission)
            source_lookup[source_id] = submission
            schedule.append(
                {
                    "expected_report_id": source_id,
                    "date": report_date.isoformat(),
                    "week": week,
                    "kiosk": profile.name,
                    "status": status,
                    "submission_id": source_id,
                    "issue": issue,
                }
            )

            for tag in tags:
                events[tag].append(
                    {
                        "source_submission_id": source_id,
                        "date": report_date.isoformat(),
                        "week": str(week),
                        "kiosk": profile.name,
                    }
                )

    duplicates: list[dict[str, str]] = []
    for duplicate_number, original_id in enumerate(DUPLICATE_SOURCE_IDS, start=1):
        duplicate = deepcopy(source_lookup[original_id])
        duplicate_id = f"DUP-{duplicate_number:03d}"
        duplicate["id"] = duplicate_id
        duplicate["created_at"] = duplicate["created_at"].replace("18:15:00", "18:22:00")
        submissions.append(duplicate)
        duplicates.append(
            {
                "duplicate_submission_id": duplicate_id,
                "original_submission_id": original_id,
            }
        )

    normalized = normalize_submissions({"content": submissions})
    validation_counts = Counter(report["parse_status"] for report in normalized)
    schedule_counts = Counter(row["status"] for row in schedule)
    kiosk_counts = Counter(row["kiosk"] for row in schedule)

    ground_truth = {
        "dataset_version": "1.0",
        "seed": SEED,
        "period": {
            "start_date": START_DATE.isoformat(),
            "end_date": scheduled_dates()[-1].isoformat(),
            "weeks": WEEKS,
            "service_days_per_week": len(SERVICE_WEEKDAYS),
        },
        "expected_schedule": {
            "total_expected": len(schedule),
            "valid_scheduled": schedule_counts["valid"],
            "missing": schedule_counts["missing"],
            "malformed": schedule_counts["malformed"],
        },
        "duplicates": duplicates,
        "events": {
            tag: {
                "expected_count": len(records),
                "source_records": records,
            }
            for tag, records in sorted(events.items())
        },
        "benchmark_questions": [
            "Which kiosk has the highest total unclaimed lunches?",
            "Which kiosk repeatedly experiences food shortages?",
            "Which employee is recognized most frequently?",
            "Which kiosk has the most equipment-related operational friction?",
            "Which kiosk receives the most dietary or allergy questions?",
            "Which kiosk has the most inconsistent inventory notes?",
            "Which kiosk/date reports are missing?",
            "What cross-kiosk issues increased during Weeks 7 through 10?",
        ],
    }

    validation_summary = {
        "seed": SEED,
        "expected_schedule_rows": len(schedule),
        "scheduled_status_counts": dict(sorted(schedule_counts.items())),
        "payload_submission_count": len(submissions),
        "unique_scheduled_submission_count": len(submissions) - len(duplicates),
        "duplicate_submission_count": len(duplicates),
        "normalized_status_counts": dict(sorted(validation_counts.items())),
        "kiosk_expected_counts": dict(sorted(kiosk_counts.items())),
        "date_count": len(scheduled_dates()),
        "week_count": WEEKS,
        "ground_truth_event_counts": {
            tag: len(records) for tag, records in sorted(events.items())
        },
    }

    return {
        "api_response": {"content": submissions},
        "schedule": schedule,
        "ground_truth": ground_truth,
        "normalized": normalized,
        "validation_summary": validation_summary,
    }


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def write_schedule(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_normalized_csv(path: Path, reports: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(reports[0]))
        writer.writeheader()
        writer.writerows(reports)


def write_generation_log(path: Path, dataset: dict[str, Any]) -> None:
    summary = dataset["validation_summary"]
    path.write_text(
        "\n".join(
            (
                "# Final Mock Dataset Generation Log",
                "",
                "Generated deterministically for ShiftNotes.",
                "",
                f"- Seed: `{summary['seed']}`",
                f"- Expected schedule rows: `{summary['expected_schedule_rows']}`",
                f"- Payload submissions: `{summary['payload_submission_count']}`",
                f"- Duplicate submissions: `{summary['duplicate_submission_count']}`",
                f"- Scheduled statuses: `{summary['scheduled_status_counts']}`",
                f"- Normalized statuses: `{summary['normalized_status_counts']}`",
                f"- Weeks: `{summary['week_count']}`",
                f"- Reporting dates: `{summary['date_count']}`",
                "",
                "The generator can be rerun with:",
                "",
                "```bash",
                "python scripts/generate_final_mock_dataset.py",
                "```",
                "",
            )
        ),
        encoding="utf-8",
    )


def write_dataset(dataset: dict[str, Any], output_dir: Path = OUTPUT_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "jotform_submissions.json", dataset["api_response"])
    write_schedule(output_dir / "expected_reporting_schedule.csv", dataset["schedule"])
    write_json(output_dir / "ground_truth.json", dataset["ground_truth"])
    write_json(output_dir / "normalized_reports.json", dataset["normalized"])
    write_normalized_csv(output_dir / "normalized_reports.csv", dataset["normalized"])
    write_json(output_dir / "validation_summary.json", dataset["validation_summary"])
    write_generation_log(output_dir / "GENERATION_LOG.md", dataset)


def main() -> None:
    dataset = build_dataset()
    write_dataset(dataset)
    summary = dataset["validation_summary"]
    print(f"Wrote final mock dataset to {OUTPUT_DIR}")
    print(f"Expected schedule rows: {summary['expected_schedule_rows']}")
    print(f"Payload submissions: {summary['payload_submission_count']}")
    print(f"Scheduled statuses: {summary['scheduled_status_counts']}")
    print(f"Normalized statuses: {summary['normalized_status_counts']}")


if __name__ == "__main__":
    main()
