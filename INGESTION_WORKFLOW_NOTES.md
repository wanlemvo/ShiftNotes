# Ingestion Workflow Notes

## Purpose

This document captures the current thinking about how real JotForm shift-note emails could become clean data for ShiftNotes.

The key concern was originally that Ted receives individual JotForm emails. After reviewing the workflow, the better ingestion path is to treat JotForm itself as the source of truth when API access is available.

ShiftNotes should pull structured submissions from the JotForm API instead of parsing the email copy whenever possible.

## Current Real-World Workflow

The likely workflow is:

```text
Shift lead submits JotForm
    |
    v
JotForm sends formatted email
    |
    v
Ted receives individual report email
    |
    v
Report sits in inbox as human-readable text
```

This is different from the prototype dataset, which already exists as a structured CSV.

More specifically, the current human workflow appears to be:

```text
Shift lead completes shift notes
    |
    v
JotForm submission is created
    |
    v
JotForm email is sent to Ted
    |
    v
Ted manually moves the email into a kiosk-specific folder
    |
    v
Ted reads reports either during email triage, during filing, or later when he has time
```

The exact timing of Ted's review may vary. Sometimes he may read the report when it arrives. Sometimes he may read it while moving it into a folder. Sometimes he may review reports later in batches.

The system should not depend on Ted changing that habit.

## Current Ingestion Decision

Primary ingestion path:

```text
JotForm API
    |
    v
Structured form submissions
    |
    v
ShiftNotes normalization and validation
```

Gmail should be used for briefing delivery, not form-data extraction, unless JotForm API access is unavailable.

The original JotForm emails can remain available to Ted as part of his normal workflow, but ShiftNotes does not need to rely on parsing email HTML if the API can provide the submission data directly.

## Core Problem

ShiftNotes needs an ingestion layer before analysis.

That layer must convert each JotForm submission into a structured ShiftNotes report record.

Example structured record:

```text
date
kiosk
lead_name
food_quality_rating
food_quantity_rating
food_concerns_or_outages
team_members_who_did_well
guest_issues_for_the_day
operational_notes
number_of_unclaimed_lunches
source_email_id
source_received_at
```

The important point is that analysis should not run directly on raw API output. Submissions should first be normalized, validated, and stored in a consistent internal schema.

The system also should not remove or replace Ted's original email copies.

Ted should keep access to the original JotForm emails because those are the source records. ShiftNotes should make that archive easier to manage and easier to learn from.

## Target Workflow

The preferred workflow is:

```text
Shift lead submits JotForm
    |
    v
JotForm stores structured submission
    |
    v
ShiftNotes fetches submissions from JotForm API
    |
    v
ShiftNotes normalizes and validates submissions
    |
    v
ShiftNotes stores clean report records
    |
    v
ShiftNotes checks expected reports against received reports
    |
    v
ShiftNotes generates weekly and monthly operational briefings
    |
    v
Ted reviews source-backed insights and decides what to do
```

The goal is to use the cleanest available source of form data while preserving Ted's email-based experience through the final briefing output.

## Gmail Role

Gmail is no longer the primary ingestion path if JotForm API access is available.

Gmail's main role becomes:

- Delivering the weekly briefing email
- Delivering the monthly briefing email
- Optionally preserving Ted's existing JotForm notification workflow

Optional future Gmail features:

- Labeling or filing original JotForm notification emails
- Linking briefing claims back to email copies
- Sending follow-up reminders for missing reports

## Briefing Cadence

The preferred briefing cadence is weekly and monthly, not daily.

From Ted's perspective, ShiftNotes should add a small number of higher-priority briefing emails on top of the existing JotForm archive.

The original JotForm emails still exist and remain available. The briefing emails help Ted decide what deserves attention first.

In practice, this means Ted does not need to manually read every JotForm email unless he wants to verify a specific AI-generated claim or inspect a source report.

### Weekly Briefing

The weekly briefing should help Ted understand what happened across the week without reading every report.

It should include:

- Kiosk-by-kiosk summaries
- Food quality and quantity trends
- Guest issue trends
- Food concern trends
- Operational issue trends
- Waste and unclaimed lunch patterns
- Employee recognition patterns
- Source references for important claims

### Monthly Briefing

The monthly briefing should focus on broader patterns.

It should include:

- Recurring kiosk-specific issues
- Cross-kiosk trends
- Guest demand signals
- Waste patterns
- Operational friction
- Labor and workflow observations
- Potential cost-saving opportunities

### Why Not Daily Briefings

Daily briefings may be less useful because one day of reports may not contain enough pattern evidence.

The value of ShiftNotes is trend detection. Weekly and monthly windows are more appropriate for identifying repeated signals, cost patterns, staffing friction, recurring guest requests, and operational changes.

This reasoning should be revisited and strengthened before the final paper.

## Source-Backed Claims

Every meaningful claim should be traceable back to the original reports.

Example claim:

```text
"Bring back poke" was mentioned 16 times at Bowls and Buns in June.
```

Ted should be able to inspect the evidence:

```text
View source reports:
- Report 2026-06-03, Bowls and Buns
- Report 2026-06-07, Bowls and Buns
- Report 2026-06-09, Bowls and Buns
- ...
```

This is similar to citation behavior in tools like NotebookLM. ShiftNotes should not only generate a claim; it should show the reports behind the claim.

For trend claims, the evidence should include every matching report or a clearly filtered list.

For individual claims, the evidence should include the exact report or reports that support the claim.

## Human-in-the-Loop Correction

The human-in-the-loop process is not just approval.

Ted should be able to review the evidence behind any important claim and correct the system when it is wrong.

This is a general checkpoint pattern, not only a personnel-complaint workflow.

The same review process can apply to:

- Food trends
- Guest requests
- Waste patterns
- Missing reports
- Operational issues
- Recognition trends
- Complaints or sensitive personnel-related notes

Example:

```text
ShiftNotes claim:
"There were three complaints about Tony this week."

Ted reviews sources:
- Report 1 was actually about Tony helping solve a problem.
- Report 2 was a real complaint.
- Report 3 mentioned Tony but was not negative.

Ted marks the claim as incorrect.
```

The system should then:

- Re-check the evidence
- Correct the claim
- Preserve the correction
- Avoid repeating the same mistake if possible

This HITL design matters because any AI-generated operational claim can be wrong. Personnel-related claims are especially sensitive, but the same correction pattern should exist for food, guest, waste, reporting, and operational claims too.

## Possible Ingestion Approaches

### Option 1: Manual CSV Export

JotForm may allow exporting submissions as CSV.

This is the cleanest prototype path if available.

Pros:

- Easiest to analyze
- Lowest parsing risk
- Good for proving the idea

Cons:

- May not match Ted's normal workflow
- Requires manual export
- Not a true automated intake pipeline

### Option 2: Gmail or Email Parsing

The system reads Ted's JotForm emails and extracts fields from the email body.

Pros:

- Matches the real workflow more closely
- Preserves the current reporting process
- Can potentially run automatically

Cons:

- Email formatting can vary
- Parsing failures need handling
- Requires careful validation and source traceability

Decision:

This is now a fallback path.

If JotForm API access is unavailable, Gmail parsing can still be used. However, when API access is available, the API should be preferred because it provides cleaner structured data and reduces parsing risk.

### Option 3: JotForm API

The system pulls submissions directly from JotForm.

Pros:

- Cleaner than email parsing
- More reliable field structure
- Better long-term production path

Cons:

- Requires API access and credentials
- May be more setup than the prototype needs
- Could be out of scope if the goal is only proof of concept

Decision:

This is now the preferred path for the independent final project.

The immediate milestone is to confirm that ShiftNotes can consistently fetch JotForm submissions and normalize them into clean, stable report records.

### Option 4: Hybrid Prototype Path

Use CSV for the prototype, but document how email or API ingestion would replace it later.

Pros:

- Keeps implementation realistic but manageable
- Separates proof of value from integration complexity
- Allows final paper to explain the production path clearly

Cons:

- Does not fully prove live ingestion
- Requires honest documentation of the limitation

## Recommended Thinking For Now

For the independent project, ingestion should be treated as its own pipeline stage:

```text
Raw JotForm Email
    |
    v
Field Extraction
    |
    v
Validation
    |
    v
Clean Structured Report
    |
    v
Trend Analysis
    |
    v
Summary Generation
```

The final implementation should prioritize JotForm API ingestion.

The project should be clear about which path is being used:

- Primary final-project path: JotForm API ingestion
- Delivery path: Gmail or SMTP email briefing delivery
- Fallback ingestion path: Gmail/email parsing if API access is unavailable
- Reproducibility fallback: saved API responses or local fixture files

## Validation Requirements

Every parsed report should be checked for:

- Missing date
- Missing kiosk
- Missing lead name
- Invalid rating values
- Missing freeform fields
- Unclaimed lunches not numeric
- Duplicate report IDs or duplicate emails

If a report cannot be parsed confidently, it should be flagged for human review instead of silently entering the analysis dataset.

## Missing Report Detection

The ingestion layer should also detect missing submissions.

This requires a schedule or expectation table that defines which kiosks should submit reports on which days.

Example:

```text
Expected:
- Kiosk A: Monday, Tuesday, Wednesday, Thursday, Friday
- Kiosk B: Monday, Tuesday, Wednesday, Thursday, Friday
- Kiosk C: Monday, Tuesday, Wednesday, Thursday, Friday

Received this week:
- Kiosk A: Monday, Tuesday, Wednesday, Thursday, Friday
- Kiosk B: Monday, Wednesday, Friday
- Kiosk C: Monday, Tuesday, Wednesday, Thursday

Missing:
- Kiosk B: Tuesday, Thursday
- Kiosk C: Friday
```

Missing reports should appear in weekly and monthly briefings because they affect confidence in the analysis.

Example briefing note:

```text
Reporting completeness: Kiosk B did not submit notes on Tuesday or Thursday. Kiosk C did not submit notes on Friday.
```

This prevents the system from implying that "nothing happened" when the real issue is that no report was submitted.

## Design Principle

The ingestion layer should preserve traceability.

Every clean record should point back to the original source email or form submission. This matters because generated insights need to be auditable.

If ShiftNotes says "Kiosk B had high waste this month," Ted should be able to trace that insight back to the original reports.
