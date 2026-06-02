"""
signal_classifier.py
ShiftNotes — Hybrid Signal Detection
Regex handles clear-cut cases (fast, free).
HuggingFace zero-shot fills in the gaps (flexible, no API cost).
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# 1. CONFIG
# ──────────────────────────────────────────────

# Per-signal HF confidence thresholds.
# Higher = stricter. Tune these when HF over-fires on a signal.
HF_THRESHOLDS: dict[str, float] = {
    "chicken_shortage": 0.70,  # "no food concerns" scores ~0.55 — keep above that
    "poke_request":     0.50,  # clean signal, default threshold is fine
    "ops_issue":        0.70,  # avoid vague operational language false positives
    "team_recognition": 0.95,  # generic praise scores 0.75–0.97 — only catch explicit outliers
}

# Signals and their HF candidate labels
SIGNAL_LABELS: dict[str, str] = {
    "chicken_shortage": "chicken or food running out or shortage",
    "poke_request":     "guest requesting poke bowl or missing menu item",
    "ops_issue":        "equipment failure or operational problem or bottleneck",
    "team_recognition": "employee praised or team member recognized",
}

# Regex fast-path patterns per signal (lowercased match)
REGEX_PATTERNS: dict[str, list[str]] = {
    "chicken_shortage": [
        r"chicken ran low",
        r"ran out of chicken",
        r"short on chicken",
        r"chicken supply ran short",
        r"out of chicken",
    ],
    "poke_request": [
        r"\bpoke\b",
        r"bring back poke",
        r"asked for poke",
    ],
    "ops_issue": [
        r"register froze",
        r"supply delivery arrived late",
        r"temperature drift",
        r"\bbottleneck\b",
        r"equipment (issue|problem|malfunction)",
    ],
    "team_recognition": [
        r"\bshoutout\b",
        r"dom b\.",
        r"kept (the )?line (flow |moving|smooth)",
        r"great teamwork",
    ],
}


# ──────────────────────────────────────────────
# 2. LAZY HF LOADER
# ──────────────────────────────────────────────

_hf_pipeline = None  # loaded once on first use


def _get_hf_pipeline():
    """Load HuggingFace zero-shot pipeline (lazy, runs once)."""
    global _hf_pipeline
    if _hf_pipeline is None:
        try:
            from transformers import pipeline as hf_pipeline
            logger.info("Loading HuggingFace model (first run may take a moment)...")
            _hf_pipeline = hf_pipeline(
                "zero-shot-classification",
                model="cross-encoder/nli-MiniLM2-L6-H768",  # fast & lightweight
            )
            logger.info("HuggingFace model ready.")
        except ImportError:
            logger.error("transformers not installed. Run: pip install transformers")
            raise
    return _hf_pipeline


# ──────────────────────────────────────────────
# 3. CORE CLASSIFIERS
# ──────────────────────────────────────────────

def _regex_classify(text: str) -> dict[str, Optional[bool]]:
    """
    Fast-path: returns True if regex fires, None if uncertain (not False).
    None means 'no opinion yet — let HF decide'.
    """
    results: dict[str, Optional[bool]] = {}
    lowered = text.lower()
    for signal, patterns in REGEX_PATTERNS.items():
        hit = any(re.search(p, lowered) for p in patterns)
        results[signal] = True if hit else None  # None = undecided
    return results


def _hf_classify(text: str, signals_needed: list[str]) -> dict[str, bool]:
    """
    HF zero-shot for signals that Regex couldn't confirm.
    Only runs on undecided signals to save compute.
    """
    if not signals_needed:
        return {}

    clf = _get_hf_pipeline()
    candidate_labels = [SIGNAL_LABELS[s] for s in signals_needed]

    result = clf(text, candidate_labels=candidate_labels, multi_label=True)
    score_map = dict(zip(result["labels"], result["scores"]))

    return {
        signal: score_map[SIGNAL_LABELS[signal]] >= HF_THRESHOLDS[signal]
        for signal in signals_needed
    }


# ──────────────────────────────────────────────
# 4. HYBRID ENTRY POINT
# ──────────────────────────────────────────────

@dataclass
class SignalResult:
    chicken_shortage: bool = False
    poke_request:     bool = False
    ops_issue:        bool = False
    team_recognition: bool = False
    # audit trail
    regex_hits:  list[str] = field(default_factory=list)
    hf_hits:     list[str] = field(default_factory=list)


def classify(text: str) -> SignalResult:
    """
    Hybrid classifier for a single shift note text.

    Flow:
        1. Regex fast-path  → marks confirmed signals as True
        2. HF zero-shot     → resolves undecided signals
        3. Merge results    → return SignalResult

    Args:
        text: raw shift note string (any column or full_text)

    Returns:
        SignalResult dataclass with boolean flags + audit trail
    """
    if not isinstance(text, str) or not text.strip():
        return SignalResult()

    regex_results = _regex_classify(text)

    # Signals confirmed by regex
    confirmed   = {s for s, v in regex_results.items() if v is True}
    # Signals still undecided → send to HF
    undecided   = [s for s, v in regex_results.items() if v is None]

    hf_results  = _hf_classify(text, undecided)
    hf_positive = {s for s, v in hf_results.items() if v is True}

    # Merge
    all_true = confirmed | hf_positive

    return SignalResult(
        chicken_shortage = "chicken_shortage" in all_true,
        poke_request     = "poke_request"     in all_true,
        ops_issue        = "ops_issue"        in all_true,
        team_recognition = "team_recognition" in all_true,
        regex_hits       = sorted(confirmed),
        hf_hits          = sorted(hf_positive),
    )


# ──────────────────────────────────────────────
# 5. DATAFRAME HELPER
# ──────────────────────────────────────────────

def apply_to_dataframe(df: pd.DataFrame, text_col: str = "full_text") -> pd.DataFrame:
    """
    Run hybrid classifier over every row in a DataFrame.

    Adds columns:
        chicken_shortage_mention, poke_request_mention,
        ops_issue_mention, team_recognition_mention,
        regex_hits, hf_hits

    Args:
        df:       DataFrame containing shift notes
        text_col: column with the text to classify (default: 'full_text')

    Returns:
        df with new signal columns appended (original df unchanged)
    """
    if text_col not in df.columns:
        raise ValueError(f"Column '{text_col}' not found. Available: {list(df.columns)}")

    logger.info(f"Classifying {len(df)} rows from column '{text_col}'...")

    results = df[text_col].apply(classify)

    out = df.copy()
    out["chicken_shortage_mention"] = results.apply(lambda r: r.chicken_shortage)
    out["poke_request_mention"]     = results.apply(lambda r: r.poke_request)
    out["ops_issue_mention"]        = results.apply(lambda r: r.ops_issue)
    out["team_recognition_mention"] = results.apply(lambda r: r.team_recognition)
    out["regex_hits"]               = results.apply(lambda r: r.regex_hits)
    out["hf_hits"]                  = results.apply(lambda r: r.hf_hits)

    # Summary log
    for signal in ["chicken_shortage_mention", "poke_request_mention",
                   "ops_issue_mention", "team_recognition_mention"]:
        logger.info(f"  {signal}: {out[signal].sum()} hits")

    return out