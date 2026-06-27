# Claude Technical Report Generation Context

## Assignment

Generate a polished approximately 10-page technical report for the ShiftNotes
final project. The submitted report must cover:

1. Problem statement and business justification.
2. Architecture decisions and framework rationale.
3. Model selection and benchmark evidence.
4. RAG or reasoning pipeline design.
5. Responsible AI analysis, risks, and mitigations.
6. Lessons learned and future work.

The report should also explain implementation and validation evidence, known
limitations, human-in-the-loop behavior, failure recovery, and reproducibility.

Target approximately 3,000-3,500 words before references. Use formal but
readable academic prose. Do not inflate the report with repeated background.

## Critical Accuracy Rules

- Do not invent test results, user quotes, benchmark values, costs, deployed
  services, or citations.
- Do not describe ShiftNotes as a finished production deployment.
- Gmail API delivery is implemented, but it requires one-time Desktop OAuth
  setup and explicit send confirmation.
- Automatic production scheduling is not deployed.
- JotForm API ingestion works, but the large final evaluation dataset is
  synthetic and shaped like normalized JotForm submissions.
- The Streamlit interface is local and unauthenticated.
- Source links currently point to local inspection views.
- Full-dataset Groq analysis reached an on-demand quota limit and used
  deterministic fallback for unresolved batches.
- Coaching-review signals are prompts for private human review, not disciplinary
  conclusions.
- ShiftNotes does not calculate confirmed dollar savings because cost, sales,
  and labor inputs are unavailable.
- Jayden Lawson's peer-review record was reconstructed retrospectively from
  previously received verbal feedback and is not a verbatim transcript.
- Ted Snow's feedback is documented by email, but his private contact details
  must not appear in the report.

## Project Summary

ShiftNotes is an email-first operational intelligence prototype for kiosk shift
reports. It transforms JotForm-style submissions into source-backed weekly and
monthly management briefings. The intended user is Ted, an operational manager
who currently receives many individual reports and must manually identify
patterns.

The central value proposition is not autonomous management. ShiftNotes reduces
manual reading, identifies repeated operational signals, detects missing
reports, preserves links to supporting evidence, and lets the manager challenge
claims.

## Business Problem

Individual shift reports contain:

- food quality and quantity ratings;
- food concerns and outages;
- employee recognition;
- guest issues;
- operational notes;
- unclaimed lunch counts.

The information is already partly structured because JotForm defines the
questions. The primary challenge is aggregating many reports across kiosks and
time. Repeated shortages, waste, guest requests, equipment failures, and
recognition can remain hidden when reports are reviewed individually.

The intended workflow is that Ted receives one weekly briefing and one monthly
briefing instead of having to read every report. He opens original sources only
when he wants to inspect or challenge a claim.

## Final Architecture

```text
JotForm API or reproducible JotForm-shaped fixtures
-> normalization and validation
-> duplicate and malformed-record handling
-> expected-schedule completeness checks
-> deterministic operational metrics
-> Groq semantic extraction with schema/evidence validation
-> deterministic retry fallback when needed
-> source-backed claim catalog
-> urgency and follow-up classification
-> weekly/monthly HTML and plain-text briefing
-> explicit Gmail API send
-> optional Streamlit source inspection
-> natural-language claim challenge
-> proposed correction
-> HITL confirmation
-> correction history
```

### Framework Responsibilities

- Python handles deterministic calculations and pipeline implementation.
- JotForm API provides structured production ingestion.
- Groq with `openai/gpt-oss-20b` interprets free-text operational notes.
- Pydantic enforces semantic-output schemas.
- LangGraph provides stateful orchestration, conditional routing, retries,
  fallback, persistence, and HITL interrupts.
- Streamlit provides a secondary local inspection and correction interface.
- Gmail API sends multipart HTML/plain-text briefings.
- Pytest verifies normalization, analysis, source traceability, LangGraph,
  responsible-AI refusal, email rendering, prioritization, and Gmail payloads.

## Data Design

The final synthetic dataset represents 12 weeks, six kiosks, and four expected
reports per kiosk per week:

```text
12 weeks x 6 kiosks x 4 reports = 288 expected reporting slots
```

The dataset includes intentionally missing reports, duplicates, malformed
records, ratings, waste counts, food shortages, guest feedback, dietary
questions, equipment and register disruptions, inventory inconsistencies,
employee recognition, ambiguous language, and quiet days.

The planted ground-truth file identifies deliberate patterns and source IDs.
This makes it possible to measure detection against known answers rather than
judging only whether summaries sound plausible.

## Deterministic and Semantic Boundary

Python computes:

- rating averages;
- report counts;
- missing kiosk/date reports;
- duplicates;
- malformed-record counts;
- waste and unclaimed-lunch totals;
- weekly/monthly grouping;
- source counts.

The model interprets only free-text fields:

- food concerns or outages;
- team members who did well;
- guest issues;
- operational notes.

Each semantic signal must contain a category, subject, severity, confidence,
source field, exact evidence excerpt, sensitivity flag, and rationale. Output is
rejected if it invents source IDs, omits requested IDs, duplicates IDs, violates
the schema, or cites an excerpt absent from the source field.

## Model Selection and Benchmark Evidence

Default provider/model:

```text
Groq / openai/gpt-oss-20b
```

Rationale:

- low prototype cost;
- adequate latency for scheduled batch analysis;
- structured-output support;
- replaceable provider boundary;
- deterministic fallback for reproducibility.

Recorded controlled validation:

### Six-report validation

- retries: 0;
- fallback batches: 0;
- source-level micro precision: 100%;
- source-level micro recall: 100%;
- estimated cost: $0.002070.

### Twenty-four-report validation

- cache hits: 21;
- retries: 1;
- fallback batches: 0;
- source-level micro precision: 100%;
- source-level micro recall: 100%;
- estimated cost: $0.001132.

### Full-dataset attempt

- reports processed: 270;
- retries: 278;
- fallback batches: 136;
- source-level micro precision: 92.17%;
- source-level micro recall: 97.45%;
- estimated successful-call cost: $0.037991.

The full attempt is not a pure Groq-only benchmark because the daily token
limit was reached. Explain this as honest failure/recovery evidence and a reason
for quota-aware batching.

## Reasoning and Source Retrieval

The final prototype does not use conventional vector-database RAG. It uses
structured, source-backed retrieval:

1. Semantic and deterministic analysis produce claims.
2. Every claim stores all supporting submission IDs.
3. Email briefings show representative source IDs and inspection links.
4. Source inspection retrieves normalized reports directly by stable ID.
5. Challenges retrieve the affected claim and its supporting source bundle.

This design provides RAG-like grounding without embedding search because the
source records are already structured and have stable identifiers.

## Priority Design Based on Stakeholder Feedback

Ted requested:

1. identification of high-priority tasks requiring immediate attention,
   including safety concerns and malfunctioning equipment;
2. prioritization of important tasks not marked urgent;
3. employee recognition, including positive feedback and coaching
   opportunities.

The final email divides selected claims into:

- **Immediate attention:** safety concerns, equipment/register disruptions, and
  sensitive personnel notes requiring private inspection.
- **Important follow-up:** shortages, waste, inventory problems, dietary
  questions, portion concerns, and guarded coaching/training review signals.
- **Monitor and recognize:** lower-risk requests and positive recognition.

The semantic schema supports explicit safety and coaching-review categories.
The current synthetic dataset may not contain a detected example of every new
category; the implementation is designed to process them when present.

## Gmail Delivery

Gmail delivery is implemented using:

- Google Desktop OAuth client credentials;
- the narrow `https://www.googleapis.com/auth/gmail.send` scope;
- a local Git-ignored refresh token;
- RFC-compatible multipart HTML/plain-text email;
- base64URL encoding;
- Gmail `users.messages.send`;
- an explicit `--confirm-send` flag.

Tests mock the Gmail service and decode the generated MIME payload. Automated
tests never transmit email. Production scheduling remains separate and is not
deployed.

## HITL and LangGraph

The Week 6 demonstration graph includes:

- planner;
- ingestion tool;
- evaluator;
- normalization;
- analysis;
- briefing draft;
- HITL review;
- finalization;
- fallback.

It has conditional routing, retry thresholds, fallback behavior, persisted
SQLite checkpoints, and an interrupt before the demonstration's finalization
step.

The final product's more realistic HITL flow happens after delivery:

```text
Ted challenges a claim in ordinary English
-> supporting sources are retrieved
-> correction is proposed
-> Ted confirms or cancels
-> only confirmed corrections enter history
```

Corrections do not automatically alter future classification rules.

## Responsible AI

Major risks:

- unsupported or hallucinated claims;
- incorrect source attribution;
- model overtrust;
- privacy exposure;
- harmful personnel conclusions;
- hidden model fallback;
- financial overclaiming;
- accidental email sending.

Mitigations:

- exact source excerpts and stable IDs;
- schema validation;
- deterministic calculations;
- retries and explicit fallback logs;
- source-inspection links;
- correction confirmation;
- refusal of accusations, termination, discipline, and mass distribution of
  unverified allegations;
- coaching signals framed as private review;
- no confirmed savings without cost data;
- send-only Gmail scope;
- explicit send confirmation;
- secrets and OAuth tokens excluded from Git.

## Validation Evidence

Current automated test result:

```text
62 passed
```

The final asset generation produced:

- 399 source-backed claims;
- 12 weekly email previews;
- 3 monthly email previews;
- 15 total HTML/plain-text briefing pairs.

The Gmail preview command selected the Week 1 email for
`wanlemvoi@gmail.com` without sending and reported:

- subject: `ShiftNotes Weekly Briefing: 4 kiosks need attention | Week 1:
  March 2 - March 5, 2026`;
- HTML bytes: 10,837;
- plain-text bytes: 2,097.

Live Gmail delivery was subsequently authorized and demonstrated:

- recipient: `wanlemvoi@gmail.com`;
- briefing: weekly, `week-01`;
- Gmail message ID: `19f0721c707b2313`;
- evidence: `final_project/evidence/final/gmail_delivery.log`.

The report may state that live delivery was demonstrated. It must still explain
that each installation requires its own OAuth authorization and that automatic
scheduling is not deployed.

## External Feedback

### Jayden Lawson

Jayden is a student peer reviewer. His verbal feedback was implemented before
being formally recorded. The retrospective record says the manager-facing
output should prioritize actionable findings, preserve source inspection, and
remain focused on the real workflow. Do not present reconstructed wording as a
direct quote.

### Ted Snow

Ted is the intended workplace user and is not part of the student development
team. His email said the project was progressing well and requested urgent task
identification, non-urgent prioritization, and employee recognition/coaching
visibility. The final implementation responds with priority tiers, equipment
escalation, safety-category support, recognition tracking, and guarded
coaching-review signals.

## Reproducibility

Expected setup:

```bash
python -m pip install -e .
python -m pytest -q
python final_project/src/shiftnotes/cli.py baseline
python final_project/src/shiftnotes/cli.py briefings
python final_project/src/shiftnotes/cli.py product-assets
python final_project/src/shiftnotes/cli.py gmail-preview --type weekly --period week-01
```

Optional external integrations require local `.env` values. Secrets must never
be included in the report or repository.

## Known Limitations

- Production scheduling is not deployed.
- Gmail requires per-installation OAuth setup.
- The final large dataset is synthetic.
- Groq full backfills need quota-aware batching.
- Streamlit is local and unauthenticated.
- Challenge interpretation remains deterministic behind a replaceable provider
  boundary.
- Source links are local rather than hosted JotForm links.
- Financial impact is qualitative without cost, volume, revenue, and labor data.
- The priority rules are transparent prototype rules and require workplace
  validation before production use.

## Lessons to Emphasize

- Direct JotForm API access is cleaner than parsing rendered notification email.
- A hybrid deterministic/model architecture is more reliable than asking a
  language model to perform every task.
- Source traceability is part of the product, not an optional citation layer.
- Email-first delivery better matches the manager's workflow than a
  dashboard-first design.
- Missing submissions are operational information.
- Honest fallback reporting is stronger evidence than hiding quota failures.
- HITL should occur at meaningful decision points without creating unnecessary
  approval work.
- Stakeholder feedback materially changed prioritization and recognition design.

## Recommended Report Structure

1. Title page.
2. Abstract.
3. Problem Statement and Business Justification.
4. Architecture Decisions and Framework Rationale.
5. Model Selection and Benchmark Evidence.
6. RAG or Reasoning Pipeline Design.
7. Responsible AI Analysis.
8. Implementation and Validation Evidence.
9. Lessons Learned.
10. Known Limitations and Future Work.
11. Conclusion.
12. References.

Use figure placeholders where useful:

- Figure 1: End-to-end ShiftNotes architecture.
- Figure 2: LangGraph nodes and conditional routing.
- Figure 3: Email-first manager workflow and post-delivery HITL correction.

The source draft `TECHNICAL_REPORT.md`, `MODEL_SELECTION_AND_BENCHMARK.md`,
`PRODUCT_WORKFLOW.md`, `README.md`, and test files may be consulted for
additional detail, but this context document defines the factual boundaries.
