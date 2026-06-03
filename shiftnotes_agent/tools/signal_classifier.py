import re
from dataclasses import dataclass, field

# --- Signal patterns (regex fast-path) ---
SIGNAL_PATTERNS = {
    "chicken_shortage": [
        r"chicken.*(low|out|shortage|ran out|no more|limited)",
        r"(low|out of|no).*(chicken|protein)",
        r"chicken.*unavailable",
    ],
    "poke_request": [
        r"poke.*(request|asked|asking|want|wanted)",
        r"(guest|customer).*(ask|want|request).*poke",
        r"bring back poke",
        r"miss.*poke",
    ],
    "ops_issue": [
        r"(equipment|machine).*(fail|broke|down|issue|problem)",
        r"(late|delayed|missing).*(deliver|shipment|order|supply)",
        r"(bottleneck|backup|backed up|understaffed)",
        r"(oven|fryer|grill|register).*(not working|broken|down)",
    ],
    "team_recognition": [
        r"(great|excellent|outstanding|amazing).*(job|work|effort|shift)",
        r"(shoutout|kudos|recognition|props)\s+to",
        r"(went above|beyond|exceeded)",
        r"\b(did well|performed well|stepped up)\b",
    ],
}

# HuggingFace thresholds (used if regex finds nothing)
HF_THRESHOLDS = {
    "chicken_shortage": 0.70,
    "poke_request": 0.50,
    "ops_issue": 0.70,
    "team_recognition": 0.95,
}

# Lazy-load HuggingFace model — only downloads on first use
_hf_classifier = None


def _get_hf_classifier():
    global _hf_classifier
    if _hf_classifier is None:
        from transformers import pipeline
        _hf_classifier = pipeline(
            "zero-shot-classification",
            model="cross-encoder/nli-MiniLM2-L6-H768"
        )
    return _hf_classifier


def _build_full_text(report: dict) -> str:
    """Combine relevant report fields into one string for classification."""
    fields = [
        report.get("food_concerns_or_outages", ""),
        report.get("guest_issues_for_the_day", ""),
        report.get("operational_notes", ""),
        report.get("team_members_who_did_well", ""),
    ]
    # Convert to str to handle NaN values from pandas CSV reading
    return " ".join(str(f) for f in fields if f and str(f) != "nan").lower()


def _regex_check(text: str, signal: str) -> bool:
    """Stage 1 — fast regex check."""
    patterns = SIGNAL_PATTERNS.get(signal, [])
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _hf_check(text: str, signal: str) -> bool:
    """Stage 2 — HuggingFace zero-shot fallback."""
    try:
        classifier = _get_hf_classifier()
        result = classifier(text, candidate_labels=[signal])
        score = result["scores"][0]
        threshold = HF_THRESHOLDS.get(signal, 0.70)
        return score >= threshold
    except Exception:
        return False


def classify_report(report: dict) -> dict:
    """
    Classifies a single report for all four signals.
    Returns a dict with signal results and audit trail.
    """
    text = _build_full_text(report)
    signals_found = []

    for signal in SIGNAL_PATTERNS.keys():
        if _regex_check(text, signal):
            signals_found.append({"name": signal, "method": "regex"})
        elif _hf_check(text, signal):
            signals_found.append({"name": signal, "method": "huggingface"})

    return {
        "report_id": report.get("report_id"),
        "kiosk": report.get("kiosk"),
        "date": report.get("date"),
        "has_signal": len(signals_found) > 0,
        "signals_found": signals_found,
        "full_text": text,
    }