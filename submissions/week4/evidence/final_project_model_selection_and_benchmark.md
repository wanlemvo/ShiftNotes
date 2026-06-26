# Model Selection and Benchmark Plan

## Decision

ShiftNotes uses a hybrid analysis architecture:

- Python handles exact calculations, dates, ratings, report completeness,
  duplicate detection, and unclaimed-lunch totals.
- Groq handles semantic interpretation of the four free-text JotForm fields.
- LangGraph coordinates stateful workflows and human review.

The default semantic model is `openai/gpt-oss-20b` through Groq. It was selected
because Groq lists it as a production model and supports strict structured
outputs for it. The model can be changed with `GROQ_MODEL` without changing the
rest of the pipeline.

## Why AI Is Limited to Free Text

Ratings and counts do not require model interpretation. Sending them to a model
would add cost and create opportunities for arithmetic errors. The model only
receives:

- food concerns or outages;
- team members who did well;
- guest issues for the day;
- operational notes;
- source ID, kiosk, and date for traceability.

## Output Contract

Groq must return strict JSON with:

- one result for every requested source ID;
- zero or more categorized semantic signals;
- severity and confidence;
- the exact source field;
- an exact evidence excerpt;
- a sensitivity flag;
- a short rationale.

ShiftNotes rejects a response when:

- source IDs are missing, duplicated, or invented;
- the response violates the schema;
- an evidence excerpt is not an exact substring of the named source field.

The system retries failed batches up to a configured limit. Repeated failure
routes to the deterministic baseline. Fallback results are not stored as Groq
cache entries, so a temporary outage cannot silently replace later model work.
The default request size is one report because live validation showed that
multi-report generation could preserve the intended signals while malformed
the outer JSON structure. Per-report requests favor reliability and remain
economical because successful results are cached by content.
The prompt version is part of the cache key, ensuring that taxonomy or safety
improvements trigger a fresh extraction instead of reusing stale output.

## Benchmark Design

The synthetic dataset contains deliberately planted operational patterns with
source-level ground truth. AI output is compared by category and source ID.

Metrics:

- true positives;
- false positives;
- missed source reports;
- precision;
- recall;
- unavailable records caused by data quality or run scope;
- token usage, latency, retries, cache hits, and fallback usage.
- estimated API cost using the documented model rates at implementation time.

The deterministic baseline remains the control. Groq should only become the
default semantic source after its benchmark demonstrates useful recall without
unacceptable unsupported claims.

## Controlled Live Validation

On June 22, 2026, the first six valid synthetic reports were processed through
`openai/gpt-oss-20b` using one report per strict request.

Results:

- reports processed: 6;
- successful Groq requests: 6;
- retries: 0;
- fallback batches: 0;
- prompt tokens: 4,950;
- completion tokens: 5,663;
- measured latency: 30.2595 seconds;
- estimated API cost: $0.002070;
- source-level micro precision: 100%;
- source-level micro recall: 100%.

The validation also demonstrated why benchmark scope matters. The model found
legitimate employee praise, portion feedback, and beverage requests outside
some deliberately planted trend windows. Those findings are retained as valid
out-of-scope detections rather than mislabeled as hallucinations.

This is evidence that the integration and evaluation design work. It is not a
claim that the model has achieved 100% accuracy over the complete dataset.

## Expanded Live Validation

On June 23, 2026, the validation scope was expanded to the first 24 valid
synthetic reports.

Results:

- reports processed: 24;
- cache hits: 21;
- new Groq request batches: 3;
- retries: 1;
- fallback batches: 0;
- prompt tokens: 2,475;
- completion tokens: 3,153;
- measured latency: 38.8826 seconds;
- estimated API cost for this run: $0.001132;
- source-level micro precision: 100%;
- source-level micro recall: 100%.

The single retry was caused by a Groq tokens-per-minute rate limit and recovered
without fallback. This is useful evidence for the self-correction/recovery
story: the system can pause, retry, and continue without replacing model output
with deterministic fallback when the provider recovers.

The 24-report benchmark is stronger than the six-report smoke test, but it still
does not represent complete-dataset accuracy. The next benchmark step is a full
run across all valid synthetic reports.

## Complete-Dataset Attempt

On June 23, 2026, ShiftNotes ran the semantic extraction command across the full
valid synthetic dataset.

Results:

- reports processed: 270;
- cache hits: 24;
- new request batches attempted: 246;
- retries: 278;
- fallback batches: 136;
- prompt tokens: 90,679;
- completion tokens: 103,967;
- measured provider latency: 1179.3528 seconds;
- estimated API cost for billed successful calls: $0.037991;
- source-level micro precision: 92.17%;
- source-level micro recall: 97.45%.

This result is useful but must be interpreted carefully. The run exhausted the
Groq on-demand daily token limit before all reports could receive model output.
ShiftNotes retried provider failures and then used the deterministic fallback
for unresolved batches, so the full-dataset artifact is a mixed AI/fallback
artifact rather than a pure Groq benchmark.

The key production lesson is that semantic extraction works, but full backfills
need one of these controls:

- run in smaller scheduled batches;
- wait for quota reset before continuing uncached reports;
- use a higher service tier;
- treat deterministic fallback as a visibly labeled recovery path, not hidden AI
  output.

After this run, generated weekly/monthly briefings and the dashboard claim
catalog were connected to `ai_extractions.json`. When that file exists,
ShiftNotes uses semantic signals for source-backed trends while deterministic
Python still owns ratings, dates, missing reports, duplicate detection, and
waste totals.

## Responsible AI Controls

- Every signal requires source evidence.
- Personnel allegations are marked sensitive.
- The model cannot recommend discipline or termination.
- Exact operational metrics remain deterministic.
- Manager corrections require confirmation before persistence.
- Cached requests are keyed by model and report content.
- API keys remain in the ignored local `.env` file.

## Reproduce

Add these values to `final_project/.env`:

```env
GROQ_API_KEY=your_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

Run a small validation first:

```bash
python final_project/src/shiftnotes/cli.py ai-run --limit 3
```

Then run the complete benchmark:

```bash
python final_project/src/shiftnotes/cli.py ai-run
```

Generated artifacts:

```text
final_project/data/final_mock/ai_extractions.json
final_project/data/final_mock/ai_run_summary.json
final_project/data/final_mock/ai_benchmark_results.json
```

Official references:

- https://console.groq.com/docs/structured-outputs
- https://console.groq.com/docs/models
- https://console.groq.com/docs/rate-limits

Pricing is treated as configurable evidence, not a permanent guarantee. The
implementation-time estimate for `openai/gpt-oss-20b` uses $0.075 per million
input tokens and $0.30 per million output tokens.
