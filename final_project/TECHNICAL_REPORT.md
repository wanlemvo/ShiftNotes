# ShiftNotes Technical Report

## Abstract

ShiftNotes is a workplace-focused operational intelligence prototype that turns
JotForm-style shift-note reports into source-backed weekly and monthly
briefings. The project addresses a real operations problem: managers receive
many individual reports that contain useful information, but the value is hard
to see without manually reading every entry. The final prototype demonstrates a
pipeline that normalizes shift reports, validates data quality, detects missing
reports, calculates deterministic metrics, uses AI for semantic interpretation
of free-text fields, preserves source traceability, and generates briefing
emails for managerial review. The primary user experience is intentionally
email-first because the target manager should not need to open a dashboard
unless a claim requires inspection. The system includes human-in-the-loop
review, source-backed claims, responsible AI safeguards, benchmark evidence,
and clear limitations. ShiftNotes is not a complete production system, but it
proves that operational reports can be transformed into actionable,
reviewable intelligence.

## 1. Problem Statement and Business Justification

ShiftNotes addresses a practical operations problem: shift-note reports contain
valuable management information, but that information is difficult to use when
it arrives as many separate reports. A manager such as Ted may receive JotForm
submissions from multiple kiosks across a week or month. Each report can
include food quality ratings, food quantity ratings, food concerns, guest
feedback, team recognition, operational issues, and waste counts. Individually,
these reports are readable. Collectively, they become time-consuming to review.

The business problem is not that reports lack value. The problem is that the
value is trapped in unaggregated daily notes. Recurring issues such as food
shortages, repeated guest requests, high unclaimed lunches, equipment problems,
and employee recognition may only become obvious after someone reads dozens of
entries. That creates a management burden and increases the chance that
important patterns are missed. A manager may notice a major issue when it is
obvious, but subtle trends can disappear into routine reporting.

The final ShiftNotes prototype is designed around a simple value proposition:
turn submitted shift reports into source-backed weekly and monthly briefing
emails. The email is the primary product surface because it fits the manager's
workflow. Ted should not need to open a dashboard every day. Instead, he should
receive a concise briefing that explains what changed, what repeated, what
needs attention, and where the evidence came from. The dashboard exists only as
a secondary inspection tool for source review, claim challenge, and correction
history.

This matters operationally because better visibility can support faster and
more careful decisions. Food shortage patterns can inform prep planning. High
waste or unclaimed-lunch patterns can indicate possible overproduction.
Repeated guest requests can guide menu or communication decisions. Missing
report detection can improve accountability. Employee recognition can help
leadership notice strong performance that might otherwise be buried in daily
notes.

The project is also valuable because the source data is already structured
around the questions leadership cares about. The JotForm-style report includes
ratings, food concerns, recognition, guest issues, operational notes, and
unclaimed lunches. That makes the problem more realistic and more solvable than
trying to infer everything from unstructured emails. ShiftNotes does not need
to invent an operational reporting process; it adds intelligence on top of an
existing reporting process.

The project does not claim to automate management decisions. Its purpose is to
reduce manual reading, organize evidence, and make human review more focused.
The prototype proves that operational reports can be transformed into
actionable, source-backed operational intelligence while keeping the manager in
control.

## 2. Architecture Decisions and Framework Rationale

ShiftNotes uses a pipeline architecture built around reproducibility,
traceability, and human review. The main flow is:

```text
JotForm-style submissions
-> normalization and validation
-> schedule-aware completeness checks
-> deterministic operational metrics
-> semantic extraction for free-text fields
-> source-backed claim generation
-> urgency and follow-up classification
-> weekly/monthly HTML and plain-text briefings
-> explicitly confirmed Gmail API delivery
-> optional source inspection and claim correction
```

JotForm API ingestion is the preferred production direction because JotForm is
the source system that stores structured form submissions. Earlier planning
considered Gmail parsing because Ted receives JotForm notification emails, but
direct JotForm access is cleaner and less brittle. Email parsing would require
extracting values from rendered HTML, star-rating visuals, forwarded-message
formatting, and possible email-client differences. JotForm API access should
return the submitted fields more directly. For the final project, saved
JotForm-shaped fixtures make the demo reproducible without exposing private
credentials or production submissions.

The cleaning layer normalizes dates, kiosk names, ratings, text fields, and
unclaimed-lunch counts. It separates valid reports from malformed records and
identifies duplicates. This matters because analysis should not silently use
bad records. If a report has an invalid date, missing kiosk, impossible rating,
or duplicate submission ID, the system should flag the issue before trend
analysis is trusted.

The schedule-aware layer compares expected kiosk/date reports against received
valid reports. This is important because missing reports are themselves an
operational signal. If a kiosk does not submit notes on Tuesday and Thursday,
the weekly briefing should say so before anyone trusts the trend analysis. A
quiet week could mean there were no problems, but it could also mean reports
were not submitted. ShiftNotes therefore treats completeness as a first-class
part of the briefing.

Exact metrics are computed deterministically in Python. Ratings, counts, waste
totals, missing reports, duplicate detection, and period grouping do not need a
language model. Keeping them deterministic reduces cost and avoids avoidable
model arithmetic errors. It also makes the system easier to test because exact
calculations can be verified with normal unit tests.

Semantic interpretation is used only for free-text fields: food concerns or
outages, team recognition, guest issues, and operational notes. These fields
contain the operational meaning that simple numeric calculations cannot fully
capture. The semantic layer extracts categorized source-backed signals such as
food shortages, overproduction, dietary questions, equipment failures,
recognition, inventory inconsistencies, portion complaints, beverage requests,
explicit safety concerns, guarded coaching-review signals, and sensitive
personnel notes.

The manager-facing layer divides selected claims into immediate attention,
important follow-up, and monitor/recognize sections. Safety concerns,
equipment failures, register disruptions, and sensitive personnel notes are
elevated for immediate inspection. Shortages, waste, inventory inconsistencies,
dietary questions, and coaching-review signals appear as important follow-up.
Recognition and lower-risk recurring requests remain visible without being
presented as emergencies. Coaching signals never recommend discipline; they
only direct a manager to inspect the original source privately.

LangGraph is included for stateful orchestration and human-in-the-loop
demonstration. It supports planner/tool/evaluator responsibilities,
conditional routing, retry/fallback behavior, persisted checkpoints, and a
human confirmation step. This satisfies the stateful agent requirements while
also aligning with the real product need: the system should be able to pause,
recover, and preserve decision state.

For the final product experience, the most meaningful human-in-the-loop
behavior happens after the briefing is delivered. Ted can inspect a claim,
challenge it in ordinary English, review the proposed correction, and confirm
or cancel before anything is saved. This design is more realistic than asking
Ted to approve every briefing before receiving it. The product should reduce
his workload, not create a new approval chore.

Streamlit is used as a local inspection workspace. It is intentionally not the
primary interface. The primary interface is the generated briefing email. The
workspace supports demo needs: source inspection, challenge review,
confirmation checkpoint, safety refusals, and correction history. In a
production version, this workspace would need hosting, authentication, and
access control before it could safely handle real operational data.

Gmail delivery is implemented as a narrow adapter around the generated
briefing. A Desktop OAuth client authorizes only the `gmail.send` scope, the
refresh token remains in a Git-ignored local file, and the command refuses to
send unless the operator supplies an explicit confirmation flag. This preserves
the preview-first workflow and prevents tests or ordinary asset generation from
accidentally sending email.

The final validation sent the Week 1 multipart briefing through Gmail to the
authorized test account. Gmail accepted the message and returned message ID
`19f0721c707b2313`, providing direct evidence that the delivery boundary works.

## 3. Model Selection and Benchmark Evidence

ShiftNotes uses a hybrid model strategy. Python performs deterministic
calculations, and Groq handles semantic interpretation of free-text fields. The
project deliberately avoids using a language model for tasks that simple code
can perform more reliably.

The selected default model is `openai/gpt-oss-20b` through Groq. It was chosen
because it supports strict structured outputs and is cost-effective enough for
a prototype. The model can be changed through `GROQ_MODEL` without changing the
rest of the pipeline. This provider boundary matters because model quality,
pricing, latency, and safety behavior can change over time. The architecture
should not trap the project inside one provider.

The semantic extraction contract is strict. The model must return JSON matching
the expected schema. Each signal must include a category, subject, severity,
confidence, source field, exact evidence excerpt, sensitivity flag, and short
rationale. ShiftNotes rejects model output if it invents source IDs, omits
requested source IDs, duplicates source IDs, violates the schema, or cites an
evidence excerpt that does not appear in the named source field.

The benchmark uses the synthetic final dataset with planted ground-truth
patterns. Ground truth is source-level, meaning the benchmark checks whether
the system identified the correct reports for each category rather than merely
producing plausible summary text. This is important because a plausible
briefing is not enough. The system must be able to point back to the specific
reports that support its claims.

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

The broader model strategy also considered GPT-class, Claude-class, and
Gemini-class models. GPT-class models scored well for coding, structured
output, and general reasoning. Claude-class models were strong for long-context
review, careful writing, and cautious analysis. Gemini-class models remained
interesting for large-context and multimodal tasks. Groq-hosted models were
chosen for the prototype because low latency and practical cost made them a
good fit for iterative semantic extraction. The final recommendation is not
that Groq is always the best model. The recommendation is that ShiftNotes
should separate exact computation from semantic interpretation and keep the
semantic provider replaceable.

## 4. RAG or Reasoning Pipeline Design

ShiftNotes does not use a traditional vector RAG system in the final
prototype. Instead, it uses a source-backed reasoning pipeline. This choice
matches the project's operational need: Ted needs claims tied directly to
reports, not open-ended document retrieval.

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
briefing says that overproduction or elevated waste appeared in multiple
reports at a kiosk, the claim record contains the source IDs supporting that
count. The email preview shows representative source IDs, and the inspection
workspace can display the underlying normalized report fields.

This is similar in spirit to RAG because generated statements remain connected
to source material. However, the retrieval step is deterministic and
structured: the system retrieves reports by source ID rather than embedding and
searching unstructured documents. This reduces complexity and makes
verification clearer for the prototype.

This design also fits the kind of questions the manager is likely to ask. A
traditional RAG system is useful when the user has open-ended questions over a
large document collection. ShiftNotes is more constrained. It needs to answer
recurring operational questions: Which kiosk had missing reports? Which kiosk
had the highest waste? What food concerns appeared repeatedly? Which guest
requests kept coming up? Which claims need source review? Those questions map
well to structured records, deterministic grouping, and source-backed claims.

The human challenge flow is also part of the reasoning design. Ted can
challenge a claim in ordinary English. The system retrieves the supporting
reports, proposes a correction when it can identify the issue, and requires
confirmation before saving. Confirmed corrections are audit records for the
challenged claim; they do not automatically update future classification rules.

This distinction matters. If Ted says a claim is wrong, the system should not
silently change future behavior based on one correction. A correction can fix
the current claim and preserve audit history. A separate reviewed update would
be required before future classification rules or model prompts are changed.

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

First, every semantic signal requires exact evidence from a source field. If
the model cites text that is not present in the report, the output is rejected.
Second, important claims preserve source IDs so Ted can inspect the evidence.
Third, exact calculations remain deterministic and are not delegated to the
model.

Personnel-related content receives special handling. ShiftNotes can mark
sensitive personnel notes, but it cannot recommend discipline, termination, or
employee accusations. The challenge workflow refuses unsafe requests such as
spreading unverified allegations or recommending that someone be fired. This is
important because shift notes can include names and subjective comments. A tool
that summarizes those notes must not turn ambiguity into accusation.

The system also avoids financial overclaiming. It can identify possible waste
or overproduction opportunities, but it does not calculate dollar savings
because meal cost, transaction volume, revenue, and labor-hour data are not
available. The email and monthly briefing explicitly describe financial
findings as possible opportunities, not confirmed savings.

Privacy is another major concern. Real JotForm reports may contain names,
workplace details, and business-sensitive information. The final demo uses
synthetic data to avoid exposing private production records. The repository
includes `.env.example` but does not commit real API keys. In production, raw
data access, logs, and any hosted dashboard would need access control and data
retention rules.

Fallback behavior is documented. The full-dataset Groq run hit quota limits and
used deterministic fallback. The benchmark documentation labels this clearly so
model evidence is not overstated. This is part of responsible AI because users
should know when results come from the model, deterministic logic, or fallback
behavior.

Finally, the primary product design keeps humans in control. ShiftNotes
summarizes and organizes evidence; it does not take operational action. The
manager remains responsible for interpreting the briefing, inspecting important
claims, and deciding what to do next.

## 6. Implementation and Validation Evidence

The final prototype includes code, data, tests, documentation, and generated
demo artifacts. The core implementation lives in `final_project/src/shiftnotes`.
The major modules include normalization, JotForm client scaffolding, baseline
analysis, semantic extraction, benchmarking, briefing generation, email preview
generation, LangGraph orchestration, scheduling policy, and product correction
flow.

The dataset was expanded beyond the early team prototype. The final mock
dataset represents three months of operational reporting across six kiosks.
It includes realistic variation: different shift leads, ratings from one to
five, unclaimed lunch counts, shortages, underproduction, guest praise,
complaints, dietary questions, equipment problems, quiet days, missing reports,
duplicates, malformed records, and personnel-sensitive comments. A companion
ground-truth file documents planted patterns so the analysis can be evaluated
against known expectations rather than judged only by whether the summary
sounds reasonable.

The generated artifacts include normalized reports, reporting completeness,
weekly summaries, monthly summaries, source-backed claims, benchmark results,
AI extraction results, and email previews. Weekly email previews demonstrate
the kiosk-by-kiosk briefing format. Monthly previews emphasize broader trends
and cost-saving opportunities while staying careful not to claim confirmed
dollar savings.

The test suite validates the main behavior. Tests cover JotForm normalization,
final mock dataset structure, baseline analysis, final briefings, LangGraph
workflow behavior, product correction flow, and semantic extraction validation.
The local suite passed with:

```text
62 passed
```

The LangGraph evidence demonstrates conditional routing, retry behavior,
fallback behavior, and a human-in-the-loop checkpoint. One run simulates an
ingestion failure, retries successfully, continues through normalization and
analysis, drafts a source-backed briefing, and pauses for review. Another run
exceeds the retry limit and routes to fallback. This provides evidence that
the workflow can handle failure rather than only succeeding in the happy path.

The final product HITL behavior is post-delivery review. Ted receives the
briefing first. If a claim appears wrong, he can inspect the supporting reports
and challenge the claim in ordinary English. The system then proposes a
correction and requires confirmation before saving it. This better matches the
real workflow than requiring pre-approval of every briefing.

## 7. Lessons Learned

The most important lesson is that the core idea works: operational shift notes
can be transformed into useful source-backed briefings. The final prototype can
detect missing reports, summarize weekly and monthly metrics, extract semantic
signals from free text, preserve source references, and produce email previews
that match the intended manager workflow.

Another lesson is that the email-first design is stronger than a dashboard-first
design for this use case. Ted should not need to seek out another tool. A
weekly or monthly briefing email is more likely to fit the real workflow. The
dashboard is still valuable, but as a secondary inspection and correction
surface.

The project also showed the importance of clean source data. At first, Gmail
parsing seemed like the natural path because the manager receives emails. After
reviewing the actual workflow, JotForm API ingestion became the better
production direction. It is easier to clean structured form submissions than to
parse rendered email notifications. This decision improved the architecture and
made the prototype more realistic.

The model benchmark revealed an important production constraint: even when the
model works, API quotas and batching strategy matter. The small and
medium-sized validations were clean. The full run produced useful accuracy
evidence but also showed that full backfills need quota-aware scheduling. This
is a practical lesson for any operational AI system: model quality is only one
part of reliability. Rate limits, fallback behavior, caching, and auditability
also matter.

The final lesson is that human-in-the-loop design should match the user
workflow. A class checkpoint may ask for an interrupt before a high-impact
operation, but the real product needs a post-delivery correction loop. Ted
should not need to approve his own briefing before seeing it. He should be able
to inspect and challenge claims after delivery.

## 8. Known Limitations and Future Work

The current limitations are clear. Gmail delivery is implemented through a
narrow send-only OAuth integration, but every installation still requires a
one-time Google Cloud OAuth client setup and user authorization. The scheduler
is represented as policy metadata rather than a deployed job.
The demo uses synthetic data instead of private production reports. The
challenge interpretation is deterministic/mock behavior behind a replaceable
provider boundary. The Streamlit workspace is local, not hosted or
authenticated. Source links point to local inspection views rather than
original JotForm records or emails.

Future work should focus on:

- automated Gmail delivery triggered by the production scheduler;
- production scheduling in Pacific time;
- authenticated hosted source inspection;
- live JotForm API deployment with Ted's form credentials;
- quota-aware Groq backfills;
- Groq-assisted challenge interpretation after validation;
- richer cost analysis once meal cost, transaction volume, and labor data are
  available;
- user testing with Ted or another non-team operations reviewer.

The production setup would likely use JotForm API ingestion as the primary data
source, scheduled processing to generate weekly and monthly briefings, email
delivery to Ted, and a secure web interface only for inspection and correction.
The model layer should remain replaceable. The validation layer should remain
strict. The system should continue to treat human review as central rather than
optional.

## 9. Conclusion

ShiftNotes is not a finished production system, but it is a production-shaped
prototype. It demonstrates the core value: turning many shift notes into
traceable, reviewable operational intelligence that helps a manager focus on
what matters.

The project satisfies the final project goals by presenting a documented,
test-covered, reproducible codebase; explaining architecture decisions and
framework rationale; providing model selection and benchmark evidence;
describing the reasoning pipeline; analyzing responsible AI risks and
mitigations; and identifying lessons learned and future work.

Most importantly, the prototype remains grounded in the real operational
workflow. The goal is not to build an impressive dashboard for its own sake.
The goal is to help Ted understand what is happening across kiosks without
manually reading every report. ShiftNotes proves that this is possible while
preserving source evidence, supporting human correction, and avoiding
unsupported AI authority.
