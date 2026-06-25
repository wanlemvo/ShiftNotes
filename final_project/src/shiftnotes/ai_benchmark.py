from __future__ import annotations

from typing import Any, Callable

from shiftnotes.baseline import percentage


GROUND_TRUTH_TO_AI = {
    "food_shortage:kung_pao_chicken": "food_shortage",
    "waste:high_unclaimed_lunches": "high_waste_or_overproduction",
    "guest_theme:dietary_or_allergy_question": "dietary_or_allergy_question",
    "operational_issue:equipment_failure": "equipment_failure",
    "recognition:maya_chen": "employee_recognition",
    "inventory:inconsistent_prep": "inventory_inconsistency",
    "cross_kiosk:register_disruption_week_7": "register_disruption",
    "cross_kiosk:portion_complaints_weeks_9_10": "portion_complaint",
    "guest_request:beverage_variety": "beverage_request",
    "sensitive_personnel:ambiguous_comment": "sensitive_personnel_note",
}

SignalFilter = Callable[[dict[str, Any], str], bool]


def _all_signals(signal: dict[str, Any], source_id: str) -> bool:
    return True


def _maya_chen_only(signal: dict[str, Any], source_id: str) -> bool:
    return "maya chen" in str(signal.get("subject", "")).lower()


def _source_ids_only(allowed: set[str]) -> SignalFilter:
    return lambda signal, source_id: source_id in allowed


def benchmark_filter(
    truth_category: str,
    expected_source_ids: set[str],
) -> SignalFilter:
    if truth_category == "recognition:maya_chen":
        return _maya_chen_only
    if truth_category in {
        "cross_kiosk:register_disruption_week_7",
        "cross_kiosk:portion_complaints_weeks_9_10",
        "guest_request:beverage_variety",
    }:
        return _source_ids_only(expected_source_ids)
    return _all_signals


def benchmark_semantic_extractions(
    extractions: list[dict[str, Any]],
    ground_truth: dict[str, Any],
    analyzable_source_ids: set[str],
) -> dict[str, Any]:
    signals_by_category: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    for result in extractions:
        source_id = str(result["source_submission_id"])
        for signal in result["signals"]:
            signals_by_category.setdefault(signal["category"], []).append(
                (source_id, signal)
            )

    categories: dict[str, dict[str, Any]] = {}
    total_tp = total_fp = total_fn = 0
    for truth_category, ai_category in GROUND_TRUTH_TO_AI.items():
        truth = ground_truth["events"].get(truth_category, {"source_records": []})
        all_expected = {
            str(record["source_submission_id"])
            for record in truth["source_records"]
        }
        expected = all_expected & analyzable_source_ids
        unavailable = all_expected - analyzable_source_ids
        filter_signal = benchmark_filter(truth_category, all_expected)
        all_category_detections = signals_by_category.get(ai_category, [])
        detected = {
            source_id
            for source_id, signal in all_category_detections
            if source_id in analyzable_source_ids
            and filter_signal(signal, source_id)
        }
        out_of_scope = {
            source_id
            for source_id, signal in all_category_detections
            if source_id in analyzable_source_ids
            and not filter_signal(signal, source_id)
        }
        true_positive = expected & detected
        false_positive = detected - expected
        missed = expected - detected
        total_tp += len(true_positive)
        total_fp += len(false_positive)
        total_fn += len(missed)
        categories[truth_category] = {
            "ai_category": ai_category,
            "true_positive_count": len(true_positive),
            "false_positive_count": len(false_positive),
            "missed_count": len(missed),
            "unavailable_due_data_quality_count": len(unavailable),
            "precision": percentage(len(true_positive), len(detected)),
            "recall": percentage(len(true_positive), len(expected)),
            "true_positive_source_ids": sorted(true_positive),
            "false_positive_source_ids": sorted(false_positive),
            "missed_source_ids": sorted(missed),
            "unavailable_source_ids": sorted(unavailable),
            "valid_but_out_of_scope_detection_count": len(out_of_scope),
            "valid_but_out_of_scope_source_ids": sorted(out_of_scope),
        }

    return {
        "categories": categories,
        "summary": {
            "true_positive_count": total_tp,
            "false_positive_count": total_fp,
            "missed_count": total_fn,
            "micro_precision": percentage(total_tp, total_tp + total_fp),
            "micro_recall": percentage(total_tp, total_tp + total_fn),
            "categories_scored": len(categories),
        },
    }
