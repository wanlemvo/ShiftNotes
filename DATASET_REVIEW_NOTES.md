# Dataset Review Notes

## Purpose

This document captures the review of the team prototype mock shift-note dataset before deciding whether it should be used in the independent final project.

The goal is to understand whether the dataset reflects the actual operational reporting workflow closely enough to support meaningful analysis.

## Initial Observation

The underlying report structure is strong.

The shift-note form already asks for the categories operations cares about:

- Food quality
- Food quantity
- Food concerns or outages
- Team member recognition
- Guest issues
- Operational notes
- Number of unclaimed lunches

This means the data is already cleaner than a generic set of unstructured notes would be. The form itself creates a useful operational frame before any analysis happens.

## Structured Fields

Some fields are already straightforward to analyze:

- Date
- Week
- Kiosk
- Lead name
- Food quality rating
- Food quantity rating
- Number of unclaimed lunches

These fields can support direct analysis such as:

- Average ratings by kiosk
- Waste totals by kiosk
- Trend changes by week
- Reporting volume by location
- Lead participation

## Semantic Fields

The harder fields are the ones that require interpretation:

- Food concerns or outages
- Guest issues for the day
- Operational notes
- Team members who did well

Team recognition can partly be analyzed through name mentions, but it still needs context because a name mention is not always the same as meaningful recognition.

Food concerns, guest issues, and operational notes are likely where the most valuable intelligence lives.

## Current Dataset Strengths

The current team dataset is useful as a starting point because:

- It contains 100 reports.
- It covers six kiosks.
- It includes repeated patterns.
- It includes food shortage, waste, guest feedback, recognition, and operational issue signals.
- It can demonstrate that repeated report patterns can be surfaced without manually reading every report.

## Current Dataset Concerns

The dataset is too narrow around poke requests.

That pattern is useful for proving the concept, but the final independent project should not rely on one repeated request as the main example of guest intelligence.

A more realistic dataset should include:

- Multiple menu requests
- Guest complaints
- Positive guest feedback
- Service speed concerns
- Portion comments
- Dietary or allergy questions
- Beverage requests
- Confusion about menu availability
- Repeated but subtle themes across weeks

## Why Scale Matters

A larger dataset may be more useful for proving value.

Three to six months of reports would make it easier to show:

- Waste patterns over time
- Whether certain menu items are worth keeping or removing
- Which guest requests repeat enough to deserve attention
- Which kiosks have recurring operational friction
- How staffing and workflow issues affect service
- Where labor time may be better allocated

This matters because one of the business values of ShiftNotes is cost awareness.

The goal is not simply to cut labor hours. The goal is to help leadership understand where time, prep, food, and attention are being used effectively or inefficiently.

## Independent Project Implication

The current dataset should be treated as a prototype dataset, not final evidence.

Before using it for the final project, the independent version should either:

1. revise and expand the mock data, or
2. create a new final-project dataset based more closely on the real shift-note language and operational workflow.

The final dataset should be large enough and varied enough to support both trend analysis and source-traceable summaries.

## Final Dataset Decision

The independent project now uses a new deterministic 12-week dataset rather than
expanding the original CSV in place.

The final dataset contains:

- six realistically named synthetic kiosks;
- 288 expected kiosk/date reporting slots;
- 267 valid scheduled submissions;
- 18 missing kiosk/date reports;
- three malformed submissions;
- three duplicate extras;
- broader guest, food, recognition, workflow, waste, dietary, and safety-related language;
- a separate ground-truth file with expected patterns and source IDs.

The original 96-report dataset and team 100-report dataset remain preserved as
prototype history. The final dataset is stored under
`final_project/data/final_mock/`.

Three months was selected because it supports weekly and monthly comparisons
without the additional generation and validation cost of a six-month dataset.

Missing reports are defined by the expected kiosk/date schedule. They are not
represented as empty forms, and they must not be detected by assuming that every
calendar day is a reporting day.
