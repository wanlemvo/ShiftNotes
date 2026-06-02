# ARCHITECTURE

# Purpose

This document describes the system components, data flow, and technical design of the ShiftNotes prototype.

---

# System Overview

ShiftNotes is a pipeline that transforms freeform operational shift reports into structured signals and actionable intelligence.

The prototype demonstrates this transformation end-to-end using a synthetic dataset, a hybrid signal classifier, and an automated briefing generator.

---

# High-Level Data Flow

```text
Shift Reports (CSV)
        ↓
Data Loading & Cleaning
        ↓
Signal Detection
  ├── Regex Fast-Path
  └── HuggingFace Zero-Shot Fallback
        ↓
Aggregation
  ├── By Kiosk
  └── By Week
        ↓
Ground Truth Validation
        ↓
Operational Briefings
```

---

# Components

## Data Layer

### mock_shift_notes.csv

Synthetic dataset representing 100 shift reports across 6 kiosks over 5 weeks.

Fields:

* report_id
* date
* week
* kiosk
* lead_name
* food_quality_rating
* food_quantity_rating
* food_concerns_or_outages
* team_members_who_did_well
* guest_issues_for_the_day
* operational_notes
* number_of_unclaimed_lunches

---

### ground_truth_targets.csv

Seven known patterns planted in the dataset used to validate pipeline output.

| Metric | Expected Value |
| --- | --- |
| total_reports | 100 |
| poke_request_mentions | 18 |
| chicken_shortage_mentions | 12 |
| highest_waste_kiosk | Kiosk B |
| high_recognition_kiosk | Kiosk E |
| ops_friction_kiosk | Kiosk D |
| inventory_inconsistency_kiosk | Kiosk F |

---

## Signal Classifier

### signal_classifier.py

Hybrid detection module responsible for identifying four operational signals from shift note text.

### Signals

| Signal | Description |
| --- | --- |
| chicken_shortage | Chicken or key protein running low or out during service |
| poke_request | Guests requesting poke or a missing menu item |
| ops_issue | Equipment failures, late deliveries, or operational bottlenecks |
| team_recognition | Explicit employee shoutouts or standout team contributions |

### Detection Strategy

Stage 1 — Regex Fast-Path

Each text input is scanned against a set of exact patterns per signal.

If a match is found, the signal is confirmed immediately.

Regex is fast, free, and deterministic.

---

Stage 2 — HuggingFace Zero-Shot Fallback

If regex finds no match, the text is sent to a zero-shot classification model.

Model: `cross-encoder/nli-MiniLM2-L6-H768`

Each signal has a dedicated confidence threshold. If the model score meets or exceeds the threshold, the signal is confirmed.

Per-Signal Thresholds:

| Signal | Threshold |
| --- | --- |
| chicken_shortage | 0.70 |
| poke_request | 0.50 |
| ops_issue | 0.70 |
| team_recognition | 0.95 |

Higher thresholds are used for signals where general language tends to produce false positives.

---

### Output

Each row is classified into a `SignalResult` dataclass containing:

* Four boolean signal flags
* `regex_hits` — list of signals confirmed by regex
* `hf_hits` — list of signals confirmed by HuggingFace

The audit trail allows inspection of how each signal was detected.

---

## Analysis Pipeline

### ShiftNotes_Prototype.ipynb

Eight-step Jupyter notebook that runs the full prototype pipeline.

| Step | Description |
| --- | --- |
| 1 | Imports |
| 2 | Load data |
| 3 | Data cleaning and full_text construction |
| 4 | Signal detection via signal_classifier.py |
| 5 | Kiosk-level aggregation |
| 6 | Weekly trend aggregation |
| 7 | Ground truth validation |
| 8 | Weekly operational briefing generation |

---

# Kiosk Profiles

Each kiosk in the dataset has a designed operational signature.

| Kiosk | Planted Pattern |
| --- | --- |
| Kiosk A | Recurring chicken shortages during lunch rush |
| Kiosk B | High food waste and overpreparation |
| Kiosk C | Recurring guest poke requests |
| Kiosk D | Operational friction — equipment, supply, and bottleneck issues |
| Kiosk E | High team performance and employee recognition |
| Kiosk F | Inconsistent inventory management and mid-shift corrections |

---

# Technology Stack

| Component | Technology |
| --- | --- |
| Data processing | Python, pandas |
| Signal detection | Regex, HuggingFace Transformers |
| Classification model | cross-encoder/nli-MiniLM2-L6-H768 |
| Notebook | Jupyter |
| Version control | Git, GitHub |

---

# Current Limitations

The prototype is intentionally scoped to validate the core concept.

* Signal detection relies on a small set of predefined patterns
* The HuggingFace model is downloaded on first run (~330 MB)
* The dataset is synthetic and does not reflect real operational variability
* Briefings are plain text and not yet formatted for email delivery
* No persistent storage or database layer exists in the prototype

---

# Future Architecture

Future versions of ShiftNotes may introduce the following components.

## Intake Layer

Automated ingestion from JotForm submissions via email or API.

---

## Storage Layer

Structured database for historical report storage and querying.

---

## Intelligence Layer

* LLM-based signal extraction replacing rule-based detection
* Retrieval-augmented generation for natural language querying
* Trend detection across extended historical windows

---

## Delivery Layer

* Formatted daily and weekly email briefings
* Operational dashboards
* Multi-location comparison views
