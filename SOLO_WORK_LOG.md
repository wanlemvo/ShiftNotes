# Solo Work Log

## Purpose

This document records the point where ShiftNotes moved from a team checkpoint project into my independent project work.

The team and I last worked together on the Week 8 submission: Final Project Prototype Kickoff. After that checkpoint, beginning with Week 9, I continued developing my own version of ShiftNotes independently.

My independent work is focused on solving a real operational reporting problem at my job. The team may continue working on a similar class project, but this log documents the version I am building around my workplace workflow, operational needs, and prototype goals.

## Collaboration Timeline

### Before and Through Week 8

Work during this period was connected to the team project and shared checkpoint requirements.

The shared Week 8 focus was:

- Final project prototype kickoff
- Initial project concept and scope
- Architecture planning
- Mock shift-note prototype direction
- Required class checkpoint artifacts

The Week 8 submission is the collaboration checkpoint where the shared team phase ends for the purpose of this log.

### Week 9 and Forward

Beginning after the Week 8 checkpoint, I continued independently.

The independent version of ShiftNotes is tailored to:

- My actual operations environment
- Shift reports and recurring operational notes
- Food shortages, guest requests, employee recognition, waste, and operational issues
- Turning reports into useful operational intelligence
- Helping leadership review patterns without manually reading every report

## Scope Difference

The team project and my independent project may share the same original idea, but they should be treated as separate paths after Week 8.

### Team-Oriented Path

The team path may include broader class-project features, shared design decisions, or implementation choices made by multiple collaborators.

### My Independent Path

My independent path is focused on proving and improving a practical workflow for my job:

```text
Mock or real shift notes
    |
    v
Cleaning and organization
    |
    v
Trend analysis
    |
    v
Insight generation
    |
    v
Weekly operations summary
    |
    v
Human review and operational follow-up
```

## Attribution Rule

When documenting future work, I will separate:

- Work completed as part of the team through Week 8
- Work I completed independently from Week 9 onward
- Work inspired by team ideas but modified or rebuilt for my workplace use case
- Work that still needs validation before being claimed as complete

This is intended to keep the project history honest and traceable.

## Ongoing Documentation Rule

From this point forward, any significant project change should be recorded in this log.

Significant changes include:

- Architectural decisions
- Refactors
- Removed features or files
- Added features or files
- Changes to project scope
- Changes to implementation strategy
- Major documentation rewrites
- Decisions about what gets pushed as the real independent project
- Evidence gathered for the final paper or final demo

This log should act as the project memory for the independent version of ShiftNotes. It will help support the final 10-page paper by preserving not just what was built, but why each major direction was chosen.

When possible, each entry should answer:

- What changed?
- Why did it change?
- What evidence or reasoning supported the decision?
- What does this mean for the next step?

## Independent Change Log

Use this section to record changes made after the Week 8 checkpoint.

### Week 9

Status: independent work begins.

Planned documentation:

- Identify what exists in the GitHub/team version.
- Compare the team version against my original docs and prototype goals.
- Decide which pieces support my workplace-specific version.
- Document what needs to be kept, revised, removed, or rebuilt.

Changes:

- Created this solo work log to document the transition from team work to independent work.
- Established the rule that significant independent changes must be recorded here.
- Decided not to make implementation changes until the independent direction, backlog, and final-project structure are clear.
- Reviewed the current GitHub/team implementation at a high level and identified it as a useful but messy prototype artifact rather than the final independent implementation.
- Began reviewing the team mock dataset against the actual JotForm-style report structure.
- Identified that the source form is already operationally useful because it asks directly for food quality, quantity, concerns, recognition, guest issues, operational notes, and waste.
- Identified that guest issues, operational notes, and food concerns are the most semantic fields and likely need the most careful analysis.
- Identified that the current mock dataset over-focuses on poke requests and should be expanded with more varied guest feedback and longer time windows before becoming final-project evidence.
- Identified email ingestion as a key architecture question: Ted receives individual JotForm emails, not necessarily a clean CSV export.
- Documented that the final system needs a reliable way to convert JotForm email bodies into structured records before analysis.
- Defined the preferred real workflow: preserve Ted's original JotForm emails, assist with kiosk folder/label organization, parse the emails into clean data, then generate weekly and monthly operational briefings.
- Clarified that weekly and monthly briefings are more valuable than daily briefings because the core value is trend detection, not single-report summarization.
- Defined source-backed claims as a core requirement: every important trend or claim should link back to the original reports that support it.
- Expanded the HITL concept: Ted should be able to inspect the evidence behind any important claim, mark the AI wrong, and have the system correct itself. This applies broadly to food trends, guest requests, waste patterns, missing reports, operational issues, recognition, and complaints.
- Clarified Ted's user experience: ShiftNotes should produce one or two high-priority briefing emails that help him understand what matters without manually reading every JotForm email.
- Clarified that Ted only needs to open original JotForm emails when he wants to inspect the evidence behind a claim.
- Added missing-report detection as a required architecture feature because shift leads may forget to submit JotForm notes for a kiosk on a given day.
- Clarified that weekly and monthly summaries should flag missing kiosk/day submissions so Ted understands reporting completeness before trusting trends.
- Started organizing class deliverables and pre-implementation requirements before writing new implementation code.
- Identified known deliverables from Week 8 and locally documented Week 9 notes, while marking final paper requirements as needing rubric confirmation.
- Created the independent backlog for the workplace-focused version of ShiftNotes.
- Organized the backlog into epics covering scope, data, ingestion, cleaning, analysis, traceability, HITL, briefings, UX, testing, and final paper documentation.
- Defined minimum viable final prototype tasks and recommended build order.
- Added the actual Week 9, Week 10, and final submission requirements to the planning documents.
- Revised the backlog so it traces directly to required deliverables: final codebase, README, CLAUDE.md, 10-page report, live demo, HITL checkpoint, failure/recovery path, reproducibility, model rationale, RAG/reasoning design, and responsible AI analysis.
- Decided that Gmail/JotForm email ingestion should be the primary ingestion path because the goal is to solve Ted's real workflow, not only simulate it.
- Clarified that local sample email fixtures can exist for reproducibility and grading, but they should not replace Gmail as the main product direction.
- Revised the ingestion decision after confirming that JotForm API access would provide cleaner structured data than Gmail parsing.
- Decided that JotForm API should be the primary ingestion path, with Gmail used for briefing delivery rather than data extraction.
- Identified the next technical milestone: consistently fetch JotForm API submissions and normalize them into clean ShiftNotes report records.
- Scaffolded the first final-project implementation step: JotForm API fetch, submission normalization, validation, local JSON output, environment template, and normalizer tests.

Planning notes:

- Keep the original documentation as the product vision baseline.
- Preserve the team/GitHub implementation as evidence of prototype exploration.
- Avoid modifying the team prototype directly until the independent project direction is defined.
- Consider creating a separate final-project implementation folder or branch after the backlog is written.
- Before building with Spec Kit or another implementation workflow, define the independent project scope in plain language.
- Consider expanding the dataset to three or six months of reports to better prove cost-saving and RAG-style trend discovery at scale.
- Frame labor efficiency carefully as better allocation and operational planning, not simply reducing hours.
- Define the ingestion strategy before implementation: CSV export, Gmail/email parsing, JotForm API, or a hybrid prototype path.
- Prioritize Gmail/email parsing as the target workflow because it best matches Ted's current process.
- Treat original JotForm emails as audit records that should be preserved, not replaced.
- Require source traceability for trend claims before trusting generated summaries.
- Track expected kiosk reporting days against received JotForm emails so missing notes are visible.
- Confirm the actual class rubric before finalizing deliverables.
- Create a formal independent backlog before implementation.
- Define acceptance criteria for the independent prototype before building.
- Use `INDEPENDENT_BACKLOG.md` as the primary planning document before implementation begins.
- Resolve P0 decisions before starting code: deliverables, implementation structure, dataset strategy, ingestion format, and source traceability format.
- Treat `INDEPENDENT_BACKLOG.md` as the final-project backlog, not only a Week 9 backlog.
- Build toward Week 10 final delivery and final submission due June 26, 2026.
- Validate Gmail access and credential strategy early because it is now on the critical path.
- Validate JotForm API access, form ID, and API key early because ingestion is now the critical path.
- Before expanding to analysis, validate that `final_project/.env` can fetch real JotForm submissions and produce stable clean records.

### Week 10

Status: pending.

Changes:

- Pending.

### Week 11

Status: pending.

Changes:

- Pending.

## Decision Log

Use this section for major project-direction decisions.

Some decisions below emerged before they were written down. The "Decision period" column records when the thinking emerged; the "Logged" column records when it was documented in this file.

| Decision period | Logged | Decision | Reason | Impact |
| --- | --- | --- | --- | --- |
| Week 9 | 2026-06-12 | Treat Week 8 as the team checkpoint and Week 9+ as independent work. | The project direction shifted from shared class collaboration to a workplace-specific operational tool. | Future documentation should distinguish team artifacts from independent work. |
| Week 9 | 2026-06-12 | Preserve the team implementation as a prototype artifact instead of editing it immediately. | The team version contains useful work, but it may not match the workplace-specific problem closely enough to become the final implementation as-is. | Next steps should focus on review, scope definition, and backlog creation before implementation changes. |
| Week 9 | 2026-06-12 | Do documentation and planning before starting a Spec Kit implementation flow. | The independent version needs a clear target before generating or refactoring code. | The project should define what problem is being solved, what evidence matters, and what features belong in the final version before implementation begins. |
| Week 9 | 2026-06-12 | Treat the current mock dataset as a starting point, not final evidence. | The data structure matches the operational form, but the content is too heavily centered on poke requests and needs broader guest, food, staffing, waste, and operational variation. | Dataset review and revision should happen before relying on it for final conclusions. |
| Week 9 | 2026-06-12 | Treat JotForm email ingestion as a separate architecture problem. | The real workflow produces individual form emails, not automatically clean CSV rows. | The final design needs an ingestion layer that extracts fields from email text and validates them before analysis. |
| Week 9 | 2026-06-12 | Prioritize Gmail/email parsing as the target ingestion workflow. | Ted already receives JotForm reports as individual emails, so the least disruptive solution should work with that existing process. | The final architecture should preserve original emails, parse them into structured data, and optionally organize them by kiosk labels/folders. |
| Week 9 | 2026-06-12 | Make weekly and monthly briefings the primary output instead of daily briefings. | The value of ShiftNotes is identifying trends over time, and daily reports may not contain enough evidence to justify a briefing. | The final project should explain this reasoning and design outputs around weekly and monthly operational intelligence. |
| Week 9 | 2026-06-12 | Require source-backed operational claims. | Ted needs to verify that the system's claims are accurate, especially for trends and personnel-related notes. | Briefings should include references to the original JotForm reports behind each important claim. |
| Week 9 / Week 10 planning | 2026-06-13 | Frame ShiftNotes as priority briefing emails over Ted's existing JotForm archive. | Ted should not have to manually read every report to understand operational patterns, but he should still be able to inspect originals when needed. | The product experience should center on weekly/monthly briefing emails with links or references back to source reports. |
| Week 9 / Week 10 planning | 2026-06-13 | Add missing-report detection to the architecture. | Missing JotForm submissions are operationally important and affect the reliability of trend analysis. | The system should compare expected kiosk/day reports against received emails and flag gaps in weekly/monthly briefings. |
| Week 10 planning | 2026-06-13 | Pause implementation until deliverables, backlog, and acceptance criteria are clear. | The project has enough direction to build, but the final implementation should be aligned to class requirements and the independent workplace-specific scope. | Next work should produce a backlog and confirm deliverables before starting Spec Kit or code changes. |
| Week 10 planning | 2026-06-15 | Create the independent backlog before implementation. | The project needs a structured work plan that translates the product direction into buildable tasks. | `INDEPENDENT_BACKLOG.md` becomes the bridge between planning and implementation. |
| Week 10 planning | 2026-06-15 | Align the independent backlog to Week 9, Week 10, and final submission requirements. | The backlog should represent the actual final project path, not just an internal planning list. | Backlog tasks now trace to codebase, report, demo, HITL, failure/recovery, reproducibility, responsible AI, and model/rationale deliverables. |
| Week 10 planning | 2026-06-16 | Make Gmail/JotForm email ingestion the primary implementation path. | The project is intended to solve Ted's real workflow, where shift notes arrive as individual JotForm emails in Gmail. | Gmail access, email parsing, source preservation, and a fallback fixture path become core implementation concerns. |
| Week 10 planning | 2026-06-16 | Make JotForm API ingestion the primary implementation path. | JotForm is the source system and API submissions are cleaner than parsing email HTML. | ShiftNotes should fetch structured submissions from JotForm, normalize them, and use Gmail only for briefing delivery. |
| Week 10 implementation | 2026-06-16 | Scaffold JotForm API ingestion proof. | The project needs to prove that JotForm submissions can become clean ShiftNotes records before analysis, briefings, or dashboards. | Added initial final-project ingestion modules, `.env` template, CLI fetch command, storage helpers, and tests. |
| Week 10 implementation | 2026-06-16 | Add the first weekly analysis and briefing layer. | After JotForm API ingestion produced clean records, the next proof point was showing that reports can become source-backed operational claims. | Added deterministic metrics, local semantic signal extraction, missing-report flagging, weekly briefing generation, date normalization, and tests. |
| Week 10 implementation / Week 6 checkpoint completion | 2026-06-20 | Wrap the independent ShiftNotes pipeline in a persistent LangGraph workflow. | The final system and Week 6 assignment require stateful orchestration, conditional routing, retry/fallback behavior, and human approval before a high-impact action. | Added demo/live ingestion modes, planner/tool/evaluator responsibilities, SQLite checkpoints, correction routing, HITL interrupt, execution evidence, architecture documentation, and orchestration tests. |
| Week 10 implementation | 2026-06-21 | Create the final 12-week synthetic benchmark dataset. | Weekly/monthly analysis, missing-report detection, source traceability, and model benchmarking require more realistic multi-kiosk data with known expected outcomes. | Added a deterministic generator, 288-slot expected schedule, 273 JotForm-shaped payload submissions, 18 missing reports, malformed and duplicate cases, separate ground truth, design rationale, validation artifacts, and dataset tests. |
| Week 10 implementation | 2026-06-21 | Add the schedule-aware deterministic baseline analysis. | The expanded dataset requires cleaning and benchmarking before AI-assisted semantic analysis can be evaluated responsibly. | Added duplicate fingerprints, malformed-record exclusion, exact kiosk/date missing detection, weekly/monthly summaries, waste and quantity findings, source-level precision/recall benchmarks, baseline artifacts, briefing output, CLI support, and tests. |
| Week 10 implementation | 2026-06-21 | Define and generate the final weekly and monthly briefing formats. | Ted needs a kiosk-centered weekly view and a broader monthly cost and trend view rather than a technical benchmark dump. | Added 12 weekly and three monthly briefings, week/month comparisons, per-report waste rates, reporting exceptions, source references, cost and productivity guardrails, rotating-menu limitations, sensitive-personnel safeguards, documentation, CLI generation, and tests. |
| Week 10 implementation | 2026-06-22 | Build the email-first product workspace and post-delivery correction loop. | Ted should receive briefings passively and use the application only to inspect or challenge claims after delivery. | Added responsive HTML/plain-text email previews, claim/source records, source inspection, natural-language mock challenges, safety refusals, a persistent LangGraph confirmation checkpoint, correction history, Pacific schedule policy, and a production-ready Streamlit workspace based on the preserved team dashboard. |
| Week 10 implementation | 2026-06-22 | Add Groq as the semantic extraction provider. | The most important report fields require semantic interpretation, but exact operational calculations should remain deterministic and auditable. | Added separate Groq configuration, strict structured extraction, exact-evidence and source-ID validation, retry and fallback behavior, content-based caching, token/latency observability, source-level benchmark metrics, CLI support, tests, and model-selection documentation. Later live validation confirmed the integration works, with quota limits documented as a production constraint. |
| Week 10 validation | 2026-06-22 | Validate Groq semantic extraction against six synthetic source reports. | The semantic layer needed live evidence for schema reliability, source traceability, model quality, failure recovery, latency, and cost. | Initial multi-report generation exposed malformed outer JSON and successfully exercised deterministic fallback. The production default was changed to one report per request, fallback citations were corrected, the prompt was versioned in cache keys, and category guidance was refined. The final six-report rerun completed with zero retries, zero fallback, 100% source-level micro precision/recall on the planted targets, 10,613 tokens, 30.2595 seconds measured latency, and an estimated cost of $0.002070. Full-dataset benchmarking remains pending. |
| Week 10 validation | 2026-06-23 | Expand Groq validation to 24 synthetic source reports. | The first live test proved the integration worked, but the final project needs evidence that semantic extraction remains stable across more varied reports. | The 24-report run completed with 21 cache hits, three new Groq request batches, one recoverable rate-limit retry, zero fallback batches, 5,628 billed tokens for the run, 38.8826 seconds measured latency, an estimated cost of $0.001132, and 100% source-level micro precision/recall on planted patterns present in the run scope. This provides stronger benchmark evidence while still leaving the complete-dataset run as the next validation step. |
| Week 10 validation / implementation | 2026-06-23 | Run the full semantic benchmark and connect AI signals into briefings. | The final prototype needed evidence beyond the 24-report validation and the weekly/monthly outputs needed to use the semantic extraction artifact instead of remaining deterministic-only. | The full run processed 270 reports with 24 cache hits, 278 retries, 136 fallback batches, 194,646 successful-call tokens, 92.17% source-level micro precision, and 97.45% source-level micro recall. The run exhausted Groq's on-demand daily token limit, so it is documented as a mixed AI/fallback artifact rather than a pure full-dataset Groq benchmark. Added semantic-event conversion, AI-backed briefing generation, AI-backed claim catalog generation, provider metadata for future extraction artifacts, cleaner trend grouping, regenerated 12 weekly briefings, three monthly briefings, 399 source-backed claims, and 15 email previews. |
| Week 10 implementation | 2026-06-23 | Polish the email-first workflow as the primary product interface. | The dashboard is only a support surface; Ted's main experience should be a useful briefing email that reduces the need to manually read shift notes. | Updated email preview ranking so repeated source-backed trends drive the priority cards, hid vague catch-all issues from the top priority list when stronger claims exist, preserved label capitalization for names and menu items, displayed source IDs directly in HTML cards, replaced long plain-text dumps with concise plain-text email alternatives, regenerated all 15 email previews, and verified the test suite still passes. |

## Open Questions

- Which team implementation files should be adopted into my independent version?
- Which documents need to be rewritten to match my current direction?
- Should the independent version keep the LangGraph/RAG approach, or stay notebook-first until the value is proven?
- What evidence is needed to show the prototype solves a real operational issue at work?
- Does the mock dataset reflect the structure, wording, and ambiguity of real shift reports closely enough to be useful?
- Is the dashboard experience useful for Ted, or should the final version focus more on passive weekly summaries?
- Should the final independent implementation live in a separate folder, a separate branch, or a separate repository?
- Can Gmail labels/folders be used to preserve Ted's current organization while reducing manual filing?
- What is the simplest reliable way to parse individual JotForm emails into structured records?
- How should source links or source references be represented in the prototype?
- What is the correct expected reporting schedule for each kiosk?
- Should missing report alerts appear only in weekly/monthly briefings, or should Ted also get a separate reminder?
- What are the exact final paper and final submission requirements?
- What implementation evidence does the class require?
