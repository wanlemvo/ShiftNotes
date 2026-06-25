# ShiftNotes Final Project Prototype

This folder contains the independent final-project implementation for ShiftNotes.

Current milestone:

```text
JotForm API submissions
    |
    v
Clean ShiftNotes report records
    |
    v
Weekly source-backed operations briefing
    |
    v
LangGraph HITL review and finalization
```

## Setup

Copy the environment template:

```bash
copy final_project\.env.example final_project\.env
```

Then fill in:

```env
JOTFORM_API_KEY=your_api_key_here
JOTFORM_FORM_ID=your_form_id_here
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

Do not commit `.env`.

## Fetch JotForm Submissions

From the repository root:

```bash
python final_project/src/shiftnotes/cli.py fetch
```

Expected output:

```text
Fetched submissions from JotForm
Saved raw response
Saved normalized reports
```

Outputs:

```text
final_project/data/raw/jotform_submissions.json
final_project/data/processed/reports.json
```

## Analyze Reports

After fetching submissions, generate a weekly analysis and briefing:

```bash
python final_project/src/shiftnotes/cli.py analyze
```

Optional missing-report checks can be enabled by passing expected kiosks:

```bash
python final_project/src/shiftnotes/cli.py analyze --expected-kiosk "Bowls & Buns"
```

Outputs:

```text
final_project/data/processed/weekly_analysis.json
final_project/data/briefings/weekly_briefing.md
```

## Run the Stateful LangGraph Workflow

Install the project:

```bash
python -m pip install -e .
```

Start a safe demo run:

```bash
python final_project/src/shiftnotes/cli.py workflow-start \
  --thread-id week6-demo \
  --mode demo \
  --expected-kiosk "Bowls & Buns"
```

The graph pauses at the human-review interrupt. Inspect the persisted state from
a separate process:

```bash
python final_project/src/shiftnotes/cli.py workflow-status week6-demo
```

Resume with a human decision:

```bash
python final_project/src/shiftnotes/cli.py workflow-resume week6-demo approve
```

Correction and rejection are also supported:

```bash
python final_project/src/shiftnotes/cli.py workflow-resume week6-demo correct \
  --note "Treat poke mentions as guest requests, not confirmed demand."

python final_project/src/shiftnotes/cli.py workflow-resume week6-demo reject
```

Demonstrate retry and recovery:

```bash
python final_project/src/shiftnotes/cli.py workflow-start \
  --thread-id week6-retry \
  --mode demo \
  --simulate-failures 1 \
  --max-retries 2
```

The persistent SQLite checkpoint is stored under
`final_project/data/checkpoints/` and is excluded from Git.

See `final_project/WEEK6_ARCHITECTURE.md` for node roles and routing logic.

## Final Mock Dataset

The reproducible final dataset is stored in:

```text
final_project/data/final_mock/
```

It covers 12 weeks, six kiosks, 288 expected kiosk/date reports, 18 missing
reports, three malformed records, and three duplicate submissions. Ground truth
is stored separately from the JotForm payload for later benchmark evaluation.

Regenerate and validate it with:

```bash
python scripts/generate_final_mock_dataset.py
python -m pytest tests/test_final_mock_dataset.py
python final_project/src/shiftnotes/cli.py baseline
```

See `final_project/data/final_mock/DATASET_DESIGN.md` for the design rationale.

The baseline command creates schedule-aware reporting completeness, weekly and
monthly summaries, deterministic operational findings, source-level benchmark
results, and a readable briefing. It excludes duplicate and malformed records
before calculating operational metrics.

Generate the final weekly and monthly management briefing prototypes:

```bash
python final_project/src/shiftnotes/cli.py briefings
```

Outputs:

```text
final_project/data/final_mock/briefings/weekly/
final_project/data/final_mock/briefings/monthly/
```

See `final_project/BRIEFING_DESIGN.md` for the format rationale, guardrails, and
production interaction design.

## Product Workspace

Generate claim records and polished email previews:

```bash
python final_project/src/shiftnotes/cli.py product-assets
```

Run the Streamlit inspection workspace:

```bash
python -m streamlit run final_project/app.py
```

The email remains the primary interface. Streamlit provides briefing previews,
claim/source inspection, ordinary-English challenges, a second HITL correction
confirmation, safety refusals, and correction history.

See `final_project/PRODUCT_WORKFLOW.md` for the complete product behavior.

## Demo Path

The recommended final demo path is email-first:

1. Open a generated weekly email preview:

   ```text
   final_project/data/final_mock/email_previews/weekly/week_01.html
   ```

2. Open a generated monthly email preview:

   ```text
   final_project/data/final_mock/email_previews/monthly/2026-03.html
   ```

3. Point out that the email contains:

   - reporting completeness;
   - rating and waste metrics;
   - priority source-backed operational findings;
   - source IDs for inspection;
   - links for source review or claim challenge.

4. Run the supporting inspection workspace:

   ```bash
   python -m streamlit run final_project/app.py
   ```

5. In the workspace, inspect a claim source bundle and demonstrate the
   post-delivery correction flow:

   ```text
   Challenge claim -> propose correction -> human confirmation -> correction history
   ```

The dashboard is not the primary interface. It exists to support source
inspection, challenge/correction, and auditability after Ted receives a
briefing email.

## Run Groq Semantic Analysis

Groq interprets only the free-text fields. Python continues to calculate exact
ratings, counts, missing reports, duplicates, and period summaries.

Start with a three-report validation:

```bash
python final_project/src/shiftnotes/cli.py ai-run --limit 3
```

After inspecting the source-backed output, run the full dataset:

```bash
python final_project/src/shiftnotes/cli.py ai-run
```

The command validates exact evidence excerpts, retries malformed responses,
uses a deterministic fallback after repeated failure, caches successful model
results, and writes source-level precision/recall evidence.

See `final_project/MODEL_SELECTION_AND_BENCHMARK.md`.

## Test

From the repository root:

```bash
python -m pytest -q
```

## Current Scope

Implemented:

- Read JotForm credentials from `final_project/.env`
- Fetch form submissions from JotForm API
- Normalize JotForm submission answers into ShiftNotes records
- Normalize JotForm date objects into `YYYY-MM-DD`
- Validate required fields
- Save raw and processed JSON
- Generate deterministic weekly metrics
- Extract first-pass semantic signals from free-text fields
- Generate source-backed weekly briefing text
- Detect missing reports when expected kiosks are provided
- Run a stateful LangGraph workflow in demo or live mode
- Route ingestion through success, retry, or fallback branches
- Persist interrupted runs with SQLite
- Pause for human approval, correction, or rejection before finalization
- Extract semantic signals through Groq using a strict JSON schema
- Reject invented source IDs and unsupported evidence excerpts
- Retry failed model calls and route repeated failures to a deterministic fallback
- Cache successful model results by report content and model
- Benchmark AI categories against source-level synthetic ground truth
- Use saved AI semantic signals in weekly/monthly briefings and dashboard claims
- Generate monthly briefings
- Generate email previews
- Provide dashboard/source inspection

Not implemented yet:

- Email briefing delivery
- Production scheduler and hosted authentication
- Quota-aware full-dataset Groq backfill without fallback

## Known Limitations

- Email delivery is previewed locally as HTML/plain text; Gmail sending is not
  connected in this submission.
- The scheduler policy is represented in configuration, but no production cron,
  cloud job, or hosted scheduler is deployed.
- The final demo uses synthetic JotForm-shaped data rather than Ted's private
  production submissions.
- Groq semantic extraction works, but the full-dataset run hit the on-demand
  daily token limit and used deterministic fallback for unresolved batches.
- Challenge interpretation is deterministic/mock behavior behind a replaceable
  provider boundary; Groq-assisted correction interpretation is future work.
- Financial impact is described as a possible opportunity because meal cost,
  transaction volume, revenue, and labor-hour data are not inputs yet.
- The Streamlit workspace is a local inspection tool, not a hosted authenticated
  production dashboard.
- Source links point into the local inspection workflow rather than hosted
  source records or original JotForm emails.
