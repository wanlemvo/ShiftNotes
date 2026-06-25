# ShiftNotes Product Workflow

## Primary User Experience

Email is the primary ShiftNotes interface.

Ted receives:

- a Thursday afternoon weekly briefing;
- a monthly briefing before the final expected reporting shift used for
  inventory planning.

The Streamlit application is a secondary inspection workspace. Ted does not
need to open it unless he wants to inspect evidence, challenge a claim, or
review correction history.

## Email Preview

The implemented email preview includes:

- a concise subject line;
- reporting, quality, quantity, and waste metrics;
- priority source-backed findings;
- links to supporting reports;
- links to challenge individual claims;
- interpretation and financial guardrails;
- responsive HTML and plain-text alternatives.

The preview is generated locally. It is not sent through Gmail yet.

## Claim and Source Model

Each claim stores:

- stable claim ID;
- weekly or monthly period;
- kiosk;
- category;
- readable claim text;
- all supporting submission IDs;
- source count;
- sensitivity status.

The source viewer displays the original normalized JotForm fields rather than
only a model-generated excerpt.

## Post-Delivery Challenge Workflow

The production interaction differs from the Week 6 class demonstration.

```text
Generate briefing
-> preview/deliver briefing
-> Ted optionally challenges a claim
-> retrieve supporting reports
-> interpret the challenge
-> propose a corrected claim
-> HITL confirmation
-> save or cancel correction
-> preserve audit history
```

Ted can write ordinary English and may include a source ID. Challenge
interpretation currently uses deterministic mock behavior behind a replaceable
provider boundary. Groq is connected to report-semantic extraction first so its
quality can be benchmarked before it is allowed to propose corrections.

## Second HITL Checkpoint

A challenge does not immediately change a claim.

ShiftNotes displays:

- original claim;
- proposed correction;
- removed and retained sources;
- rationale.

Ted must choose:

- Confirm correction
- Revise challenge
- Cancel

Only confirmation writes an accepted correction to history.

## Correction Authority

Confirmed corrections are audit records for the challenged claim. They do not
automatically modify future classification rules.

Changing future system behavior would require a separate reviewed model or rule
update.

## Safety Policy

ShiftNotes refuses requests to:

- accuse an employee automatically;
- recommend or execute discipline;
- recommend termination;
- distribute unverified personnel allegations.

Ambiguous personnel notes require source inspection and cannot support
autonomous personnel action.

## Scheduling Policy

Timezone:

```text
America/Los_Angeles
```

Weekly:

```text
Thursday at 3:30 PM Pacific
```

Monthly:

```text
Day before the final expected reporting day of the month at 3:30 PM Pacific
```

The monthly timing is intended to inform end-of-month inventory review and
ordering. The policy is represented as configuration metadata; an external job
scheduler is not connected yet.

## Streamlit Workspace

The workspace includes:

1. Briefings
   - polished weekly/monthly email previews;
   - full Markdown briefing text.
2. Claims & Sources
   - filters;
   - stable claim selection;
   - original source reports and ratings.
3. Challenge Review
   - ordinary-English challenge input;
   - clarification and safety responses;
   - proposed correction;
   - confirmation checkpoint.
4. Correction History
   - actor;
   - timestamps;
   - original and proposed claims;
   - decision and removed sources.

## Implemented Without External APIs

- claim catalog;
- source inspection;
- deterministic challenge interpretation;
- safety refusal;
- LangGraph correction checkpoint;
- SQLite persistence;
- correction history;
- HTML and plain-text email previews;
- scheduling policy;
- Streamlit workspace.

## Semantic Intelligence

The Groq integration now implements the provider boundary previously represented
by deterministic fixtures. It extracts source-backed signals from free text,
validates exact evidence, retries malformed responses, and benchmarks results
against planted source-level ground truth.

When `ai_extractions.json` exists, weekly/monthly briefings and the dashboard
claim catalog use those semantic signals for source-backed trends. Exact
operational metrics still come from deterministic Python.

The deterministic path remains available for failure recovery and comparison.
The full-dataset validation exposed Groq on-demand quota limits, so full
backfills should run in smaller batches or on a higher service tier before being
claimed as pure model output.
See `MODEL_SELECTION_AND_BENCHMARK.md`.

## Future Integrations

- Groq-assisted challenge interpretation;
- Gmail email delivery;
- production scheduler;
- hosted source links;
- authenticated manager access.
