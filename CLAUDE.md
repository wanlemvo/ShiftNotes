# CLAUDE.md

## Project Context

ShiftNotes is an email-first operational intelligence prototype for workplace
shift reports.

The prototype goal is to prove that JotForm-style shift notes can be turned
into source-backed weekly and monthly management briefings. The dashboard is a
secondary inspection surface; the primary user experience is the briefing email
that Ted can read without manually reviewing every individual shift-note report.

## Active Prototype Scope

Implemented scope:

- normalize JotForm-style submissions into clean ShiftNotes records;
- validate malformed and duplicate submissions;
- detect missing kiosk/date reports from an expected reporting schedule;
- generate deterministic metrics for ratings, reporting completeness, and waste;
- use Groq semantic extraction for free-text operational signals;
- preserve source IDs and exact evidence excerpts for meaningful claims;
- generate weekly and monthly briefings in HTML and plain text;
- classify findings into immediate attention, important follow-up, and
  monitoring/recognition sections;
- send an explicitly confirmed briefing through Gmail after OAuth authorization;
- support source inspection and ordinary-English claim challenge flows;
- require human confirmation before saving a proposed correction;
- refuse or flag unsafe personnel-related requests;
- provide tests and reproducible synthetic data for grading.

Current implementation limits:

- production hosting and authentication;
- production scheduler deployment;
- live Ted account integration;
- autonomous personnel decisions;
- pure full-dataset Groq backfill without quota-aware batching.

## Development Guidance

- Keep the email briefing as the primary product surface.
- Treat Streamlit as the leadership dashboard and supporting evidence/review interface.
- Keep exact calculations deterministic in Python.
- Use the model only for semantic interpretation of free-text fields.
- Preserve source traceability for every important claim.
- Do not allow unsupported claims, invented sources, or hidden model fallback.
- Do not recommend discipline, termination, or personnel accusations.
- Document significant changes in `docs/CHANGELOG.md`; preserve the historical solo work log.
- Document provider support honestly: only JotForm ingestion is implemented.
- Dashboard counts use weekly claims once per category/source, after correction history.
- Keep the public dataset synthetic. Live fetch output is not automatically wired to the dashboard.

## Important Artifacts

- `demo/README.md`: setup, run steps, demo path, and limitations.
- `docs/README.md`: current documentation index.
- `docs/submissions/final_report/ShiftNotes_Technical_Report.md`: class report artifact.
- `docs/PRODUCT_WORKFLOW.md`: email-first product behavior.
- `docs/MODEL_SELECTION_AND_BENCHMARK.md`: model rationale and evidence.
- `docs/DASHBOARD_METRICS.md`: aggregation and interpretation contracts.
- `docs/INTEGRATIONS.md`: supported inputs and live-data boundaries.
- `demo/data/final_mock/`: reproducible final dataset and artifacts.
- `demo/data/final_mock/email_previews/`: demo-ready email outputs.
- `tests/`: automated validation suite.
- `docs/archive/class_docs/SOLO_WORK_LOG.md`: earlier independent development history.
- `docs/archive/class_docs/INDEPENDENT_BACKLOG.md`: historical backlog.
- `docs/CHANGELOG.md`: ongoing significant changes.

## Setup and Verification

Run `uv sync --locked`, `uv run pytest -q`, and
`uv run streamlit run streamlit_app.py` from the repository root.
The no-key demo uses bundled reports. Keep old team code and retired packaging
helpers in the archive. See `docs/PUBLICATION.md` before preparing a release.

## Human-in-the-Loop Requirement

ShiftNotes produces operational intelligence for human review. It does not take
operational action by itself.

The intended HITL pattern is post-delivery review:

```text
briefing email
-> Ted inspects a claim if needed
-> Ted challenges the claim in ordinary English
-> ShiftNotes proposes a correction
-> Ted confirms or cancels
-> confirmed correction is recorded for auditability
```

Corrections do not automatically change future classification rules. Any change
to future model/rule behavior requires a separate reviewed update.
