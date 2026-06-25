# ShiftNotes Briefing Design

## Purpose

ShiftNotes produces two different management outputs because weekly and monthly
decisions operate at different levels.

- Weekly briefings answer: What happened at each kiosk this week?
- Monthly briefings answer: What patterns may affect cost, service, and
  operational planning?

The formats are generated from the same cleaned, source-traceable reports, but
they do not present the same information.

## Weekly Briefing

The weekly briefing is kiosk-centered.

It contains:

1. week-at-a-glance metrics;
2. reporting completeness;
3. management attention items;
4. one section for each kiosk;
5. week-over-week changes;
6. source-backed trends and recognition;
7. suggested follow-up;
8. missing and malformed report details.

Each kiosk section includes:

- valid reports received versus expected;
- average food quality;
- average food quantity;
- unclaimed lunches and unclaimed lunches per valid report;
- change from the previous week;
- notable food, guest, workflow, waste, or recognition signals;
- source submission IDs.

Weekly follow-ups are operational prompts rather than autonomous decisions.

## Monthly Briefing

The monthly briefing is comparative and decision-oriented.

It contains:

1. executive summary;
2. month-over-month direction;
3. cost and waste signals;
4. kiosk comparisons;
5. recurring guest, food, and operational trends;
6. workflow-efficiency indicators;
7. team recognition;
8. reporting compliance;
9. management priorities;
10. sensitive-note safeguards.

Raw monthly totals can be misleading when months contain different numbers of
reporting days. Comparisons therefore emphasize:

- averages;
- percentages;
- unclaimed lunches per valid report;
- direction of change.

May 2026 is explicitly labeled as a partial month.

## Cost-Saving Language

ShiftNotes can identify waste and overproduction signals, but it does not
currently receive:

- cost per meal;
- revenue;
- guest volume;
- transaction volume;
- labor hours.

The briefing therefore describes a "possible opportunity" and recommends
validation. It does not calculate dollar savings or claim confirmed
productivity changes.

## Source Traceability

Meaningful trends include JotForm submission IDs. These IDs will later connect
to a source-inspection view.

The current Markdown artifact lists IDs directly. The production email should
replace long ID lists with links such as:

```text
View 5 supporting reports
Challenge this claim
```

The source bundle must still preserve every supporting ID.

## Human-in-the-Loop Position

Ted does not approve routine briefings before delivery.

The intended production flow is:

```text
Generate briefing
-> deliver briefing
-> Ted optionally inspects sources
-> Ted challenges a claim in ordinary English
-> ShiftNotes rechecks the sources
-> correction is explained and logged
```

A checkpoint is required before consequential follow-up actions such as
personnel escalation or treating a correction as authoritative.

## Rotating Menu Limitation

ShiftNotes does not currently receive the weekly rotating menu schedule.

Menu-specific findings are limited to dishes explicitly named in shift reports.
The system must not calculate an item availability rate or assume that a dish
was offered on dates where it was not mentioned.

## Personnel Safety

Ambiguous personnel notes are surfaced for inspection but cannot be treated as
evidence of misconduct or used for autonomous personnel action.

## Current Implementation Boundary

Implemented:

- twelve weekly Markdown briefings;
- three monthly Markdown briefings;
- source IDs;
- reporting exceptions;
- weekly and monthly comparisons;
- financial and productivity guardrails;
- menu limitation;
- sensitive-personnel warning.

Not implemented:

- email delivery;
- clickable source inspection;
- natural-language challenge processing;
- correction history;
- AI-assisted semantic extraction.
