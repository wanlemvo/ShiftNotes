from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any


FIELD_ALIASES = {
    "date": {"date", "shift date"},
    "kiosk": {"kiosk", "kiosk / station", "station", "location"},
    "lead_name": {"lead name", "shift lead", "lead"},
    "food_quality_rating": {"food quality rating", "quality rating"},
    "food_quantity_rating": {"food quantity rating", "quantity rating"},
    "food_concerns_or_outages": {
        "food concerns or outages",
        "food concerns",
        "outages",
    },
    "team_members_who_did_well": {
        "team members who did well",
        "team members who did well!",
        "team recognition",
    },
    "guest_issues_for_the_day": {
        "guest issues for the day",
        "guest issues",
        "guest feedback",
    },
    "operational_notes": {"operational notes", "operations notes"},
    "number_of_unclaimed_lunches": {
        "number of unclaimed lunches",
        "unclaimed lunches",
    },
}


@dataclass
class ShiftReport:
    source_submission_id: str
    submitted_at: str
    date: str = ""
    kiosk: str = ""
    lead_name: str = ""
    food_quality_rating: int | None = None
    food_quantity_rating: int | None = None
    food_concerns_or_outages: str = ""
    team_members_who_did_well: str = ""
    guest_issues_for_the_day: str = ""
    operational_notes: str = ""
    number_of_unclaimed_lunches: int | None = None
    parse_status: str = "valid"
    validation_errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_label(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().replace("_", " ").split())


def canonical_field(label: str) -> str | None:
    normalized = normalize_label(label)
    for field, aliases in FIELD_ALIASES.items():
        if normalized in aliases:
            return field
    return None


def extract_answer_value(answer: Any) -> Any:
    if isinstance(answer, dict):
        for key in ("answer", "prettyFormat", "value"):
            if key in answer and answer[key] not in (None, ""):
                return answer[key]
        if "text" in answer:
            return answer["text"]
        return ""
    if isinstance(answer, list):
        return ", ".join(str(item) for item in answer)
    return answer


def parse_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return int(value)

    text = str(value).strip()
    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return None
    return int(digits)


def parse_date(value: Any) -> str:
    if value in (None, ""):
        return ""

    if isinstance(value, dict):
        if value.get("datetime"):
            return parse_date(value["datetime"])
        year = value.get("year")
        month = value.get("month")
        day = value.get("day")
        if year and month and day:
            return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
        return ""

    text = str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m-%d-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    return text


def submission_answers(submission: dict[str, Any]) -> dict[str, Any]:
    answers = submission.get("answers", {})
    extracted: dict[str, Any] = {}

    for answer in answers.values():
        if not isinstance(answer, dict):
            continue
        label = answer.get("text") or answer.get("name") or answer.get("label")
        field = canonical_field(str(label or ""))
        if not field:
            continue
        extracted[field] = extract_answer_value(answer)

    return extracted


def normalize_submission(submission: dict[str, Any]) -> dict[str, Any]:
    values = submission_answers(submission)

    report = ShiftReport(
        source_submission_id=str(submission.get("id", "")),
        submitted_at=str(
            submission.get("created_at")
            or submission.get("updated_at")
            or submission.get("created")
            or ""
        ),
        date=parse_date(values.get("date")),
        kiosk=str(values.get("kiosk", "") or ""),
        lead_name=str(values.get("lead_name", "") or ""),
        food_quality_rating=parse_int(values.get("food_quality_rating")),
        food_quantity_rating=parse_int(values.get("food_quantity_rating")),
        food_concerns_or_outages=str(values.get("food_concerns_or_outages", "") or ""),
        team_members_who_did_well=str(values.get("team_members_who_did_well", "") or ""),
        guest_issues_for_the_day=str(values.get("guest_issues_for_the_day", "") or ""),
        operational_notes=str(values.get("operational_notes", "") or ""),
        number_of_unclaimed_lunches=parse_int(values.get("number_of_unclaimed_lunches")),
    )

    errors = validate_report(report)
    report.validation_errors = errors
    report.parse_status = "valid" if not errors else "needs_review"
    return report.to_dict()


def normalize_submissions(api_response: dict[str, Any]) -> list[dict[str, Any]]:
    submissions = api_response.get("content", [])
    if not isinstance(submissions, list):
        raise ValueError("Expected JotForm API response content to be a list.")
    return [normalize_submission(submission) for submission in submissions]


def validate_report(report: ShiftReport) -> list[str]:
    errors: list[str] = []

    if not report.source_submission_id:
        errors.append("missing source_submission_id")
    if not report.date:
        errors.append("missing date")
    if not report.kiosk:
        errors.append("missing kiosk")
    if not report.lead_name:
        errors.append("missing lead_name")

    for field_name, rating in (
        ("food_quality_rating", report.food_quality_rating),
        ("food_quantity_rating", report.food_quantity_rating),
    ):
        if rating is None:
            errors.append(f"missing {field_name}")
        elif rating < 1 or rating > 5:
            errors.append(f"{field_name} out of range")

    if report.number_of_unclaimed_lunches is None:
        errors.append("missing number_of_unclaimed_lunches")
    elif report.number_of_unclaimed_lunches < 0:
        errors.append("number_of_unclaimed_lunches cannot be negative")

    return errors
