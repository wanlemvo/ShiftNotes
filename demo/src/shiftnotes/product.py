from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from shiftnotes.baseline import deduplicate_reports, detect_baseline_events
from shiftnotes.briefings import EVENT_LABELS, event_label, event_is_sensitive
from shiftnotes.semantic_events import semantic_events_from_extractions


SENSITIVE_CATEGORIES = {"sensitive_personnel:ambiguous_comment"}
PERSONNEL_TERMS = (
    "fire",
    "fired",
    "terminate",
    "termination",
    "discipline",
    "disciplinary",
    "accusation",
    "stealing",
    "write them up",
    "send everyone",
    "email everyone",
)
REVIEW_TERMS = (
    "wrong",
    "incorrect",
    "not accurate",
    "not a complaint",
    "praise",
    "positive",
    "remove",
    "exclude",
    "doesn't belong",
    "does not belong",
)


@dataclass(frozen=True)
class Claim:
    claim_id: str
    period_type: str
    period: str
    category: str
    label: str
    kiosk: str
    claim_text: str
    source_submission_ids: list[str]
    source_count: int
    sensitive: bool
    status: str = "active"


@dataclass(frozen=True)
class CorrectionProposal:
    proposal_id: str
    claim_id: str
    challenge_text: str
    original_claim_text: str
    proposed_claim_text: str
    original_source_ids: list[str]
    proposed_source_ids: list[str]
    removed_source_ids: list[str]
    rationale: str
    status: str
    requires_confirmation: bool
    safety_refusal: bool
    created_at: str


def build_claim_catalog(
    reports: list[dict[str, Any]],
    schedule: list[dict[str, str]],
    semantic_extractions: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    unique, _ = deduplicate_reports(reports)
    valid = [report for report in unique if report.get("parse_status") == "valid"]
    events = (
        semantic_events_from_extractions(semantic_extractions, valid)
        if semantic_extractions is not None
        else detect_baseline_events(valid)
    )
    report_lookup = {
        str(report["source_submission_id"]): report
        for report in valid
    }
    schedule_by_slot = {
        (row["kiosk"], row["date"]): row
        for row in schedule
    }

    claims: list[Claim] = []
    for period_type in ("weekly", "monthly"):
        grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
        for category, records in events.items():
            for record in records:
                report = report_lookup[record["source_submission_id"]]
                if period_type == "weekly":
                    row = schedule_by_slot[(report["kiosk"], report["date"])]
                    period = f"week-{int(row['week']):02d}"
                else:
                    period = str(report["date"])[:7]
                key = (period, category, str(report["kiosk"]))
                grouped.setdefault(key, []).append(record)

        for (period, category, kiosk), records in sorted(grouped.items()):
            source_ids = sorted(
                {str(record["source_submission_id"]) for record in records}
            )
            label = event_label(category, records)
            claim_id = slugify(f"{period_type}-{period}-{kiosk}-{category}")
            claims.append(
                Claim(
                    claim_id=claim_id,
                    period_type=period_type,
                    period=period,
                    category=category,
                    label=label,
                    kiosk=kiosk,
                    claim_text=claim_sentence(label, len(source_ids), kiosk),
                    source_submission_ids=source_ids,
                    source_count=len(source_ids),
                    sensitive=(
                        category in SENSITIVE_CATEGORIES
                        or event_is_sensitive(category, records)
                    ),
                )
            )
    return [asdict(claim) for claim in claims]


def build_source_bundle(
    claim: dict[str, Any],
    reports: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    lookup = {
        str(report.get("source_submission_id", "")): report
        for report in reports
    }
    bundle = []
    for source_id in claim["source_submission_ids"]:
        report = lookup.get(source_id)
        if not report:
            continue
        bundle.append(
            {
                "source_submission_id": source_id,
                "date": report.get("date", ""),
                "kiosk": report.get("kiosk", ""),
                "lead_name": report.get("lead_name", ""),
                "food_quality_rating": report.get("food_quality_rating"),
                "food_quantity_rating": report.get("food_quantity_rating"),
                "number_of_unclaimed_lunches": report.get(
                    "number_of_unclaimed_lunches"
                ),
                "food_concerns_or_outages": report.get(
                    "food_concerns_or_outages", ""
                ),
                "team_members_who_did_well": report.get(
                    "team_members_who_did_well", ""
                ),
                "guest_issues_for_the_day": report.get(
                    "guest_issues_for_the_day", ""
                ),
                "operational_notes": report.get("operational_notes", ""),
            }
        )
    return bundle


def propose_correction(
    claim: dict[str, Any],
    challenge_text: str,
    reports: list[dict[str, Any]],
) -> dict[str, Any]:
    challenge = " ".join(challenge_text.split())
    lowered = challenge.lower()
    created_at = datetime.now(timezone.utc).isoformat()
    proposal_id = slugify(f"{claim['claim_id']}-{created_at}")

    unsafe_reason = unsafe_request_reason(lowered)
    if unsafe_reason:
        proposal = CorrectionProposal(
            proposal_id=proposal_id,
            claim_id=claim["claim_id"],
            challenge_text=challenge,
            original_claim_text=claim["claim_text"],
            proposed_claim_text=claim["claim_text"],
            original_source_ids=list(claim["source_submission_ids"]),
            proposed_source_ids=list(claim["source_submission_ids"]),
            removed_source_ids=[],
            rationale=unsafe_reason,
            status="refused",
            requires_confirmation=False,
            safety_refusal=True,
            created_at=created_at,
        )
        return asdict(proposal)

    if not any(term in lowered for term in REVIEW_TERMS):
        proposal = CorrectionProposal(
            proposal_id=proposal_id,
            claim_id=claim["claim_id"],
            challenge_text=challenge,
            original_claim_text=claim["claim_text"],
            proposed_claim_text=claim["claim_text"],
            original_source_ids=list(claim["source_submission_ids"]),
            proposed_source_ids=list(claim["source_submission_ids"]),
            removed_source_ids=[],
            rationale=(
                "The challenge does not yet identify what is incorrect. "
                "Name a source ID or explain which evidence should be reconsidered."
            ),
            status="needs_clarification",
            requires_confirmation=False,
            safety_refusal=False,
            created_at=created_at,
        )
        return asdict(proposal)

    source_bundle = build_source_bundle(claim, reports)
    explicit_ids = {
        match.upper()
        for match in re.findall(r"\b(?:FM|DUP)-\d{3,4}\b", challenge, re.I)
    }
    removable = [
        source["source_submission_id"]
        for source in source_bundle
        if source["source_submission_id"] in explicit_ids
    ]

    if not removable and ("praise" in lowered or "positive" in lowered):
        removable = [
            source["source_submission_id"]
            for source in source_bundle
            if contains_positive_language(source)
        ][:1]

    if not removable and len(source_bundle) == 1 and any(
        term in lowered for term in ("wrong", "incorrect", "remove", "exclude")
    ):
        removable = [source_bundle[0]["source_submission_id"]]

    if not removable:
        proposal = CorrectionProposal(
            proposal_id=proposal_id,
            claim_id=claim["claim_id"],
            challenge_text=challenge,
            original_claim_text=claim["claim_text"],
            proposed_claim_text=claim["claim_text"],
            original_source_ids=list(claim["source_submission_ids"]),
            proposed_source_ids=list(claim["source_submission_ids"]),
            removed_source_ids=[],
            rationale=(
                "ShiftNotes could not determine which supporting report should "
                "change. Inspect the sources and include a source ID."
            ),
            status="needs_clarification",
            requires_confirmation=False,
            safety_refusal=False,
            created_at=created_at,
        )
        return asdict(proposal)

    proposed_ids = [
        source_id
        for source_id in claim["source_submission_ids"]
        if source_id not in removable
    ]
    proposed_text = claim_sentence(
        claim["label"],
        len(proposed_ids),
        claim["kiosk"],
    )
    proposal = CorrectionProposal(
        proposal_id=proposal_id,
        claim_id=claim["claim_id"],
        challenge_text=challenge,
        original_claim_text=claim["claim_text"],
        proposed_claim_text=proposed_text,
        original_source_ids=list(claim["source_submission_ids"]),
        proposed_source_ids=proposed_ids,
        removed_source_ids=removable,
        rationale=(
            f"Removed {', '.join(removable)} from this claim based on the "
            "manager's challenge. The proposal must be confirmed before it is saved."
        ),
        status="pending_confirmation",
        requires_confirmation=True,
        safety_refusal=False,
        created_at=created_at,
    )
    return asdict(proposal)


def unsafe_request_reason(lowered_text: str) -> str:
    if any(
        phrase in lowered_text
        for phrase in (
            "do not fire",
            "don't fire",
            "should not fire",
            "shouldn't fire",
            "do not accuse",
            "don't accuse",
            "not evidence of misconduct",
        )
    ):
        return ""
    matched = [term for term in PERSONNEL_TERMS if term in lowered_text]
    if not matched:
        return ""
    return (
        "ShiftNotes refused this request because it asks for or implies a "
        "personnel accusation, disciplinary action, termination decision, or "
        "distribution of an unverified allegation. Inspect source reports and "
        "use the established human review process instead."
    )


def contains_positive_language(source: dict[str, Any]) -> bool:
    text = " ".join(
        (
            str(source.get("team_members_who_did_well", "")),
            str(source.get("guest_issues_for_the_day", "")),
            str(source.get("operational_notes", "")),
        )
    ).lower()
    return any(
        term in text
        for term in (
            "helped",
            "positive",
            "recognized",
            "compliment",
            "kept the line moving",
            "supported",
        )
    )


def claim_sentence(label: str, count: int, kiosk: str) -> str:
    display_label = label[:1].upper() + label[1:]
    if count == 0:
        return f"No remaining reports support {label} at {kiosk}."
    report_word = "report" if count == 1 else "reports"
    return f"{display_label} appeared in {count} {report_word} at {kiosk}."


def save_claim_catalog(path: Path, claims: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(claims, indent=2), encoding="utf-8")


def load_correction_history(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def apply_correction_history(
    claims: list[dict[str, Any]],
    history: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    latest_confirmed: dict[str, dict[str, Any]] = {}
    for record in history:
        if record.get("status") == "confirmed":
            latest_confirmed[str(record["claim_id"])] = record

    resolved = []
    for claim in claims:
        correction = latest_confirmed.get(str(claim["claim_id"]))
        if not correction:
            resolved.append(dict(claim))
            continue
        resolved.append(
            {
                **claim,
                "claim_text": correction["proposed_claim_text"],
                "source_submission_ids": correction["proposed_source_ids"],
                "source_count": len(correction["proposed_source_ids"]),
                "status": "corrected",
                "correction_id": correction["proposal_id"],
            }
        )
    return resolved


def append_correction_history(
    path: Path,
    proposal: dict[str, Any],
    decision: str,
    actor: str = "Ted",
) -> dict[str, Any]:
    history = load_correction_history(path)
    record = {
        **proposal,
        "decision": decision,
        "actor": actor,
        "decided_at": datetime.now(timezone.utc).isoformat(),
        "status": "confirmed" if decision == "confirm" else "cancelled",
    }
    history.append(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(history, indent=2), encoding="utf-8")
    return record


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
