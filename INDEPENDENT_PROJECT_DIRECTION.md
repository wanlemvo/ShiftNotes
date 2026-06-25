# Independent Project Direction

## Purpose

This document defines the planning direction for the independent version of ShiftNotes before any new implementation work begins.

The immediate goal is not to write code. The immediate goal is to define the final project clearly enough that the backlog and future implementation can follow from it.

## Current Thinking

The team prototype should remain available as a prototype artifact.

The independent final project should be shaped around the real operational issue:

Operational reports contain useful information, but leadership should not need to manually read every report to understand recurring issues, guest requests, waste patterns, employee recognition, and operational friction.

The value of ShiftNotes is turning those reports into operational intelligence.

## Final Project Candidate Framing

ShiftNotes is a workplace-focused operational intelligence prototype that transforms shift notes into weekly summaries and trend findings for human review.

The final version should prioritize:

- Realistic shift-note structure
- JotForm API ingestion as the target workflow
- Preservation of Ted's original JotForm email archive
- Missing-report detection by kiosk and expected reporting day
- Traceable insight generation
- Weekly and monthly operations summary output
- Human review before action
- Clear evidence that the prototype reduces manual review effort

The final version does not need to prove every possible future feature.

## What To Preserve

- Original product vision and problem framing
- Current-form analysis
- Mock-data design goals
- Week 8 prototype evidence
- Team prototype as exploratory evidence
- The idea of passive summaries before dashboards

## What To Reconsider

- Whether the dashboard is the primary user experience
- Whether LangGraph is necessary for the final version
- Whether RAG is needed now or should remain future work
- Whether Gmail/MCP integration is required for the final submission
- Whether the mock dataset needs to be rewritten to sound more like actual shift notes

## Likely Final Implementation Shape

The final implementation may be separate from the team prototype.

Possible structure:

```text
final_project/
    data/
    notebooks/
    src/
    reports/
    docs/
```

This would allow the team prototype to remain untouched while the independent version becomes cleaner, narrower, and easier to explain in the final paper.

## Target Product Workflow

The independent project should be designed around Ted's real workflow:

```text
Shift lead creates shift notes
    |
    v
JotForm sends report email to Ted
    |
    v
JotForm stores structured submission data
    |
    v
ShiftNotes fetches submissions from the JotForm API
    |
    v
ShiftNotes aggregates reports by week and month
    |
    v
ShiftNotes produces source-backed operational briefings
    |
    v
Ted reviews claims, checks sources, and corrects the system when needed
```

The final project should not require Ted to stop receiving the original JotForm emails, but ShiftNotes does not need to parse those emails if the JotForm API provides the structured submission data directly.

## Ingestion Decision

The final independent project should prioritize JotForm API ingestion.

The reason is simple: JotForm is the source system that creates the shift-note submissions. If ShiftNotes can access the form submissions directly through the JotForm API, it can avoid brittle email parsing and work with cleaner structured data.

The project should therefore pull from JotForm first:

```text
JotForm form
    |
    v
JotForm API submissions
    |
    v
Normalizer and validator
    |
    v
Clean structured records
```

Gmail remains important for sending Ted the final weekly and monthly briefing emails.

For reproducibility, the codebase can include saved API responses or fixture files. Those are fallback inputs for testing and grading, not the main product direction.

## Ted's Experience

The simplest way to describe the user experience is:

Ted still receives the original JotForm emails, but ShiftNotes gives him one or two higher-priority briefing emails that summarize what is actually going on.

Instead of manually reading every shift-note email to find patterns, Ted can read:

- A weekly operations briefing
- A monthly operations briefing

These briefings should tell him what changed, what repeated, what needs attention, and where the evidence came from.

Ted only needs to open the original JotForm emails when he wants to inspect or verify a claim that ShiftNotes made.

Example:

```text
ShiftNotes says:
"Poke was requested 16 times at Bowls and Buns in June."

Ted can then click into the source list and review the original JotForm reports behind that claim.
```

This keeps Ted's existing workflow intact while reducing the amount of manual reading required.

## Source-Backed Intelligence Requirement

A core requirement for the independent version is evidence-backed claims.

If the system says a pattern occurred, Ted should be able to inspect the reports that support it.

Example:

```text
Poke was requested 16 times at Bowls and Buns in June.
```

The briefing should include a way to view the matching source reports.

This requirement is especially important for:

- Guest request trends
- Food shortage trends
- Waste patterns
- Operational issue trends
- Employee recognition
- Employee complaints or sensitive personnel-related notes

## Human Review Requirement

Human review is not just a final approval button, and it is not limited to personnel-related claims.

It is a general checkpoint pattern for any place where the system might be wrong or where the consequence of being wrong matters.

Ted should be able to:

- Click into the evidence behind a claim
- Confirm that the claim is accurate
- Mark a claim as wrong
- Correct the interpretation
- Preserve that correction for future analysis

This can apply to:

- Food trends
- Guest requests
- Waste patterns
- Missing reports
- Operational issues
- Employee recognition
- Employee complaints or sensitive personnel-related notes

Examples:

- If the system says poke was requested 16 times, Ted should be able to inspect the matching reports and correct the count if needed.
- If the system says Kiosk B had the highest waste, Ted should be able to inspect the waste records behind that claim.
- If the system says there were three complaints about an employee, Ted should be able to verify whether those were actually complaints or just neutral mentions.

This matters because the system may misunderstand tone, context, counts, categories, or operational meaning.

## Missing Report Detection

ShiftNotes should not only analyze reports that were submitted. It should also notice when expected reports are missing.

This matters because shift leads may forget to submit JotForm notes for a kiosk on a given day. If the system only analyzes received emails, missing submissions become invisible.

Example weekly finding:

```text
Missing shift notes:
- Kiosk B: Tuesday
- Kiosk D: Thursday
```

This should be treated as an operational accountability and data-completeness signal.

Before generating weekly or monthly insights, ShiftNotes should compare:

- Expected kiosks
- Expected reporting days
- Received JotForm emails
- Parsed clean records

If a kiosk/day combination is missing, the briefing should flag it clearly.

This also improves trust in the analysis. If a weekly summary is based on incomplete reporting, Ted should know that before acting on the trends.

## Backlog Should Come Next

Before implementation, create a backlog that separates:

- Documentation tasks
- Data validation tasks
- Mock dataset revision tasks
- Notebook or analysis tasks
- Dashboard or summary-output tasks
- Testing tasks
- Final paper evidence tasks

The backlog should make it clear what is required for the final project and what is optional.

## Paper Evidence To Capture

The final 10-page paper can draw from:

- Original problem documentation
- Current form analysis
- Product vision
- Mock data design
- Solo work log
- Team prototype review
- Independent backlog
- Implementation decisions
- Screenshots or notebook outputs
- Final summary examples
- Known limitations and future work

Because the documentation already exists, the paper can focus on telling a clear story:

1. What operational problem exists?
2. Why existing reporting is not enough?
3. What prototype was built?
4. What changed after the team checkpoint?
5. What independent direction was chosen?
6. What evidence shows the idea works?
7. What remains future work?
