# MOCK_DATA_DESIGN.md

# Purpose

This document defines the synthetic operational dataset used to test and validate ShiftNotes.

The goal is not to generate random reports.

The goal is to simulate realistic operational behavior and create recurring patterns that ShiftNotes should be capable of identifying.

This document serves as the ground truth for evaluating whether the intelligence pipeline is functioning correctly.

---

# Dataset Scope

## Time Period

4 Weeks

---

## Reporting Locations

6 Kiosks

* Kiosk A
* Kiosk B
* Kiosk C
* Kiosk D
* Kiosk E
* Kiosk F

---

## Reporting Frequency

4 reports per week per kiosk

Approximate Total:

```text
6 kiosks
×
6 reports per day
x
4 days a week
×
4 weeks

=
96 reports
```

Rounded Target:

```text
100 reports
```

---

# Intelligence Goals

The synthetic dataset should contain patterns that are obvious in hindsight but difficult to identify through manual review alone.

ShiftNotes should be capable of discovering these patterns automatically.

---

# Kiosk Profiles

## Kiosk A

### Known Pattern

Recurring Chicken Shortages

### Typical Issues

* Running out of chicken during peak hours
* Prep levels slightly below demand
* Lower food quantity ratings

### Expected Insights

* Chicken shortage frequency
* Peak shortage periods
* Inventory planning concerns

---

## Kiosk B

### Known Pattern

High Food Waste

### Typical Issues

* Excess food preparation
* High number of unclaimed lunches
* Overproduction during slower shifts

### Expected Insights

* Waste trends
* Overproduction indicators
* Cost-saving opportunities

---

## Kiosk C

### Known Pattern

Recurring Guest Requests

### Typical Issues

* Frequent requests for poke
* Menu variety requests
* Product demand observations

### Expected Insights

* Most requested menu items
* Customer demand signals
* Potential revenue opportunities

---

## Kiosk D

### Known Pattern

Operational Friction

### Typical Issues

* Equipment problems
* Supply issues
* Process bottlenecks

### Expected Insights

* Recurring operational concerns
* Areas requiring investigation
* Operational reliability issues

---

## Kiosk E

### Known Pattern

High Team Performance

### Typical Issues

* Minimal operational issues
* Frequent employee recognition
* Positive staffing observations

### Expected Insights

* Recognition trends
* Positive operational patterns
* Staffing effectiveness

---

## Kiosk F

### Known Pattern

Inconsistent Inventory Management

### Typical Issues

* Frequent quantity concerns
* Preparation inconsistencies
* Inventory fluctuations

### Expected Insights

* Inventory instability
* Quantity rating trends
* Preparation accuracy concerns

---

# Structured Data Guidelines

Food Quality Ratings

Range:

```text
1 - 5
```

Expected Average:

```text
3.5 - 4.5
```

Most ratings should be positive.

---

Food Quantity Ratings

Range:

```text
1 - 5
```

Variation should reflect inventory challenges.

---

Unclaimed Lunches

Range:

```text
0 - 12
```

Kiosk B should consistently report higher values.

---

# Freeform Data Guidelines

Reports should contain realistic operational language.

Examples:

Food Concerns

* "Chicken ran low around lunch rush."
* "Prep levels were perfect for today's volume."
* "Rice needed additional preparation around 1PM."

---

Guest Feedback

* "Bring back poke."
* "Guests asked for more menu variety."
* "Several guests requested additional beverage options."

---

Recognition

* "Dom B. helped keep the line moving during lunch."
* "Great teamwork during the afternoon rush."
* "Strong communication between team members."

---

Operational Notes

* "Register system froze briefly during lunch."
* "Supply delivery arrived later than expected."
* "No major concerns today."

---

# Hidden Cross-Kiosk Trends

The dataset should contain several trends that only become visible when reports are aggregated.

Examples:

## Menu Requests

"Bring back poke."

Should appear across multiple kiosks.

Expected Discovery:

* Most requested menu item

---

## Waste Trends

Unclaimed lunches should increase slightly during Week 3.

Expected Discovery:

* Waste spike detection

---

## Staffing Trends

Positive staffing observations should correlate with higher food quantity ratings.

Expected Discovery:

* Relationship between staffing and operational performance

---

## Operational Issues

Most equipment-related concerns should occur at Kiosk D.

Expected Discovery:

* Recurring operational hotspot

---

# Success Criteria

The dataset will be considered successful if ShiftNotes can identify:

* Most requested menu item
* Highest waste location
* Most common operational issue
* Most frequently recognized employee
* Most common food concern
* Most significant trend changes over time

---

# Future Expansion

Future datasets may include:

* Multiple locations
* Seasonal trends
* Staffing schedules
* Revenue data
* Inventory data
* Customer traffic data

The MVP dataset focuses exclusively on operational reporting data.
