from __future__ import annotations

import re
from typing import Any


AI_CATEGORY_LABELS = {
    "safety_concern": "safety concern requiring immediate review",
    "food_shortage": "food shortages",
    "high_waste_or_overproduction": "overproduction or elevated waste",
    "dietary_or_allergy_question": "dietary and allergy questions",
    "equipment_failure": "equipment-related disruptions",
    "employee_recognition": "employee recognition",
    "inventory_inconsistency": "inventory and prep inconsistencies",
    "register_disruption": "register disruptions",
    "portion_complaint": "portion-size concerns",
    "beverage_request": "beverage requests",
    "sensitive_personnel_note": "sensitive personnel note requiring careful review",
    "coaching_review": "potential coaching or training opportunity requiring review",
    "other_operational_issue": "other operational issues",
}

AI_CATEGORY_FOLLOW_UPS = {
    "safety_concern": "Inspect the source immediately and follow the applicable workplace safety process.",
    "food_shortage": "Compare prep levels with lunch-rush demand.",
    "high_waste_or_overproduction": "Review prep quantities and unclaimed-lunch patterns before adjusting production.",
    "dietary_or_allergy_question": "Confirm that dietary and allergen information is easy for staff and guests to access.",
    "equipment_failure": "Review recurring equipment incidents and document maintenance follow-up.",
    "employee_recognition": "Recognize repeated positive performance and identify practices worth reinforcing.",
    "inventory_inconsistency": "Review inventory handoffs and end-of-shift counts.",
    "register_disruption": "Confirm whether register interruptions require technical follow-up.",
    "portion_complaint": "Compare portion guidance across kiosks before changing service standards.",
    "beverage_request": "Track whether beverage requests continue before changing the offering.",
    "sensitive_personnel_note": "Inspect the original report; do not infer misconduct or take personnel action from this note alone.",
    "coaching_review": "Review the source privately and confirm whether supportive training or clarification is appropriate.",
    "other_operational_issue": "Inspect source reports and decide whether a recurring operational pattern needs follow-up.",
}

GROUP_BY_SUBJECT_CATEGORIES = {
    "food_shortage",
    "employee_recognition",
    "inventory_inconsistency",
    "sensitive_personnel_note",
    "coaching_review",
}


def semantic_events_from_extractions(
    extractions: list[dict[str, Any]],
    reports: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    lookup = {
        str(report.get("source_submission_id", "")): report
        for report in reports
    }
    events: dict[str, list[dict[str, Any]]] = {}
    for result in extractions:
        source_id = str(result.get("source_submission_id", ""))
        report = lookup.get(source_id)
        if not report:
            continue
        for signal in result.get("signals", []):
            category = str(signal.get("category", "other_operational_issue"))
            subject = clean_subject(str(signal.get("subject", "")))
            key = semantic_event_key(category, subject)
            events.setdefault(key, []).append(
                {
                    "source_submission_id": source_id,
                    "date": report.get("date", ""),
                    "kiosk": report.get("kiosk", ""),
                    "excerpt": signal.get("evidence_excerpt", ""),
                    "evidence_field": signal.get("evidence_field", ""),
                    "confidence": signal.get("confidence"),
                    "severity": signal.get("severity", ""),
                    "sensitive": (
                        bool(signal.get("sensitive"))
                        or category == "coaching_review"
                    ),
                    "semantic_category": category,
                    "subject": subject,
                    "label": semantic_label(category, subject),
                    "follow_up": AI_CATEGORY_FOLLOW_UPS.get(
                        category,
                        AI_CATEGORY_FOLLOW_UPS["other_operational_issue"],
                    ),
                    "source": "groq_semantic",
                    "semantic_provider": result.get("semantic_provider", "unknown"),
                }
            )
    return {
        key: sorted(records, key=lambda item: item["source_submission_id"])
        for key, records in sorted(events.items())
    }


def semantic_event_key(category: str, subject: str) -> str:
    grouping = grouped_subject(category, subject)
    return f"semantic:{category}:{slugify(grouping)}"


def semantic_label(category: str, subject: str) -> str:
    base = AI_CATEGORY_LABELS.get(category, category.replace("_", " "))
    grouping = grouped_subject(category, subject)
    if grouping != category:
        return f"{base}: {display_subject(category, grouping)}"
    return base


def grouped_subject(category: str, subject: str) -> str:
    if category not in GROUP_BY_SUBJECT_CATEGORIES:
        return category
    if subject and subject.lower() not in {"n/a", "none", "general", "guest", "guests"}:
        return subject
    return category


def clean_subject(value: str) -> str:
    cleaned = " ".join(value.split())
    return cleaned[:80]


def display_subject(category: str, subject: str) -> str:
    if category == "employee_recognition":
        return subject.title()
    if category == "food_shortage":
        return subject.replace("kung pao", "Kung Pao").replace("chicken", "chicken")
    return subject[:1].upper() + subject[1:]


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "general"
