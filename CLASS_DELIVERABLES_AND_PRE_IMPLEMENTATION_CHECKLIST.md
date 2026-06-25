# Class Deliverables and Pre-Implementation Checklist

## Purpose

This document captures what is currently known about class deliverables and what should be clarified before implementation begins.

It separates confirmed or locally documented requirements from assumptions that still need to be checked against the class rubric, syllabus, or instructor guidance.

## Known Deliverables From Class Requirements

### Week 8: Final Project Prototype Kickoff

Known Week 8 requirements:

- Finalized `SPEC.md`
- Architecture diagram
- Environment setup notes
  - `uv`
  - `CLAUDE.md`
  - MCP notes
  - CI notes
- Prototype demo evidence
  - video
  - screenshot
  - logs
- Risk register with planned Week 9 mitigation actions

Week 8 scoring emphasis:

- Architecture clarity and readiness
- Technical quality of implementation kickoff
- Evidence of HITL and observability design
- Team execution discipline and traceability

### Week 9: QA / Progress Checkpoint

Due: Sunday, June 14, 2026 at 11:59 PM.

Required artifacts:

- Peer review feedback received
- Response actions to peer review
- HITL validation evidence with a non-team user
- Backlog completion report targeting 80% or more of planned work
- Technical report draft covering sections 1 through 3

Week 9 scoring emphasis:

- Quality and usefulness of review feedback integration
- Rigor of HITL validation process
- Project readiness for Week 10 final demo
- Clarity and depth of technical report draft

Week 9 milestones:

- Cross-team code review session completed
- HITL checkpoint validation with non-team user
- Backlog progress reaches at least 80%
- Technical report draft sections 1-3 submitted for feedback

Week 9 code review scope:

- Architecture coherence and requirement traceability
- Error handling, fallback behavior, and logging quality
- Test coverage and reproducibility of setup
- Security and responsible AI safeguards

Week 9 HITL validation checklist:

- Demonstrate at least one interrupt before high-impact action
- Capture user decision path, approve or deny, and downstream behavior
- Log decisions for auditability and debugging
- Test at least one refusal or unsafe-request scenario

Week 9 report draft sections:

1. Problem statement and business context
2. Architecture and framework rationale
3. Implementation progress and validation evidence

### Week 10: Final Presentation and Demo

Theme: final project completion, live demo, and technical report submission.

Format:

- 15-minute live demo and presentation
- 5-minute Q&A
- All team members participate where applicable

Required demo elements:

- End-to-end system run with realistic input
- One HITL checkpoint in action
- One failure mode and recovery demonstration
- Brief walkthrough of architecture and key design choices

Week 10 outcomes:

- Demonstrate an end-to-end agentic system with real inputs
- Present architecture and model-selection rationale clearly
- Show HITL behavior and failure/recovery path in live workflow
- Submit complete technical documentation for evaluation

Evaluation focus:

- Technical correctness and reliability
- Architecture clarity and tradeoff justification
- Responsible AI design and safeguards
- Team communication and professionalism

### Final Submission: Codebase and Technical Report

Due: Friday, June 26, 2026 at 11:59 PM.

Submit one final package as a repository link or ZIP containing production-ready artifacts.

Required deliverables:

- Codebase: documented, test-covered, reproducible environment
- `README.md`: setup, run steps, architecture summary
- `CLAUDE.md`: project guidance and workflow context
- 10-page technical report

Required technical report sections:

- Problem statement and business justification
- Architecture decisions and framework rationale
- Model selection and benchmark evidence
- RAG or reasoning pipeline design
- Responsible AI analysis, risks, and mitigations
- Lessons learned and future work

Final checks before submission:

- Reproducibility verified on a clean environment
- Demo path documented and tested
- Known limitations clearly listed

## Deliverables Already Known Versus Still Unclear

Known:

- Week 9 checkpoint artifacts
- Week 10 live demo elements
- Final codebase requirements
- Final `README.md` and `CLAUDE.md` requirements
- Final 10-page technical report required sections
- Clean-environment reproducibility requirement
- Demo path documentation requirement
- Known limitations requirement

Still unclear or worth confirming:

- Whether screenshots count toward the 10-page technical report
- Whether final submission should be a repo link, ZIP, or both
- Whether the missed Week 9 checkpoint should still be submitted late
- Whether the independent project is being evaluated individually or still under team-presentation expectations
- Whether live Gmail/MCP integration is expected, or whether a realistic simulated input path is acceptable
- Whether CI is required specifically, or whether documented test commands are enough

## What Is Needed Before Implementation

### 1. Final Scope Statement

Write a one-paragraph statement of what the independent final project will build.

Current likely version:

```text
ShiftNotes is a workplace-focused operational intelligence prototype that parses JotForm-style shift-note reports, preserves source traceability, identifies trends across kiosks, detects missing reports, and generates weekly/monthly briefings for Ted to review.
```

### 2. Ingestion Decision

Decide what the implementation will actually support for the final submission.

Options:

- Mock JotForm email files
- Exported CSV
- Gmail parsing prototype
- JotForm API
- Hybrid: simulated email parsing now, real Gmail/JotForm integration as future work

Current decision:

Use JotForm API ingestion as the primary implementation direction because it provides cleaner structured form submission data.

Use Gmail or SMTP for briefing delivery.

Include saved API responses or local fixtures as a fallback for reproducibility, tests, and grading in environments where JotForm credentials are unavailable.

### 3. Dataset Plan

Decide whether to:

- keep the team dataset as prototype evidence
- expand it
- replace it with a new independent dataset

Needed dataset decisions:

- number of months represented
- number of kiosks
- expected reporting schedule
- guest feedback categories
- food concern categories
- operational issue categories
- recognition patterns
- missing-report patterns
- source IDs for traceability

### 4. Source Traceability Design

Define how claims connect back to original reports.

Every generated claim should include:

- claim text
- metric or count
- matching report IDs
- kiosk
- date
- source excerpt or source link

This is central to the product.

### 5. HITL Checkpoints

Define the human review points before coding them.

Potential checkpoints:

- Review parsed email fields when extraction confidence is low
- Review missing-report flags
- Review weekly briefing claims
- Review sensitive personnel-related claims
- Correct incorrect AI interpretations
- Approve or reject summary output

### 6. Briefing Format

Define the output shape before building.

Weekly briefing should include:

- reporting completeness
- kiosk-by-kiosk summary
- food quality and quantity trends
- guest feedback trends
- food concerns and outages
- operational issues
- waste/unclaimed lunch patterns
- recognition highlights
- source-backed claims

Monthly briefing should include:

- broader trend changes
- recurring issues
- cost-saving opportunities
- guest demand signals
- operational reliability patterns
- labor/workflow observations

### 7. Backlog

Create the actual independent backlog before implementation.

Backlog sections should include:

- Documentation
- Data and mock report generation
- Email parsing / ingestion
- Cleaning and validation
- Trend analysis
- Briefing generation
- Source traceability
- HITL review
- Testing
- Demo evidence
- Final paper

### 8. Acceptance Criteria

Define how to know the prototype works.

Example acceptance criteria:

- Parses all required fields from mock JotForm-style reports
- Flags missing kiosk/day reports
- Produces weekly and monthly briefings
- Identifies at least five operational trend categories
- Links every major claim to source report IDs
- Allows human correction of incorrect claims
- Produces evidence suitable for the final paper

## Recommended Immediate Next Steps

1. Decide the final implementation folder or branch strategy.
2. Define the JotForm API access and credential strategy.
3. Define the exact weekly and monthly briefing formats.
4. Define the source-reference format.
5. Define the HITL validation scenario for the demo.
6. Define the failure mode and recovery path for the demo.
7. Create the final paper outline using the required sections.
8. Begin implementation once the above decisions are stable.

## Current Recommendation

Implementation can begin after the P0 scope decisions are resolved.

The next best step is to convert the independent backlog into a Week 10 execution plan, with JotForm API ingestion treated as the primary path and saved API responses or fixtures treated as the reproducibility fallback.
