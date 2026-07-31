# Independent Backlog

## Purpose

This backlog defines the work for the final independent version of ShiftNotes after the Week 8 team checkpoint.

The goal is to build a workplace-focused operational intelligence prototype that works with Ted's real reporting workflow, preserves original JotForm emails as source records, and generates source-backed weekly and monthly briefings.

This is the actual final-project backlog. It is not only a Week 9 checkpoint backlog.

It must support:

- Week 9 QA checkpoint artifacts
- Week 10 final presentation and live demo
- Final codebase submission
- 10-page technical report

## Backlog Principles

- Preserve the original JotForm email archive.
- Reduce Ted's manual report-reading burden.
- Treat the team implementation as prototype evidence, not the final system.
- Build around source-backed claims.
- Keep human review as a core part of the workflow.
- Prefer a clean, explainable prototype over an overbuilt system.
- Document major decisions in `SOLO_WORK_LOG.md`.

## Class Requirement Traceability

### Week 9 Checkpoint Requirements

| Requirement | Backlog Coverage |
| --- | --- |
| Peer review feedback received and response actions | DOC-07, SCOPE-04 |
| HITL validation evidence with non-team user | HITL-04, TEST-06 |
| Backlog completion report targeting 80%+ | DOC-09 |
| Technical report draft sections 1-3 | DOC-06, REPORT-01, REPORT-02, REPORT-03 |

### Week 10 Demo Requirements

| Requirement | Backlog Coverage |
| --- | --- |
| End-to-end system run with realistic input | DEMO-01, INGEST-06, BRIEF-03 |
| One HITL checkpoint in action | DEMO-02, HITL-02, HITL-03 |
| One failure mode and recovery demonstration | DEMO-03, CLEAN-02, HITL-02 |
| Architecture and key design walkthrough | DEMO-04, DOC-08, REPORT-02 |

### Final Submission Requirements

| Requirement | Backlog Coverage |
| --- | --- |
| Documented, test-covered codebase | TEST-01 through TEST-06, DOC-08 |
| Reproducible environment | ENV-01, ENV-02, ENV-03 |
| `README.md` with setup, run steps, architecture summary | DOC-08 |
| `CLAUDE.md` with project guidance and workflow context | DOC-09 |
| 10-page technical report | REPORT-01 through REPORT-06 |
| Model selection and benchmark evidence | MODEL-01, MODEL-02 |
| RAG or reasoning pipeline design | ANALYSIS-09, REPORT-04 |
| Responsible AI risks and mitigations | RAI-01, RAI-02, REPORT-05 |
| Demo path documented and tested | DEMO-01, DEMO-05 |
| Known limitations listed | DOC-10, REPORT-06 |

## Priority Levels

| Priority | Meaning |
| --- | --- |
| P0 | Required for final prototype credibility |
| P1 | Important if time allows |
| P2 | Useful future improvement |

## Status Labels

| Status | Meaning |
| --- | --- |
| Not Started | No implementation or final documentation yet |
| In Progress | Actively being worked on |
| Blocked | Needs information, access, or a decision |
| Done | Complete enough for the current prototype |
| Deferred | Intentionally moved to future work |

## Epic 1: Project Scope and Submission Alignment

| ID | Priority | Status | Task | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| SCOPE-01 | P0 | In Progress | Define the independent project scope. | A one-paragraph final scope statement exists and clearly separates the independent project from the team prototype. |
| SCOPE-02 | P0 | Done | Confirm final class deliverables. | Week 9, Week 10, and final submission requirements are documented in `CLASS_DELIVERABLES_AND_PRE_IMPLEMENTATION_CHECKLIST.md`. |
| SCOPE-03 | P0 | Not Started | Decide final implementation location. | Project structure is chosen: separate folder, separate branch, or separate repository. |
| SCOPE-04 | P0 | Not Started | Decide what counts as final implementation versus prototype artifact. | Team implementation files are categorized as adopt, revise, preserve, or ignore. |
| SCOPE-05 | P0 | Not Started | Create final paper outline. | 10-page paper outline maps project docs to required report sections. |
| SCOPE-06 | P0 | Not Started | Decide Week 9 late-submission strategy. | Decision made whether to submit Week 9 artifacts late or fold them into final documentation. |

## Epic 2: Data and Dataset Design

| ID | Priority | Status | Task | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| DATA-01 | P0 | Completed | Review team mock dataset. | Dataset strengths and concerns are documented in `DATASET_REVIEW_NOTES.md`. |
| DATA-02 | P0 | Completed | Decide final dataset strategy. | Decision made: keep, expand, replace, or hybridize the existing mock dataset. |
| DATA-03 | P0 | Completed | Define expected reporting schedule. | Expected kiosk/day report schedule is documented for missing-report detection. |
| DATA-04 | P0 | Completed | Design source report IDs. | Every mock or parsed report has a stable ID that can be referenced from claims. |
| DATA-05 | P0 | Completed | Expand guest feedback variety. | Dataset includes requests, complaints, praise, service issues, menu questions, dietary questions, and repeated non-poke themes. |
| DATA-06 | P0 | Completed | Add missing-report examples. | Dataset includes intentional missing kiosk/day submissions for testing completeness checks. |
| DATA-07 | P1 | Completed | Expand dataset to three or six months. | Dataset covers enough time to show weekly/monthly trends and larger-scale cost patterns. |
| DATA-08 | P1 | Completed | Add labor/workflow signals. | Dataset includes rush periods, staffing friction, line slowdowns, recovery notes, and workflow observations. |

## Epic 3: Ingestion and Email Parsing

| ID | Priority | Status | Task | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| INGEST-01 | P0 | In Progress | Define target ingestion workflow. | `INGESTION_WORKFLOW_NOTES.md` documents JotForm API ingestion as the preferred workflow. |
| INGEST-02 | P0 | Done | Choose prototype ingestion format. | JotForm API is the primary target; saved API responses or fixtures may be used only as a reproducibility fallback. |
| INGEST-03 | P0 | Not Started | Define required parsed fields. | Required field list exists for clean structured report records. |
| INGEST-04 | P0 | Not Started | Design validation rules. | Missing/invalid date, kiosk, lead, ratings, text fields, duplicates, and unclaimed lunches are handled. |
| INGEST-05 | P0 | Not Started | Design source preservation model. | Every clean record can trace back to original JotForm submission ID and source payload. |
| INGEST-06 | P0 | Not Started | Implement JotForm API fetch. | System can retrieve submissions for the target form using an API key and form ID. |
| INGEST-07 | P0 | Not Started | Normalize JotForm API submissions. | API response is converted into stable ShiftNotes report records. |
| INGEST-08 | P1 | Not Started | Add saved API response fallback. | Fixture files allow reproducible tests and demo runs without live JotForm credentials. |
| INGEST-09 | P1 | Not Started | Design Gmail briefing delivery. | System can send or draft weekly/monthly briefing emails. |
| INGEST-10 | P2 | Deferred | Evaluate Gmail parsing fallback. | Gmail parsing is documented as a fallback if JotForm API access is unavailable. |
| INGEST-09 | P2 | Deferred | Evaluate JotForm API. | JotForm API is assessed as a possible production ingestion path. |

## Epic 4: Cleaning, Validation, and Missing Reports

| ID | Priority | Status | Task | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| CLEAN-01 | P0 | Completed | Normalize parsed reports. | Dates, kiosks, ratings, text fields, and numeric fields are consistently formatted. |
| CLEAN-02 | P0 | Completed | Validate report completeness. | Invalid or incomplete reports are flagged instead of silently analyzed. |
| CLEAN-03 | P0 | Completed | Detect missing reports. | System compares expected kiosk/day reports against received reports. |
| CLEAN-04 | P0 | Completed | Include reporting completeness in briefings. | Weekly/monthly briefings clearly list missing kiosk/day reports. |
| CLEAN-05 | P1 | Completed | Detect duplicate reports. | Duplicate emails or repeated report IDs are flagged. |
| CLEAN-06 | P1 | Completed | Log cleaning and validation outcomes. | Counts of loaded, valid, invalid, duplicate, and missing reports are visible. |

## Epic 5: Trend Analysis and Insight Generation

| ID | Priority | Status | Task | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| ANALYSIS-01 | P0 | Completed | Define trend categories. | Food quality, food quantity, food concerns, guest issues, operational notes, recognition, waste, and missing reports are included. |
| ANALYSIS-02 | P0 | Completed | Calculate weekly kiosk summaries. | Each kiosk has weekly metrics and notable signals. |
| ANALYSIS-03 | P0 | Completed | Calculate monthly kiosk summaries. | Each kiosk has monthly metrics and recurring patterns. |
| ANALYSIS-04 | P0 | Completed | Detect cross-kiosk trends. | Briefings can identify patterns across all kiosks. |
| ANALYSIS-05 | P0 | Completed | Identify guest feedback themes. | Repeated guest issues or requests are grouped beyond a single poke example. |
| ANALYSIS-06 | P0 | Completed | Analyze waste and unclaimed lunches. | Highest waste kiosk, changes over time, and possible cost signals are identified. |
| ANALYSIS-07 | P1 | Not Started | Analyze labor/workflow observations. | Reports surface staffing friction, rush periods, and workflow bottlenecks when present. |
| ANALYSIS-08 | P1 | Not Started | Compare best/worst rating days. | System highlights notable high or low food quality/quantity days and source reports. |
| ANALYSIS-09 | P0 | Not Started | Document RAG or reasoning pipeline design. | Final report and README explain whether the system uses RAG, deterministic reasoning, LLM reasoning, or a hybrid. |

## Epic 6: Source Traceability

| ID | Priority | Status | Task | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| TRACE-01 | P0 | In Progress | Define source-backed claim requirement. | Documentation states that meaningful claims need source report references. |
| TRACE-02 | P0 | Completed | Design claim data model. | Each claim stores text, count/metric, category, kiosk, date range, source report IDs, and excerpts. |
| TRACE-03 | P0 | Completed | Link trend claims to source reports. | Claims like "poke requested 16 times" include all matching report IDs or excerpts. |
| TRACE-04 | P0 | Completed | Link sensitive claims to source reports. | Personnel-related claims include source support and require human review. |
| TRACE-05 | P1 | Completed | Design source-view output. | Prototype shows source references in a readable way, even if not clickable yet. |
| TRACE-06 | P2 | Deferred | Implement clickable source links. | Briefings link directly to source email, source file, or source record when possible. |

## Epic 7: Human-in-the-Loop Review

| ID | Priority | Status | Task | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| HITL-01 | P0 | Completed | Define HITL as a general checkpoint pattern. | Documentation shows HITL applies to food, guest, waste, missing-report, operational, recognition, and complaint claims. |
| HITL-02 | P0 | Completed | Define correction workflow. | Ted can mark a claim as wrong and provide correction notes. |
| HITL-03 | P0 | Completed | Define review checkpoints. | Checkpoints are identified for parsing uncertainty, missing reports, sensitive claims, and briefing review. |
| HITL-04 | P1 | Not Started | Capture HITL validation evidence. | A non-team user reviews output and feedback is documented if required by class. |
| HITL-05 | P1 | Completed | Preserve correction history. | Corrections are stored or documented for auditability. |

## Epic 8: Briefing Output

| ID | Priority | Status | Task | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| BRIEF-01 | P0 | Completed | Define weekly briefing format. | Weekly briefing has sections for reporting completeness, kiosk summaries, trends, and source-backed claims. |
| BRIEF-02 | P0 | Completed | Define monthly briefing format. | Monthly briefing has broader trend, cost, demand, and operational summaries. |
| BRIEF-03 | P0 | Completed | Generate weekly briefing prototype. | Prototype produces a readable weekly operations briefing from sample data. |
| BRIEF-04 | P0 | Completed | Generate monthly briefing prototype. | Prototype produces a readable monthly operations briefing from sample data. |
| BRIEF-05 | P0 | Completed | Include source references in briefings. | Every major claim includes report IDs or excerpts. |
| BRIEF-06 | P1 | Completed | Design briefing email layout. | Briefing can be represented as an email Ted would plausibly prioritize. |
| BRIEF-07 | P2 | Deferred | Send briefing email automatically. | Email delivery works or is documented as future production work. |

## Epic 9: Interface and User Experience

| ID | Priority | Status | Task | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| UX-01 | P0 | Completed | Decide whether final prototype needs a dashboard. | Dashboard is either included, simplified, or deferred based on Ted's actual workflow. |
| UX-02 | P0 | Completed | Prioritize passive briefing experience. | Final user experience centers on weekly/monthly priority briefings. |
| UX-03 | P1 | Completed | Design source inspection view. | Ted can inspect evidence behind claims in a simple view or report section. |
| UX-04 | P1 | Completed | Decide whether to reuse team Streamlit dashboard. | Team dashboard is categorized as adopt, revise, or preserve as artifact. |
| UX-05 | P2 | Completed | Build interactive dashboard. | Dashboard exists only if it directly supports source inspection or demo needs. |

## Epic 10: Testing and Validation

| ID | Priority | Status | Task | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| TEST-01 | P0 | Completed | Test parsing behavior. | Parser tests cover expected JotForm-style report fields. |
| TEST-02 | P0 | Completed | Test missing-report detection. | Tests prove missing kiosk/day reports are flagged. |
| TEST-03 | P0 | Completed | Test trend counts. | Known planted patterns produce expected counts. |
| TEST-04 | P0 | Completed | Test source traceability. | Generated claims include expected source report IDs. |
| TEST-05 | P1 | Completed | Test briefing output shape. | Briefings contain required sections. |
| TEST-06 | P1 | Completed | Test HITL correction model. | Incorrect claim can be marked wrong and correction can be recorded. |
| TEST-07 | P0 | Completed | Capture demo evidence. | Screenshots, logs, or notebook outputs show the prototype working. |

## Epic 11: Environment and Reproducibility

| ID | Priority | Status | Task | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| ENV-01 | P0 | Completed | Define reproducible environment. | Dependencies and Python version are documented in `pyproject.toml`, lockfile, or equivalent setup notes. |
| ENV-02 | P0 | In Progress | Verify clean environment setup. | A fresh setup can install dependencies and run the demo path. |
| ENV-03 | P0 | Completed | Document setup and run commands. | README includes install, test, and demo commands. |
| ENV-04 | P1 | Not Started | Add or update CI. | Automated tests run in a reproducible environment if time allows. |

## Epic 12: Model Selection, Benchmarks, and Responsible AI

| ID | Priority | Status | Task | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| MODEL-01 | P0 | Completed | Decide model/reasoning approach. | Selected a hybrid architecture: deterministic Python metrics plus Groq semantic extraction with strict source evidence. |
| MODEL-02 | P0 | Completed | Produce benchmark evidence. | Benchmark code, source-level metrics, clean 6-report and 24-report Groq validations, and a full-dataset mixed AI/fallback run are documented; a pure full-dataset Groq run is a production quota/batching improvement. |
| MODEL-03 | P1 | Not Started | Evaluate team classifier approach. | Team classifier is assessed for reuse, revision, or rejection. |
| RAI-01 | P0 | Completed | Document responsible AI risks. | Risks include false claims, personnel sensitivity, missing reports, privacy, and overtrust. |
| RAI-02 | P0 | Completed | Document mitigations. | Mitigations include source citations, HITL correction, limitations, and no autonomous personnel decisions. |

## Epic 13: Demo and Presentation

| ID | Priority | Status | Task | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| DEMO-01 | P0 | Completed | Define end-to-end demo path. | Demo starts with realistic input and ends with a source-backed briefing. |
| DEMO-02 | P0 | Completed | Demonstrate HITL checkpoint. | Demo includes Ted/user reviewing a claim or parsed issue and approving/correcting it. |
| DEMO-03 | P0 | Completed | Demonstrate failure mode and recovery. | Demo shows missing report, parsing issue, unsafe/sensitive claim, or incorrect claim recovery. |
| DEMO-04 | P0 | Completed | Prepare architecture walkthrough. | Presentation explains key design choices and tradeoffs. |
| DEMO-05 | P0 | Completed | Test demo path. | Demo has been run successfully before submission/presentation. |
| DEMO-06 | P1 | Not Started | Prepare Q&A notes. | Likely questions and answers are documented. |

## Epic 14: Documentation and Final Paper

| ID | Priority | Status | Task | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| DOC-01 | P0 | In Progress | Maintain solo work log. | Significant decisions and changes are recorded in `SOLO_WORK_LOG.md`. |
| DOC-02 | P0 | In Progress | Maintain team prototype review. | Team implementation remains documented as prototype evidence. |
| DOC-03 | P0 | In Progress | Maintain dataset review notes. | Dataset concerns and revisions are documented. |
| DOC-04 | P0 | In Progress | Maintain ingestion workflow notes. | Gmail/JotForm/email parsing design is documented. |
| DOC-05 | P0 | Not Started | Create final paper outline. | Paper outline maps existing docs and evidence to required final report sections. |
| DOC-06 | P0 | Not Started | Draft technical report sections 1-3. | Problem/business context, architecture/framework rationale, and implementation progress/validation evidence are drafted. |
| DOC-07 | P0 | Not Started | Capture class deliverable evidence. | Required screenshots, logs, peer review, HITL feedback, or demo materials are organized. |
| DOC-08 | P0 | Not Started | Update README for independent project. | README includes setup, run steps, architecture summary, and final independent project direction. |
| DOC-09 | P0 | Not Started | Update CLAUDE.md for final project. | CLAUDE.md explains project guidance, workflow context, and documentation expectations. |
| DOC-10 | P0 | Not Started | List known limitations. | Known limitations are documented in README and final report. |
| DOC-11 | P0 | Not Started | Create backlog completion report. | Backlog completion percentage and critical gaps are documented for Week 9/final evidence. |

## Epic 15: Technical Report Sections

| ID | Priority | Status | Task | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| REPORT-01 | P0 | Not Started | Draft problem statement and business justification. | Report explains Ted's workflow, manual reading burden, cost/operations value, and why ShiftNotes matters. |
| REPORT-02 | P0 | Not Started | Draft architecture decisions and framework rationale. | Report explains ingestion, cleaning, analysis, source traceability, HITL, and briefing architecture. |
| REPORT-03 | P0 | Not Started | Draft implementation progress and validation evidence. | Week 9-style draft covers current implementation, tests, demo evidence, and gaps. |
| REPORT-04 | P0 | Not Started | Draft model selection and RAG/reasoning pipeline section. | Report explains chosen model/reasoning approach and benchmark evidence. |
| REPORT-05 | P0 | Not Started | Draft responsible AI analysis. | Report covers risks, mitigations, HITL, privacy, false claims, and personnel sensitivity. |
| REPORT-06 | P0 | Not Started | Draft lessons learned, limitations, and future work. | Report explains what was learned, what remains incomplete, and production next steps. |

## Minimum Viable Final Prototype

The minimum credible final prototype should complete:

- SCOPE-01
- SCOPE-02
- SCOPE-03
- DATA-02
- DATA-03
- DATA-04
- DATA-05
- DATA-06
- INGEST-02
- INGEST-03
- INGEST-04
- INGEST-05
- CLEAN-01
- CLEAN-02
- CLEAN-03
- CLEAN-04
- ANALYSIS-01
- ANALYSIS-02
- ANALYSIS-03
- ANALYSIS-04
- ANALYSIS-05
- ANALYSIS-06
- TRACE-02
- TRACE-03
- TRACE-04
- HITL-02
- HITL-03
- BRIEF-01
- BRIEF-02
- BRIEF-03
- BRIEF-04
- BRIEF-05
- TEST-01
- TEST-02
- TEST-03
- TEST-04
- ENV-01
- ENV-02
- ENV-03
- MODEL-01
- MODEL-02
- RAI-01
- RAI-02
- DEMO-01
- DEMO-02
- DEMO-03
- DEMO-04
- DEMO-05
- DOC-05
- DOC-06
- DOC-08
- DOC-09
- DOC-10
- DOC-11
- REPORT-01
- REPORT-02
- REPORT-03
- REPORT-04
- REPORT-05
- REPORT-06

## Recommended Build Order

1. Choose final implementation structure.
2. Choose final dataset strategy.
3. Design JotForm API ingestion and fallback fixture path.
4. Define expected kiosk reporting schedule.
5. Define source traceability format.
6. Define weekly and monthly briefing formats.
7. Define HITL checkpoint and correction behavior.
8. Define failure mode and recovery scenario for demo.
9. Define model/reasoning approach and benchmark plan.
10. Build or revise dataset.
11. Implement parsing/cleaning path.
12. Implement missing-report detection.
13. Implement trend analysis.
14. Implement source-backed claim generation.
15. Implement briefing output.
16. Add HITL correction path.
17. Add tests.
18. Verify clean environment setup.
19. Capture demo evidence.
20. Update README and CLAUDE.md.
21. Draft final paper.

## Week 10 Execution Plan

1. Finalize scope, implementation structure, and dataset strategy.
2. Build the minimum end-to-end path with realistic input.
3. Add source-backed claims and missing-report detection.
4. Add one HITL checkpoint and one failure/recovery path.
5. Add tests and clean setup instructions.
6. Capture screenshots/logs for demo evidence.
7. Update README and CLAUDE.md.
8. Draft the 10-page technical report using required sections.
9. Rehearse the 15-minute demo.

## Current Blockers

- Final implementation location has not been chosen.
- Dataset strategy has not been finalized.
- Expected kiosk reporting schedule has not been confirmed.
- Source-reference format has not been selected.
- Pure complete-dataset Groq benchmarking requires quota-aware batching or a higher Groq service tier.
- Demo failure/recovery scenario has not been selected.
- JotForm API access and credential strategy have not been validated.

## Next Best Step

The next best step is to resolve the P0 decisions before writing code:

1. Choose final implementation structure.
2. Choose final dataset strategy.
3. Define JotForm API access and credential strategy.
4. Define source traceability format.
5. Define HITL and failure/recovery demo scenarios.
