# ShiftNotes Prototype Pack

This folder contains a ready-to-run prototype dataset and notebook.

## Files

- `mock_shift_notes.csv`: 100 synthetic shift-note reports for 6 kiosks over ~4 weeks.
- `ground_truth_targets.csv`: expected high-level trends used to validate extraction.
- `ShiftNotes_Prototype.ipynb`: notebook pipeline for cleaning, extraction, trend analysis, and weekly summary generation.

## Quick Start

1. Open `ShiftNotes_Prototype.ipynb`.
2. Run all cells in order.
3. Review the `checks` table to confirm extracted trends match ground truth.
4. Use the generated weekly summaries as your prototype briefing output.

## Prototype Goal

Demonstrate that freeform shift reports can be transformed into actionable operational intelligence with minimal manual review.
