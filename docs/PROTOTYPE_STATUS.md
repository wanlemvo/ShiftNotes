# Prototype Status

ShiftNotes is currently a usable prototype, not a production deployment.

## Implemented

- JotForm API client and JotForm-style mock ingestion.
- Normalization into consistent ShiftNotes records.
- Validation for missing required fields.
- Missing report detection by kiosk and expected date.
- Duplicate and malformed report handling.
- Three-month synthetic dataset across six kiosks.
- Planted ground truth for benchmarking.
- Deterministic metrics for ratings, waste, dates, and completeness.
- Groq semantic extraction for free-text operational signals.
- Strict source validation for AI claims.
- Retry and deterministic fallback behavior.
- Weekly and monthly briefing generation.
- HTML and plain-text email previews.
- Gmail API delivery with explicit send confirmation.
- Source-backed claim catalog.
- Streamlit source inspection workspace.
- Integrated operations dashboard with date/kiosk filters, trend charts,
  priority queue, comparison/export, recognition, and missing-date inspection.
- Ordinary-English claim challenge flow.
- Human confirmation before saving corrections.
- Correction history.
- Sensitive personnel guardrails.
- Automated test coverage for the active prototype.

## Not Implemented Yet

- Production scheduler.
- Hosted authentication.
- Production database.
- Tenant/user accounts.
- Real JotForm production backfill from Ted's account.
- Automatic recurring Gmail sends.
- Groq-assisted correction interpretation.
- Direct source links back to original JotForm records.
- Monitoring and alerting for production jobs.
- Google Forms, Microsoft Forms, Typeform, or generic CSV input connectors.
- Automatic pagination and incremental JotForm synchronization.
- Live fetch-to-rich-dashboard/briefing dataset handoff.

## Current Evidence

The October 8, 2026 local test run passed:

```text
58 tests (52 existing tests, 4 dashboard aggregation tests, and 2 app interaction tests).
```

Before archive cleanup, the full mixed repo suite had 62 passing tests. The 10
archived tests covered the older team prototype classifier/state package rather
than the active email-first ShiftNotes demo.

See [verification](VERIFICATION.md) for current checks and limitations. The
dashboard update and demo media are published on GitHub `main` in `89157b1`;
hosted deployment verification is tracked separately in that document.

The dataset includes planted ground-truth patterns so the system can be checked
against known source-level events instead of only judged by whether briefings
sound plausible.

## Product Readiness

The prototype is ready to demonstrate:

- source-backed weekly/monthly operations briefings;
- email preview and Gmail delivery;
- claim inspection;
- human-in-the-loop correction;
- responsible handling of sensitive personnel notes.

It is not ready to process private workplace data on a public unauthenticated
dashboard.

## Evaluation Signals

The prototype's value can be measured by:

- reports summarized per briefing;
- source-backed claims generated;
- missing kiosk/date reports detected;
- planted patterns recovered from the mock dataset;
- semantic precision and recall;
- time saved versus manually reading every report;
- correction history showing where a human reviewer challenged or confirmed
  claims.

## Production Readiness Gap

To become production software, ShiftNotes needs:

- authentication;
- hosted database storage;
- scheduled background jobs;
- secure secret management;
- user/tenant isolation;
- audit logging;
- operational monitoring;
- privacy review for employee-related content.

## Next Implementation Order

1. Connect live ingestion, pagination, the expected reporting schedule, and rich
   briefing generation through a configurable dataset boundary.
2. Add authenticated access and durable storage before workplace data hosting.
3. Deploy scheduled jobs with idempotent sending, monitoring, and recovery.
4. Pilot with real users and measure review time, accuracy, and correction rates.
5. Add other form providers only when the pilot establishes a need.
