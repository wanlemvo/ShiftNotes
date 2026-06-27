# CLAUDE.md

## Project Context

ShiftNotes is an email-first operational intelligence prototype for workplace
shift reports.

The final project goal is to prove that JotForm-style shift notes can be turned
into source-backed weekly and monthly management briefings. The dashboard is a
secondary inspection surface; the primary user experience is the briefing email
that Ted can read without manually reviewing every individual shift-note report.

## Final Prototype Scope

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

Out of scope for this submission:

- production hosting and authentication;
- production scheduler deployment;
- live Ted account integration;
- autonomous personnel decisions;
- pure full-dataset Groq backfill without quota-aware batching.

## Development Guidance

- Keep the email briefing as the primary product surface.
- Treat Streamlit as inspection, evidence review, and demo support only.
- Keep exact calculations deterministic in Python.
- Use the model only for semantic interpretation of free-text fields.
- Preserve source traceability for every important claim.
- Do not allow unsupported claims, invented sources, or hidden model fallback.
- Do not recommend discipline, termination, or personnel accusations.
- Document significant changes in `SOLO_WORK_LOG.md`.

## Important Artifacts

- `final_project/README.md`: setup, run steps, demo path, and limitations.
- `final_project/TECHNICAL_REPORT.md`: final technical report content.
- `final_project/PRODUCT_WORKFLOW.md`: email-first product behavior.
- `final_project/MODEL_SELECTION_AND_BENCHMARK.md`: model rationale and evidence.
- `final_project/data/final_mock/`: reproducible final dataset and artifacts.
- `final_project/data/final_mock/email_previews/`: demo-ready email outputs.
- `tests/`: automated validation suite.
- `SOLO_WORK_LOG.md`: independent development history after the team checkpoint.
- `INDEPENDENT_BACKLOG.md`: backlog and deliverable traceability.

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
