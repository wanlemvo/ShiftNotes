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

The implemented email includes:

- a concise subject line;
- reporting, quality, quantity, and waste metrics;
- immediate-attention, important-follow-up, and monitoring/recognition findings;
- links to supporting reports;
- links to challenge individual claims;
- interpretation and financial guardrails;
- responsive HTML and plain-text alternatives.

ShiftNotes generates a local preview first. After one-time Google OAuth
authorization, an explicitly confirmed CLI command can send that same HTML and
plain-text briefing through Gmail. The sender requests only the `gmail.send`
scope and cannot read the mailbox.

## Priority Model

Findings are divided into three operational tiers:

1. **Immediate attention:** explicit safety concerns, equipment or register
   disruptions, and sensitive personnel notes requiring private source review.
2. **Important follow-up:** shortages, waste/overproduction, inventory
   inconsistencies, dietary questions, portion concerns, and carefully framed
   coaching or training review signals.
3. **Monitor and recognize:** lower-risk guest requests, positive employee
   recognition, and other patterns worth watching.

Coaching signals are prompts for private human review. ShiftNotes does not
infer misconduct or recommend discipline.

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

## Gmail Delivery

Gmail delivery uses a Google Desktop OAuth client, a locally stored refresh
token, and the narrow `gmail.send` scope. Live delivery always requires the
`--confirm-send` CLI flag. Credentials and tokens are excluded from Git.

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
- production scheduler;
- hosted source links;
- authenticated manager access.
