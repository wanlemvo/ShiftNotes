# Final Mock Dataset Design

## Purpose

This dataset is a controlled synthetic representation of the ShiftNotes
workplace workflow. It provides enough scale and variation to test weekly and
monthly operational analysis without exposing real workplace or personnel data.

The dataset is an experimental artifact, not merely demonstration content.
Known patterns are planted deliberately and stored separately as ground truth so
the system's findings can be measured against expected results.

## Why Twelve Weeks

The final dataset covers 12 weeks, approximately three months.

Four weeks can demonstrate repetition, but it provides limited evidence for
monthly comparison or changes over time. Six months would approximately double
the generation, inspection, and benchmarking workload without materially
improving the final prototype demonstration.

Twelve weeks supports:

- weekly summaries;
- three monthly reporting periods;
- recurring and changing trends;
- cross-kiosk comparisons;
- missing-report detection;
- source-backed benchmark evaluation.

## Reporting Schedule

The model assumes:

```text
12 weeks x 6 kiosks x 4 expected reporting days = 288 expected reports
```

Reports are expected Monday through Thursday for every kiosk. Missing reports
are represented as absent submissions, not blank forms.

The `expected_reporting_schedule.csv` file records every expected kiosk/date
combination and whether it is valid, missing, or malformed.

## Kiosks

The six synthetic kiosks are:

- Bowls & Buns
- Market Grill
- Verde Kitchen
- Coastal Cafe
- Hearth & Grain
- Street Eats

The names and menu details are fictionalized. Bowls & Buns reflects the menu
structure used during the initial JotForm proof, while the remaining kiosks add
realistic operational variety.

## Data Composition

The schedule contains:

- 267 valid scheduled submissions;
- 18 missing kiosk/date submissions;
- 3 received but malformed submissions;
- 3 duplicate submissions added outside the expected schedule.

The JotForm-shaped payload therefore contains 273 submission objects.

Malformed and duplicate submissions are intentionally rare. JotForm validation
prevents many incomplete forms, but API, configuration, resubmission, or data
handling problems remain possible and should be tested defensively.

## Realistic Variation

Reports vary across:

- shift leads and recognized employees;
- ratings from one through five;
- unclaimed lunch counts;
- food shortages and overproduction;
- guest requests, complaints, praise, and menu questions;
- dietary and allergy questions;
- equipment failures and workflow bottlenecks;
- inventory inconsistencies;
- ambiguous personnel language;
- quiet days with no significant concerns.

Reports use repeated templates with controlled wording variation. This mirrors
how operational notes often describe similar events differently without
requiring hundreds of manually written reports.

## Planted Patterns

Each kiosk has a primary recurring pattern:

| Kiosk | Primary pattern |
| --- | --- |
| Bowls & Buns | Recurring Kung Pao chicken shortages |
| Market Grill | Elevated unclaimed lunches and overproduction |
| Verde Kitchen | Dietary and allergy questions |
| Coastal Cafe | Equipment and register friction |
| Hearth & Grain | Repeated recognition of Maya Chen |
| Street Eats | Inconsistent inventory and preparation |

Cross-kiosk events include:

- register disruption during Week 7;
- a waste increase during Weeks 7 and 8;
- portion complaints during Weeks 9 and 10;
- beverage-variety requests during Week 11.

One ambiguous personnel comment is included to test whether the system avoids
turning uncertain language into an unsupported personnel conclusion.

## Ground Truth Separation

`ground_truth.json` contains the deliberately planted event categories, expected
counts, source submission IDs, dates, weeks, and kiosks.

Those labels do not appear in `jotform_submissions.json`. The analysis pipeline
receives only the form content. Ground truth is used afterward for benchmarking.

This prevents the system from obtaining the expected answer directly from its
input.

## Source Traceability

Every expected schedule slot has a stable ID such as `FM-0001`. The same ID is
used by:

- the JotForm submission;
- the normalized report;
- the expected reporting schedule;
- ground-truth event records;
- future source-backed claims.

Duplicate submissions receive separate `DUP-*` IDs and are mapped to their
original source IDs in ground truth.

## Intended Evaluation

The dataset supports measurement of:

- trend detection precision and recall;
- source-ID accuracy;
- missing kiosk/date detection;
- duplicate and malformed-record handling;
- weekly and monthly aggregation;
- cross-kiosk comparisons;
- safety around sensitive personnel language.

## Limitations

Synthetic data cannot reproduce every ambiguity, writing style, or operational
condition found in real reports. Good benchmark performance does not prove
identical performance on live workplace data.

The dataset also reflects deliberately selected patterns and may be easier to
interpret than uncontrolled real-world reporting. These limitations should be
stated in the final technical report.
