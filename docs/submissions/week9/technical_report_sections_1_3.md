# ShiftNotes Technical Report

## 1. Problem Statement and Business Justification

ShiftNotes addresses a practical operations problem: shift-note reports contain
useful management information, but that information is difficult to use when it
arrives as many individual reports. A manager such as Ted may receive separate
JotForm submissions from multiple kiosks across a week or month. Each report can
include food quality ratings, quantity ratings, food concerns, guest feedback,
team recognition, operational issues, and waste counts. Individually, these
reports are readable. Collectively, they become time-consuming to review.

The business problem is not that reports are missing value. The problem is that
the value is trapped in unaggregated text. Recurring issues such as food
shortages, repeated guest requests, high unclaimed lunches, equipment problems,
and employee recognition may only become obvious after someone reads dozens of
notes. That creates a management burden and increases the chance that important
patterns are missed.

The final ShiftNotes prototype is designed around a simple value proposition:
turn submitted shift reports into source-backed weekly and monthly briefing
emails. The email is the primary product surface because it fits the manager's
workflow. Ted should not need to open a dashboard every day. Instead, he should
receive a concise briefing that explains what changed, what repeated, what needs
attention, and where the evidence came from. The dashboard exists only as a
secondary inspection tool for source review, claim challenge, and correction
history.

This matters operationally because better visibility can support faster and more
careful decisions. Food shortage patterns can inform prep planning. High waste
or unclaimed-lunch patterns can indicate possible overproduction. Repeated guest
requests can guide menu or communication decisions. Missing report detection can
improve accountability. Employee recognition can help leadership notice strong
performance that might otherwise be buried in daily notes.

The project does not claim to automate management decisions. Its purpose is to
reduce manual reading, organize evidence, and make human review more focused.
The prototype proves that operational reports can be transformed into
actionable, source-backed operational intelligence.

## 2. Architecture Decisions and Framework Rationale

ShiftNotes uses a pipeline architecture built around reproducibility,
traceability, and human review.

The main flow is:

```text
JotForm-style submissions
-> normalization and validation
-> schedule-aware completeness checks
-> deterministic operational metrics
-> semantic extraction for free-text fields
-> source-backed claim generation
-> weekly/monthly email previews
-> optional source inspection and claim correction
```

JotForm API ingestion is the preferred production direction because JotForm is
the source system that stores structured form submissions. Earlier planning
considered Gmail parsing because Ted receives JotForm emails, but direct
JotForm access is cleaner and less brittle. For the final project, saved
JotForm-shaped fixtures make the demo reproducible without exposing private
credentials or production submissions.

The cleaning layer normalizes dates, kiosk names, ratings, text fields, and
unclaimed-lunch counts. It also separates valid reports from malformed records
and identifies duplicates. This matters because analysis should not silently use
bad records.

The schedule-aware layer compares expected kiosk/date reports against received
valid reports. This is important because missing reports are themselves an
operational signal. If a kiosk does not submit notes on Tuesday and Thursday,
the weekly briefing should say so before anyone trusts the trend analysis.

Exact metrics are computed deterministically in Python. Ratings, counts, waste
totals, missing reports, duplicate detection, and period grouping do not need a
language model. Keeping them deterministic reduces cost and avoids avoidable
model arithmetic errors.

Semantic interpretation is used only for free-text fields: food concerns or
outages, team recognition, guest issues, and operational notes. These fields
contain the operational meaning that simple numeric calculations cannot fully
capture. The semantic layer extracts categorized source-backed signals such as
food shortages, overproduction, dietary questions, equipment failures,
recognition, inventory inconsistencies, portion complaints, beverage requests,
and sensitive personnel notes.

LangGraph is included for stateful orchestration and HITL demonstration. It
supports planner/tool/evaluator responsibilities, conditional routing,
retry/fallback behavior, persisted checkpoints, and a human confirmation step.
For the final product experience, the most meaningful HITL behavior happens
after the briefing is delivered: Ted can inspect a claim, challenge it in
ordinary English, review the proposed correction, and confirm or cancel before
anything is saved.

Streamlit is used as a local inspection workspace. It is intentionally not the
primary interface. The primary interface is the generated briefing email. The
workspace supports demo needs: source inspection, challenge review, confirmation
checkpoint, safety refusals, and correction history.

## 3. Model Selection and Benchmark Evidence

ShiftNotes uses a hybrid model strategy. Python performs deterministic
calculations, and Groq handles semantic interpretation of free-text fields.

The selected default model is `openai/gpt-oss-20b` through Groq. It was chosen
because it supports strict structured outputs and is cost-effective enough for a
prototype. The model can be changed through `GROQ_MODEL` without changing the
rest of the pipeline.

The semantic extraction contract is strict. The model must return JSON matching
the expected schema. Each signal must include a category, subject, severity,
confidence, source field, exact evidence excerpt, sensitivity flag, and short
rationale. ShiftNotes rejects model output if it invents source IDs, omits
requested source IDs, duplicates source IDs, violates the schema, or cites an
evidence excerpt that does not appear in the named source field.

The benchmark uses the synthetic final dataset with planted ground-truth
patterns. Ground truth is source-level, meaning the benchmark checks whether the
system identified the correct reports for each category rather than merely
producing plausible summary text.

Controlled live validation results:

- Six-report validation:
  - retries: 0;
  - fallback batches: 0;
  - source-level micro precision: 100%;
  - source-level micro recall: 100%;
  - estimated cost: $0.002070.
- Twenty-four-report validation:
  - cache hits: 21;
  - retries: 1;
  - fallback batches: 0;
  - source-level micro precision: 100%;
  - source-level micro recall: 100%;
  - estimated cost: $0.001132.
- Full-dataset attempt:
  - reports processed: 270;
  - retries: 278;
  - fallback batches: 136;
  - source-level micro precision: 92.17%;
  - source-level micro recall: 97.45%;
  - estimated successful-call cost: $0.037991.

The full-dataset attempt is useful evidence, but it is not a pure Groq-only
benchmark because the on-demand daily token limit was reached. ShiftNotes
retried and then used deterministic fallback for unresolved batches. This is
documented as a production constraint rather than hidden as success. A
production version should run backfills in smaller scheduled batches, wait for
quota reset, or use a higher service tier.

## 4. RAG or Reasoning Pipeline Design

ShiftNotes does not use a traditional vector RAG system in the final prototype.
Instead, it uses a source-backed reasoning pipeline. This choice matches the
project's operational need: Ted needs claims tied directly to reports, not open
ended document retrieval.

The reasoning pipeline is:

```text
structured report records
-> deterministic metrics
-> semantic signal extraction
-> source-backed claim catalog
-> weekly/monthly briefing generation
-> source inspection
-> human challenge and correction
```

Every important claim stores supporting submission IDs. For example, if the
briefing says that overproduction or elevated waste appeared in 17 reports at
Market Grill, the claim record contains the source IDs supporting that count.
The email preview shows representative source IDs, and the inspection workspace
can display the underlying normalized report fields.

This is similar in spirit to RAG because generated statements remain connected
to source material. However, the retrieval step is deterministic and structured:
the system retrieves reports by source ID rather than embedding and searching
unstructured documents. This reduces complexity and makes verification clearer
for the prototype.

The human challenge flow is also part of the reasoning design. Ted can challenge
a claim in ordinary English. The system retrieves the supporting reports,
proposes a correction when it can identify the issue, and requires confirmation
before saving. Confirmed corrections are audit records for the challenged claim;
they do not automatically update future classification rules.

## 5. Responsible AI Analysis

ShiftNotes has several responsible AI risks:

- false operational claims;
- overtrust in model-generated summaries;
- unsupported personnel accusations;
- privacy exposure from operational reports;
- incorrect source attribution;
- hidden fallback behavior;
- financial overclaiming without cost data.

The prototype includes mitigations for each risk.

First, every semantic signal requires exact evidence from a source field. If the
model cites text that is not present in the report, the output is rejected.
Second, important claims preserve source IDs so Ted can inspect the evidence.
Third, exact calculations remain deterministic and are not delegated to the
model.

Personnel-related content receives special handling. ShiftNotes can mark
sensitive personnel notes, but it cannot recommend discipline, termination, or
employee accusations. The challenge workflow refuses unsafe requests such as
spreading unverified allegations or recommending that someone be fired.

The system also avoids financial overclaiming. It can identify possible waste or
overproduction opportunities, but it does not calculate dollar savings because
meal cost, transaction volume, revenue, and labor-hour data are not available.
The email and monthly briefing explicitly describe financial findings as
possible opportunities, not confirmed savings.

Fallback behavior is documented. The full-dataset Groq run hit quota limits and
used deterministic fallback. The benchmark documentation labels this clearly so
model evidence is not overstated.

Finally, the primary product design keeps humans in control. ShiftNotes
summarizes and organizes evidence; it does not take operational action.

## 6. Lessons Learned and Future Work

The most important lesson is that the core idea works: operational shift notes
can be transformed into useful source-backed briefings. The final prototype can
detect missing reports, summarize weekly and monthly metrics, extract semantic
signals from free text, preserve source references, and produce email previews
that match the intended manager workflow.

Another lesson is that the email-first design is stronger than a dashboard-first
design for this use case. Ted should not need to seek out another tool. A weekly
or monthly briefing email is more likely to fit the real workflow. The dashboard
is still valuable, but as a secondary inspection and correction surface.

The model benchmark also revealed an important production constraint: even when
the model works, API quotas and batching strategy matter. The small and
medium-sized validations were clean. The full run produced useful accuracy
evidence but also showed that full backfills need quota-aware scheduling.

The current limitations are clear. Email delivery is not connected to Gmail.
The scheduler is represented as policy metadata rather than a deployed job.
The demo uses synthetic data instead of private production reports. The
challenge interpretation is deterministic/mock behavior behind a replaceable
provider boundary. The Streamlit workspace is local, not hosted or
authenticated. Source links point to local inspection views rather than original
JotForm emails.

Future work should focus on:

- Gmail delivery for weekly and monthly briefings;
- production scheduling in Pacific time;
- authenticated hosted source inspection;
- live JotForm API deployment with Ted's form credentials;
- quota-aware Groq backfills;
- Groq-assisted challenge interpretation after validation;
- richer cost analysis once meal cost, transaction volume, and labor data are
  available;
- user testing with Ted or another non-team operations reviewer.

ShiftNotes is not a finished production system, but it is a production-shaped
prototype. It demonstrates the core value: turning many shift notes into
traceable, reviewable operational intelligence that helps a manager focus on
what matters.
