# Project Overview

## Workplace Problem

Shift leads already record food ratings, shortages, guest feedback, recognition,
operational concerns, and unclaimed lunches. Leadership then has to read the
individual notes and decide what deserves attention. The difficult work is
comparison and prioritization, not collecting another form.

ShiftNotes is intended to reduce that review burden. Weekly briefings summarize
each kiosk and surface recurring issues. Monthly briefings support inventory
and preparation discussions. Significant semantic findings have supporting
report IDs so a manager can inspect the evidence instead of relying on a summary.

## Product Direction

Email is the primary delivery channel. The dashboard supports group meetings and
optional investigation: date and kiosk filters, trend charts, comparisons, source
inspection, and claim correction.

The business hypothesis is that organized, source-backed review saves management
time and helps reveal shortages, repeated equipment concerns, and preparation
imbalances. The prototype demonstrates the workflow; it does not establish
measured time savings, labor savings, or financial return.

## Origins and Ownership

The project began as a team class prototype. The Week 8 Final Project Prototype
Kickoff was the last shared checkpoint. Week 9 and subsequent development of
this workplace-specific version were independent work by the repository owner.
The team may have continued a separate version of the original idea.

The repository owner identified the workplace problem and directed the product
concept, email-first experience, source-backed claims, review checkpoints, and
adoption strategy. AI coding tools helped implement, test, document, and refine
those decisions. That does not imply every line was written without assistance
or that the archived team implementation was solely authored by one person.

The [original independent-work log](archive/class_docs/SOLO_WORK_LOG.md) preserves
the transition and earlier decisions. Some entries were retrospective records,
not contemporaneous proof of the decision date. New changes are recorded in the
[change log](CHANGELOG.md).

## User Feedback

Ted, the intended operations manager, requested visibility into immediate safety
or equipment issues, prioritization of other tasks, employee recognition, and
coaching opportunities. The current product uses urgent/follow-up/monitor tiers
and treats personnel material as a prompt for private review rather than an
accusation or disciplinary recommendation. See [workflow](PRODUCT_WORKFLOW.md)
and [feature inventory](FEATURE_INVENTORY.md).

## Current Boundary

This is a demonstrable prototype with a JotForm connector, reusable analysis
components, explicit Gmail sending, and a synthetic dashboard. It is not yet an
unattended workplace service or a universal form-analysis product. The next
operational step is connecting live data to an authenticated, scheduled workflow
and evaluating its usefulness with the intended users.
