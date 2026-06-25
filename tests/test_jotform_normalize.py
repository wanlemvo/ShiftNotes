import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "final_project" / "src"))

from shiftnotes.normalize import normalize_submissions
from shiftnotes.analysis import analyze_reports


def test_normalize_jotform_submission_to_shift_report():
    response = {
        "content": [
            {
                "id": "submission-001",
                "created_at": "2026-06-16 12:00:00",
                "answers": {
                    "1": {
                        "text": "Date",
                        "answer": {
                            "month": "06",
                            "day": "16",
                            "year": "2026",
                            "datetime": "2026-06-16 00:00:00",
                        },
                    },
                    "2": {"text": "Kiosk / Station", "answer": "Bowls & Buns"},
                    "3": {"text": "Lead Name", "answer": "Isaac"},
                    "4": {"text": "Food Quality Rating", "answer": "4"},
                    "5": {"text": "Food Quantity Rating", "answer": "5"},
                    "6": {
                        "text": "Food Concerns or Outages",
                        "answer": "Kung Pao chicken held well through lunch.",
                    },
                    "7": {
                        "text": "Team Members Who Did Well",
                        "answer": "Dom kept the line moving.",
                    },
                    "8": {
                        "text": "Guest Issues for the Day",
                        "answer": "Guests asked when poke would return.",
                    },
                    "9": {"text": "Operational Notes", "answer": "No issues."},
                    "10": {"text": "Number of Unclaimed Lunches", "answer": "6"},
                },
            }
        ]
    }

    reports = normalize_submissions(response)

    assert len(reports) == 1
    report = reports[0]
    assert report["source_submission_id"] == "submission-001"
    assert report["date"] == "2026-06-16"
    assert report["kiosk"] == "Bowls & Buns"
    assert report["food_quality_rating"] == 4
    assert report["food_quantity_rating"] == 5
    assert report["number_of_unclaimed_lunches"] == 6
    assert report["parse_status"] == "valid"
    assert report["validation_errors"] == []


def test_missing_required_fields_are_flagged_for_review():
    response = {
        "content": [
            {
                "id": "submission-002",
                "answers": {
                    "1": {"text": "Date", "answer": "06-16-2026"},
                    "2": {"text": "Lead Name", "answer": "Isaac"},
                },
            }
        ]
    }

    reports = normalize_submissions(response)
    report = reports[0]

    assert report["parse_status"] == "needs_review"
    assert "missing kiosk" in report["validation_errors"]
    assert "missing food_quality_rating" in report["validation_errors"]


def test_weekly_analysis_generates_source_backed_claims():
    reports = [
        {
            "source_submission_id": "submission-001",
            "date": "2026-06-16",
            "kiosk": "Bowls & Buns",
            "food_quality_rating": 4,
            "food_quantity_rating": 3,
            "food_concerns_or_outages": "Kung Pao chicken ran low and mac salad needed attention.",
            "team_members_who_did_well": "Dom helped restock quickly.",
            "guest_issues_for_the_day": "Guests asked for larger chicken portions.",
            "operational_notes": "Recommend tracking chicken demand.",
            "number_of_unclaimed_lunches": 4,
            "parse_status": "valid",
            "validation_errors": [],
        },
        {
            "source_submission_id": "submission-002",
            "date": "2026-06-17",
            "kiosk": "Bowls & Buns",
            "food_quality_rating": 5,
            "food_quantity_rating": 4,
            "food_concerns_or_outages": "Kung Pao chicken had great flavor.",
            "team_members_who_did_well": "Iris kept the station clean.",
            "guest_issues_for_the_day": "One guest asked when poke would return.",
            "operational_notes": "No major issues.",
            "number_of_unclaimed_lunches": 2,
            "parse_status": "valid",
            "validation_errors": [],
        },
    ]

    analysis = analyze_reports(reports, expected_kiosks=["Bowls & Buns"])

    assert analysis["summary"]["total_reports"] == 2
    assert analysis["summary"]["average_food_quality_rating"] == 4.5
    assert analysis["summary"]["total_unclaimed_lunches"] == 6
    assert any("Kung Pao Chicken was mentioned in 2 reports." == claim["claim"] for claim in analysis["claims"])
    claim = next(
        claim for claim in analysis["claims"] if claim["claim"] == "Kung Pao Chicken was mentioned in 2 reports."
    )
    assert claim["source_submission_ids"] == ["submission-001", "submission-002"]
