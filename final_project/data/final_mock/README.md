# ShiftNotes Final Mock Dataset

This folder contains the reproducible 12-week synthetic dataset used for final
prototype development and benchmark evaluation.

## Files

| File | Purpose |
| --- | --- |
| `DATASET_DESIGN.md` | Explains scope, reasoning, planted patterns, privacy, and limitations. |
| `jotform_submissions.json` | JotForm-shaped API response used as system input. |
| `expected_reporting_schedule.csv` | All expected kiosk/date combinations and their status. |
| `normalized_reports.json` | Reports after the production normalizer runs. |
| `normalized_reports.csv` | Human-readable flattened version of normalized reports. |
| `ground_truth.json` | Hidden expected patterns and source IDs for benchmarking. |
| `validation_summary.json` | Counts and structural validation results. |
| `GENERATION_LOG.md` | Reproduction command and generation summary. |
| `baseline_analysis.json` | Complete deterministic cleaning and analysis output. |
| `reporting_completeness.json` | Missing, malformed, duplicate, and completeness details. |
| `weekly_summaries.json` | Twelve schedule-aware weekly summaries. |
| `monthly_summaries.json` | Three monthly summaries. |
| `benchmark_results.json` | Ground-truth precision, recall, and aggregate checks. |
| `baseline_briefing.md` | Human-readable baseline operations briefing. |

## Scope

```text
12 weeks
6 kiosks
4 expected reporting days per week
288 expected kiosk/date reports
267 valid scheduled submissions
18 missing reports
3 malformed submissions
3 duplicate extras
273 JotForm payload submissions
```

Missing reports must be detected by comparing submissions with
`expected_reporting_schedule.csv`. They should not be inferred by treating every
calendar day as an expected reporting day.

## Regenerate

From the repository root:

```bash
python scripts/generate_final_mock_dataset.py
```

The fixed seed makes repeated generation deterministic.

## Validate

```bash
python -m pytest tests/test_final_mock_dataset.py
```

Ground-truth labels are intentionally excluded from the JotForm payload.

## Run Baseline Analysis

```bash
python final_project/src/shiftnotes/cli.py baseline
```

The baseline:

- removes duplicate submissions by content fingerprint;
- excludes malformed reports from operational metrics;
- detects missing reports against the expected kiosk/date schedule;
- generates weekly and monthly summaries;
- calculates waste and quantity findings;
- compares source-level detections with ground truth.

This controlled baseline is intentionally deterministic. Its strong result on
planted synthetic wording is a reference point for later AI-assisted analysis,
not evidence that simple rules will generalize to every real report.
