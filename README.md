# ShiftNotes

ShiftNotes is an email-first operational intelligence prototype for
JotForm-style shift reports.

The final project demonstrates how recurring operational notes from multiple
kiosks can be transformed into source-backed weekly and monthly management
briefings. The dashboard is secondary. The primary user experience is a
briefing email that helps a manager understand trends without manually reading
every individual shift-note report.

## Final Project Location

The final independent implementation lives in:

```text
final_project/
```

Key artifacts:

- `final_project/README.md` - setup, run steps, demo path, and limitations.
- `final_project/TECHNICAL_REPORT.md` - final technical report sections.
- `final_project/PRODUCT_WORKFLOW.md` - email-first workflow and HITL behavior.
- `final_project/MODEL_SELECTION_AND_BENCHMARK.md` - model rationale and benchmark evidence.
- `final_project/data/final_mock/email_previews/` - demo-ready weekly/monthly email previews.
- `final_project/data/final_mock/` - synthetic dataset, claims, briefings, and benchmark artifacts.
- `tests/` - automated test suite.
- `SOLO_WORK_LOG.md` - independent work log after the Week 8 team checkpoint.

## Quick Demo

Open these files in a browser:

```text
final_project/data/final_mock/email_previews/weekly/week_01.html
final_project/data/final_mock/email_previews/monthly/2026-03.html
```

These previews show the core product flow:

```text
JotForm-style shift reports
-> cleaned operational records
-> source-backed trend analysis
-> weekly/monthly briefing email
-> optional source inspection and claim correction
```

## Run Locally

Install the project from the repository root:

```bash
python -m pip install -e .
```

Run tests:

```bash
python -m pytest -q
```

Generate final briefing artifacts:

```bash
python final_project/src/shiftnotes/cli.py briefings
python final_project/src/shiftnotes/cli.py product-assets
```

Run the optional inspection workspace:

```bash
python -m streamlit run final_project/app.py
```

## Setup for a Real JotForm Account

Copy the template:

```bash
copy final_project\.env.example final_project\.env
```

Fill in:

```env
JOTFORM_API_KEY=your_api_key_here
JOTFORM_FORM_ID=your_form_id_here
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

Do not commit `.env`.

## What Is Implemented

- JotForm-style normalization and validation.
- Missing report detection by expected kiosk/date.
- Duplicate and malformed report handling.
- Weekly and monthly briefing generation.
- HTML and plain-text email previews.
- Gmail API delivery with one-time OAuth authorization and explicit send confirmation.
- Urgent, important, and monitoring/recognition briefing sections.
- Groq semantic extraction with strict source evidence validation.
- Deterministic Python metrics for ratings, dates, waste, and completeness.
- Source-backed claim catalog.
- Optional Streamlit source inspection workspace.
- Public demo: https://shiftnotes.streamlit.app
- Human-in-the-loop claim challenge and correction confirmation.
- Responsible AI guardrails for personnel-sensitive notes.
- Benchmark artifacts and tests.

## Known Limitations

- Gmail delivery is implemented, but each installation must complete one-time
  Google OAuth setup before sending.
- The scheduler is documented but not deployed as a production job.
- The final demo uses synthetic JotForm-shaped data.
- A full Groq backfill hit on-demand quota limits and used deterministic fallback
  for unresolved batches.
- The public Streamlit demo is not authenticated and uses synthetic data only.
- Source links open hosted inspection views, not original JotForm records.

## Submission Notes

The complete final submission ZIP is generated under `dist/`, but `dist/` is not
tracked in Git. The repository itself contains the code, docs, tests, and demo
artifacts needed to reproduce the project on another machine.
