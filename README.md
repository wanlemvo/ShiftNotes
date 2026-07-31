# ShiftNotes

ShiftNotes is an email-first operational intelligence prototype for kiosk shift
reports. It turns JotForm-style submissions into source-backed weekly and
monthly briefings so an operations manager can see trends without manually
reading every individual report.

The primary interface is email. The Streamlit app is a supporting inspection
workspace for reviewing sources, challenging claims, and checking correction
history.

Public demo: https://shiftnotes.streamlit.app

## Project Ownership

ShiftNotes was designed from a workplace problem I observed directly: shift-note
reports already existed, but the useful operational patterns were buried across
individual submissions. I designed the product concept, email-first workflow,
source-backed claim model, human review path, and adoption strategy. AI tools
were used as an implementation partner to help turn that design into code,
tests, documentation, and refinements.

The core product decision was not to replace the manager's workflow with a new
dashboard habit. Instead, ShiftNotes adds one high-value briefing email and
keeps the dashboard available only when a claim needs inspection or correction.

## Project Map

```text
demo/                         runnable ShiftNotes prototype
demo/src/shiftnotes/           core ingestion, analysis, AI, email, and workflow code
demo/data/final_mock/          synthetic JotForm-shaped demo dataset and outputs
docs/                          product documentation and technical writeups
docs/submissions/              class submission artifacts and report drafts
docs/archive/                  older planning, team prototype, and class-history material
tests/                         automated tests for the active prototype
scripts/                       reproducible data-generation scripts
```

Older class and team artifacts are intentionally preserved under `docs/archive/`
so the root of the repo stays focused on the current prototype.

## Workflow

```text
JotForm-style shift reports
-> normalized operational records
-> deterministic metrics and semantic signal extraction
-> source-backed weekly/monthly briefings
-> Gmail delivery
-> optional Streamlit source inspection and claim correction
```

The adoption decision is deliberate: ShiftNotes improves the manager's existing
email workflow instead of requiring a new daily dashboard habit.

## Quick Demo

Run the inspection workspace locally:

```bash
python -m pip install -e .
python -m streamlit run demo/app.py
```

Or open the hosted synthetic-data demo:

```text
https://shiftnotes.streamlit.app
```

Useful local preview files:

```text
demo/data/final_mock/email_previews/weekly/week_01.html
demo/data/final_mock/email_previews/monthly/2026-03.html
```

## Setup

Copy the environment template:

```bash
copy demo\.env.example demo\.env
```

Fill in the values you need:

```env
JOTFORM_API_KEY=your_api_key_here
JOTFORM_FORM_ID=your_form_id_here
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
GMAIL_CLIENT_SECRET_PATH=demo/google_credentials.json
GMAIL_TOKEN_PATH=demo/.gmail_token.json
GMAIL_DEFAULT_RECIPIENT=manager@example.com
```

Do not commit `.env`, Google credentials, or Gmail tokens.

## Common Commands

```bash
python -m pip install -e .
python -m pytest -q
python scripts/generate_final_mock_dataset.py
python demo/src/shiftnotes/cli.py baseline
python demo/src/shiftnotes/cli.py briefings
python demo/src/shiftnotes/cli.py product-assets
python demo/src/shiftnotes/cli.py gmail-preview --type weekly --period week-01
```

To send a real Gmail briefing after OAuth setup:

```bash
python demo/src/shiftnotes/cli.py gmail-send --type weekly --period week-01 --confirm-send
```

## What Is Implemented

- JotForm API client and JotForm-style data normalization.
- Required-field validation and malformed report flagging.
- Missing report detection by kiosk and expected date.
- Duplicate handling.
- Three-month synthetic dataset with planted ground-truth patterns.
- Weekly and monthly briefing generation.
- HTML and plain-text email previews.
- Gmail API delivery using the narrow `gmail.send` scope.
- Groq semantic extraction for free-text operational signals.
- Strict source evidence validation for AI-generated signals.
- Retry and deterministic fallback behavior for malformed or failed AI calls.
- Urgent, important, and monitor/recognize briefing sections.
- Source-backed claim catalog.
- Streamlit source inspection workspace.
- Human-in-the-loop claim challenge and correction confirmation.
- Responsible AI guardrails for sensitive personnel notes.
- Automated tests for the active prototype.

## Documentation

- `docs/DEMO_GUIDE.md` - how to present the prototype.
- `docs/PROTOTYPE_STATUS.md` - implemented scope, limits, and next steps.
- `docs/PRODUCT_WORKFLOW.md` - email-first workflow and HITL behavior.
- `docs/ARCHITECTURE_OVERVIEW.md` - system architecture and design rationale.
- `docs/MODEL_SELECTION_AND_BENCHMARK.md` - model rationale and benchmark evidence.
- `docs/BRIEFING_DESIGN.md` - briefing format and operational guardrails.
- `docs/DESIGN_AND_ENGINEERING_NOTES.md` - concise design, validation, and scale notes.

## Known Limitations

- The hosted Streamlit app uses synthetic data and is not authenticated.
- Gmail delivery works, but each installation needs one-time Google OAuth setup.
- Scheduling policy is documented, but no production scheduler is deployed yet.
- Local JSON and SQLite are used for the prototype instead of a production database.
- Full production rollout would need authentication, tenant isolation, hosted jobs,
  monitoring, secret management, and stronger operational controls.
