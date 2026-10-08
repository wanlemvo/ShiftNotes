# Dashboard Metrics

The active dashboard reads `demo/data/final_mock/`. Date presets are anchored to
the latest date in that dataset, not today's calendar date. Every view displays
its date bounds. Custom ranges and kiosk filters apply before aggregation.

| Metric | Definition |
| --- | --- |
| Reports received | Unique submissions after content-fingerprint deduplication; includes invalid submissions |
| Missing reports | Expected kiosk/date slots with no submission; invalid reports are separate |
| Average quality / quantity | Mean ratings from valid, deduplicated reports; no-data periods show N/A |
| Unclaimed lunches | Sum over valid reports; no conversion to dollars or assumption that all lunches became waste |
| Urgent findings | Distinct kiosk/category groups assigned urgent by email priority rules, excluding recognition |
| Recurring issues | Non-recognition kiosk/category groups supported on at least two reporting dates in the selected range |
| Recognition reports | Distinct supporting reports, not people or individual mentions |
| Issue observations | Distinct category/source pairs excluding recognition; one report can contain multiple categories |
| Unclaimed / report | Unclaimed total divided by valid report count; not a per-meal waste rate |

Short ranges use daily chart buckets; ranges of 14 days or longer use Monday-based
weekly buckets. Edge buckets may be partial. Missing ratings are not filled with
zero. Averages can shift with changing menus, response completeness, and observer
behavior; they are not objective productivity measurements.

## Counting and Review

Weekly claims form the counting basis. Monthly claims often cite the same sources
and are not added again. Source IDs are deduplicated within kiosk/category groups.
Three-month findings expose links to each underlying weekly claim. Source drawers
display all supporting reports in the selected range.

Priority follows `email_preview.claim_urgency`: category rules first, then the
existing four-source threshold for important follow-up. These are review tiers,
not measured financial impact or a model confidence ranking. Comparisons show
counts and averages rather than invented highest-risk or strongest-kiosk scores.

Confirmed weekly corrections change dashboard source totals. A monthly correction
stays scoped to its monthly claim; it does not rewrite weekly counterparts or
future rules. Already-generated email files are snapshots and are not silently
rewritten.

- [Dashboard projection](../demo/src/shiftnotes/dashboard.py)
- [Dashboard UI](../demo/src/shiftnotes/dashboard_view.py)
- [Counting/filter tests](../tests/test_dashboard.py)
