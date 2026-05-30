# CURRENT FORM ANALYSIS

## Purpose

This document analyzes the current operational reporting form used by Dsquared Hospitality at T-Mobile Headquarters.

The purpose of this analysis is to understand:

* What information is currently being collected
* What operational intelligence already exists within the reports
* What information may be difficult to analyze at scale
* What insights could potentially be derived from historical reporting data
* What opportunities exist to improve future data collection and intelligence extraction

This document is intended to serve as the bridge between the current reporting workflow and the future ShiftNotes intelligence system.

---

# Current Form Structure

The current form captures a combination of structured data and freeform operational notes.

| Field                       | Type       |
| --------------------------- | ---------- |
| Date                        | Structured |
| Lead Name                   | Structured |
| Food Quality Rating         | Structured |
| Food Quantity Rating        | Structured |
| Food Concerns or Outages    | Freeform   |
| Team Members Who Did Well   | Freeform   |
| Guest Issues for the Day    | Freeform   |
| Operational Notes           | Freeform   |
| Number of Unclaimed Lunches | Structured |

---

# Example Submission

## Date

05-21-2026

## Lead Name

D.B.

## Food Quality Rating

4/5

## Food Quantity Rating

4/5

## Food Concerns or Outages

"Great tasting chicken, perfect amount of prep for a Thursday."

## Team Members Who Did Well

"Great amount of people in the play it ran smooth because Dom was back and he was in the line helping out."

## Guest Issues for the Day

"Bring back poke."

## Operational Notes

"N/A"

## Number of Unclaimed Lunches

6

---

# Information Categories Currently Captured

Although the form appears simple, it is collecting several distinct categories of operational information.

## Operational Intelligence

Examples:

* Food quality
* Food quantity
* Food preparation
* Food shortages
* Operational concerns
* Waste tracking

Potential value:

* Inventory optimization
* Food preparation planning
* Waste reduction
* Operational consistency

---

## Team Intelligence

Examples:

* Employee recognition
* Staffing observations
* Leadership effectiveness
* Team performance

Potential value:

* Employee recognition tracking
* Identification of strong performers
* Staffing impact analysis
* Leadership development

---

## Guest Intelligence

Examples:

* Guest complaints
* Product requests
* Recurring feedback
* Customer sentiment

Potential value:

* Product demand signals
* Menu planning
* Guest satisfaction monitoring
* Recurring customer concerns

---

# Current Workflow Strengths

The current form provides several advantages.

## Simplicity

The form is relatively short and easy to complete.

This increases reporting consistency and reduces reporting fatigue.

---

## Operational Context

The form allows shift leads to provide context that would be difficult to capture using purely structured fields.

Examples include:

* Staffing observations
* Guest interactions
* Operational challenges
* Employee recognition

---

## Accountability

Each submission is associated with a specific lead and date.

This creates traceability and operational accountability.

---

## Historical Record Keeping

The current process successfully captures and preserves operational information over time.

---

# Current Workflow Weaknesses

The current workflow was designed primarily for human review.

It was not designed for large-scale intelligence extraction or trend analysis.

---

## Freeform Data Dominance

Many of the most valuable observations are stored as unstructured text.

Examples:

### Guest Issues

Current Entry:

"Bring back poke."

Potential meanings:

* Product request
* Demand signal
* Menu feedback
* Recurring customer interest

These meanings are understandable to a human reviewer but difficult to analyze automatically.

---

### Team Member Recognition

Current Entry:

"Great amount of people in the play it ran smooth because Dom was back and he was in the line helping out."

Potential intelligence hidden inside:

* Employee recognition
* Positive leadership impact
* Staffing contribution
* Operational efficiency

This information exists but is difficult to aggregate across hundreds of reports.

---

## Limited Categorization

The form currently relies on the lead to describe issues rather than classify them.

This creates inconsistency in reporting language.

Examples:

A staffing issue could be described as:

* "Short staffed today"
* "Needed another person"
* "Line got backed up"
* "Not enough people"

Humans understand these are related.

Traditional analytics systems do not.

---

## Limited Trend Visibility

Current reporting allows events to be documented.

However, identifying patterns requires manual review across many reports.

Examples:

* Which food items are most frequently requested?
* Which employees receive the most recognition?
* What operational issues occur most often?
* Which shifts experience the most shortages?

Answering these questions currently requires significant manual effort.

---

# Operational Intelligence Currently Available

Based on the current form structure, ShiftNotes could potentially derive the following insights.

## Food Intelligence

Potential insights:

* Most common food concerns
* Most common outages
* Waste trends
* Food quality trends
* Preparation accuracy trends

---

## Staffing Intelligence

Potential insights:

* Frequently recognized employees
* Leadership impact observations
* Staffing-related operational performance
* Team contribution trends

---

## Guest Intelligence

Potential insights:

* Most requested menu items
* Recurring guest complaints
* Product demand patterns
* Customer sentiment trends

---

## Operational Intelligence

Potential insights:

* Recurring operational issues
* Common shift challenges
* Process bottlenecks
* Operational performance patterns

---

# Future Form Evolution Opportunities

This section documents ideas for future versions of the intake form.

These ideas are exploratory and are not currently part of the MVP.

---

## Structured Guest Feedback Categories

Instead of:

Guest Issues for the Day

Potential future structure:

* Complaint
* Suggestion
* Product Request
* Service Issue

---

## Structured Employee Recognition

Instead of:

Team Members Who Did Well

Potential future structure:

* Employee Name
* Recognition Category
* Optional Notes

---

## Structured Operational Events

Potential future categories:

* Staffing Issue
* Inventory Issue
* Equipment Issue
* Guest Escalation
* Process Concern

---

## Hybrid Reporting Model

Future versions may benefit from a hybrid approach:

### Structured Data

Used for:

* Analytics
* Trend detection
* Operational scoring
* Reporting consistency

### Freeform Notes

Used for:

* Context
* Nuance
* Edge cases
* Human observations

This approach may provide the best balance between usability and intelligence extraction.

---
# Business Impact Opportunities

One of the most significant opportunities presented by ShiftNotes is the ability to convert operational observations into measurable business intelligence.

Many of the data points currently being collected are useful individually, but become significantly more valuable when analyzed across weeks, months, and years of reporting history.

ShiftNotes is designed to identify trends that may otherwise go unnoticed during manual review.

---

## Food Cost Optimization

Current Data Sources:

- Food Quality Rating
- Food Quantity Rating
- Food Concerns or Outages
- Unclaimed Lunches

Potential Insights:

- Frequently underprepared items
- Frequently overprepared items
- Recurring food shortages
- Waste trends over time
- Day-of-week preparation patterns
- Seasonal demand patterns

Potential Business Impact:

- Reduced food waste
- Improved inventory planning
- Better preparation forecasting
- Lower operational costs

---

## Labor Optimization

Current Data Sources:

- Team Members Who Did Well
- Operational Notes

Potential Insights:

- Staffing shortages
- High-performing shifts
- Leadership impact
- Team efficiency observations
- Recurring operational bottlenecks

Potential Business Impact:

- Improved scheduling decisions
- Better labor allocation
- Reduced overtime costs
- Improved shift performance

---

## Guest Experience Optimization

Current Data Sources:

- Guest Issues for the Day

Potential Insights:

- Recurring complaints
- Product requests
- Service concerns
- Menu demand trends

Potential Business Impact:

- Improved guest satisfaction
- Better menu planning
- Increased sales opportunities
- Faster issue resolution

---

## Operational Efficiency Optimization

Current Data Sources:

- Operational Notes
- Food Concerns or Outages

Potential Insights:

- Recurring operational issues
- Process inefficiencies
- Equipment concerns
- Shift-level bottlenecks

Potential Business Impact:

- Reduced operational friction
- Faster issue identification
- Improved consistency
- Better decision-making

---

## Long-Term Organizational Memory

One of the greatest challenges in operational environments is that knowledge often becomes fragmented across emails, folders, spreadsheets, and individual employees.

ShiftNotes has the potential to create a searchable operational memory layer that preserves historical context and enables leadership to identify trends that would otherwise remain hidden.

Instead of relying solely on individual memory, leadership gains access to a continuously evolving record of operational behavior and performance.

---
# Key Takeaways

The current reporting form successfully captures valuable operational information and supports daily operational communication.

However, the form was designed primarily for information collection and human review rather than intelligence extraction.

Significant operational value exists within the collected reports, but much of that value remains difficult to access due to freeform reporting and manual review processes.

ShiftNotes aims to preserve the strengths of the current workflow while introducing an intelligence layer capable of identifying patterns, generating summaries, and surfacing operational insights from information that is already being collected.
