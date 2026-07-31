# ShiftNotes Prototype Pack

This folder contains the dataset, signal classifier, and notebook for the ShiftNotes prototype pipeline.

## Files

- `mock_shift_notes.csv` — 100 synthetic shift reports across 6 kiosks over 4 weeks
- `ground_truth_targets.csv` — 7 planted trends used to validate the extraction pipeline
- `signal_classifier.py` — hybrid signal detector: regex fast-path + HuggingFace zero-shot fallback
- `ShiftNotes_Prototype.ipynb` — end-to-end pipeline: load → clean → classify → aggregate → validate → weekly briefings

## Dependencies

```
pip install pandas transformers torch
```

The HuggingFace model (`cross-encoder/nli-MiniLM2-L6-H768`, ~330 MB) downloads automatically on first run.

## Quick Start

1. Install dependencies above.
2. Open `ShiftNotes_Prototype.ipynb`.
3. Run all cells in order.
4. Review the `checks` table — all 7 rows should show `PASS`.
5. Read the generated weekly briefings at the bottom of the notebook.

## How Signal Detection Works

Each shift note is classified using a two-stage hybrid approach:

```
Shift Note Text
      ↓
Regex Fast-Path
  → Match found  →  Signal confirmed (True)
  → No match     →  Send to HuggingFace zero-shot
                          ↓
                   Score ≥ per-signal threshold  →  Signal confirmed (True)
                   Score < threshold             →  Signal absent (False)
```

Regex handles clear, explicit language (fast, free). HuggingFace fills in paraphrased or ambiguous cases without requiring an API key.

## Signals Detected

| Signal | What it captures |
|---|---|
| `chicken_shortage` | Chicken running low or out during service |
| `poke_request` | Guests asking for poke or missing menu items |
| `ops_issue` | Equipment failures, late deliveries, bottlenecks |
| `team_recognition` | Explicit employee shoutouts and standout contributions |

## Ground Truth Targets

| Metric | Expected |
|---|---|
| total_reports | 100 |
| poke_request_mentions | 18 |
| chicken_shortage_mentions | 12 |
| highest_waste_kiosk | Kiosk B |
| high_recognition_kiosk | Kiosk E |
| ops_friction_kiosk | Kiosk D |
| inventory_inconsistency_kiosk | Kiosk F |

## Prototype Goal

Demonstrate that freeform operational shift reports can be automatically transformed into structured signals and actionable intelligence — with no manual review required.
