import pytest
from shiftnotes_agent.tools.signal_classifier import (
    classify_report,
    _build_full_text,
    _regex_check
)

CHICKEN_REPORT = {
    "report_id": 1,
    "kiosk": "Kiosk A",
    "date": "2026-05-01",
    "food_concerns_or_outages": "Chicken ran low during the lunch rush.",
    "guest_issues_for_the_day": "No major issues.",
    "operational_notes": "All good.",
    "team_members_who_did_well": "Team stayed focused."
}

POKE_REPORT = {
    "report_id": 2,
    "kiosk": "Kiosk C",
    "date": "2026-05-01",
    "food_concerns_or_outages": "No concerns.",
    "guest_issues_for_the_day": "Multiple guests asked about poke.",
    "operational_notes": "Smooth shift.",
    "team_members_who_did_well": ""
}

CLEAN_REPORT = {
    "report_id": 3,
    "kiosk": "Kiosk B",
    "date": "2026-05-01",
    "food_concerns_or_outages": "Everything was fully stocked.",
    "guest_issues_for_the_day": "No complaints.",
    "operational_notes": "Normal shift.",
    "team_members_who_did_well": "Everyone did their job."
}

NAN_REPORT = {
    "report_id": 4,
    "kiosk": "Kiosk D",
    "date": "2026-05-01",
    "food_concerns_or_outages": float("nan"),
    "guest_issues_for_the_day": float("nan"),
    "operational_notes": "Normal shift.",
    "team_members_who_did_well": float("nan")
}

def test_build_full_text_combines_fields():
    text = _build_full_text(CHICKEN_REPORT)
    assert "chicken" in text
    assert "lunch rush" in text

def test_build_full_text_handles_nan():
    text = _build_full_text(NAN_REPORT)
    assert isinstance(text, str)
    assert "nan" not in text

def test_regex_detects_chicken_shortage():
    assert _regex_check("chicken ran low during the lunch rush", "chicken_shortage") is True

def test_regex_detects_poke_request():
    assert _regex_check("multiple guests asked about poke", "poke_request") is True

def test_regex_no_false_positive():
    assert _regex_check("everything was fully stocked today", "chicken_shortage") is False

def test_classify_report_chicken():
    result = classify_report(CHICKEN_REPORT)
    assert result["has_signal"] is True
    signal_names = [s["name"] for s in result["signals_found"]]
    assert "chicken_shortage" in signal_names

def test_classify_report_poke():
    result = classify_report(POKE_REPORT)
    assert result["has_signal"] is True
    signal_names = [s["name"] for s in result["signals_found"]]
    assert "poke_request" in signal_names

def test_classify_report_returns_correct_fields():
    result = classify_report(CHICKEN_REPORT)
    assert "report_id" in result
    assert "kiosk" in result
    assert "has_signal" in result
    assert "signals_found" in result

def test_classify_report_nan_does_not_crash():
    result = classify_report(NAN_REPORT)
    assert isinstance(result, dict)
    assert "has_signal" in result