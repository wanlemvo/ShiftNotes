from collections import Counter

from scripts.generate_final_mock_dataset import (
    DUPLICATE_SOURCE_IDS,
    MISSING_SLOTS,
    PROFILES,
    build_dataset,
)


def test_final_dataset_has_expected_schedule_and_anomaly_counts():
    dataset = build_dataset()
    summary = dataset["validation_summary"]

    assert summary["expected_schedule_rows"] == 288
    assert summary["scheduled_status_counts"] == {
        "malformed": 3,
        "missing": 18,
        "valid": 267,
    }
    assert summary["payload_submission_count"] == 273
    assert summary["duplicate_submission_count"] == 3
    assert summary["normalized_status_counts"] == {
        "needs_review": 3,
        "valid": 270,
    }


def test_schedule_tracks_missing_reports_by_exact_kiosk_and_date():
    dataset = build_dataset()
    missing_rows = {
        (row["kiosk"], row["date"])
        for row in dataset["schedule"]
        if row["status"] == "missing"
    }
    expected_counts = Counter(row["kiosk"] for row in dataset["schedule"])

    assert missing_rows == MISSING_SLOTS
    assert expected_counts == Counter({profile.name: 48 for profile in PROFILES})


def test_duplicate_submissions_map_to_identical_original_answers():
    dataset = build_dataset()
    submissions = {
        submission["id"]: submission
        for submission in dataset["api_response"]["content"]
    }
    duplicates = dataset["ground_truth"]["duplicates"]

    assert {item["original_submission_id"] for item in duplicates} == set(
        DUPLICATE_SOURCE_IDS
    )
    for item in duplicates:
        duplicate = submissions[item["duplicate_submission_id"]]
        original = submissions[item["original_submission_id"]]
        assert duplicate["answers"] == original["answers"]


def test_malformed_submissions_are_flagged_for_review():
    dataset = build_dataset()
    malformed_reports = [
        report
        for report in dataset["normalized"]
        if report["parse_status"] == "needs_review"
    ]
    errors = {
        error
        for report in malformed_reports
        for error in report["validation_errors"]
    }

    assert len(malformed_reports) == 3
    assert errors == {
        "missing lead_name",
        "missing food_quantity_rating",
        "missing number_of_unclaimed_lunches",
    }


def test_ground_truth_contains_expected_benchmark_patterns():
    dataset = build_dataset()
    events = dataset["ground_truth"]["events"]

    assert events["food_shortage:kung_pao_chicken"]["expected_count"] >= 15
    assert events["waste:high_unclaimed_lunches"]["expected_count"] >= 40
    assert events["guest_theme:dietary_or_allergy_question"]["expected_count"] >= 20
    assert events["operational_issue:equipment_failure"]["expected_count"] >= 10
    assert events["recognition:maya_chen"]["expected_count"] >= 20
    assert events["inventory:inconsistent_prep"]["expected_count"] >= 15
    assert events["cross_kiosk:register_disruption_week_7"]["expected_count"] == 6


def test_ground_truth_labels_are_not_exposed_in_jotform_payload():
    dataset = build_dataset()
    payload_text = str(dataset["api_response"]).lower()

    assert "food_shortage:kung_pao_chicken" not in payload_text
    assert "recognition:maya_chen" not in payload_text
    assert "cross_kiosk:register_disruption_week_7" not in payload_text


def test_sensitive_personnel_example_is_present_but_not_a_conclusion():
    dataset = build_dataset()
    sensitive = dataset["ground_truth"]["events"][
        "sensitive_personnel:ambiguous_comment"
    ]
    source_id = sensitive["source_records"][0]["source_submission_id"]
    report = next(
        report
        for report in dataset["normalized"]
        if report["source_submission_id"] == source_id
    )

    assert sensitive["expected_count"] == 1
    assert "does not establish misconduct" in report["operational_notes"]
