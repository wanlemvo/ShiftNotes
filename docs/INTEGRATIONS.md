# Integrations and Data Boundaries

## Supported Inputs

| Input | Current support | Boundary |
| --- | --- | --- |
| JotForm API | Implemented | One configured form; known labels; CLI fetch retrieves one limited page |
| Bundled JotForm-shaped JSON | Implemented | Synthetic demonstration and repeatable evaluation |
| Normalized ShiftNotes JSON | Supported by analysis code | Must already conform to the internal schema |
| Google Forms | Not implemented | Needs a connector/importer, authorization, mapping, and tests |
| Microsoft Forms / Typeform / other forms | Not implemented | Provider-specific ingestion and mapping needed |
| Arbitrary CSV / spreadsheet | No general importer | Generated CSV is an output, not universal upload support |
| Gmail inbox parsing / Gmail MCP | Not implemented in the active app | Gmail API sends briefing emails only |

The analysis can be reused for another form platform once its data is converted.
That possibility should not be advertised as existing compatibility. Even a new
JotForm needs field mapping if its questions differ from the aliases in
[normalize.py](../demo/src/shiftnotes/normalize.py).

## Internal Record

A `ShiftReport` contains source submission ID, submission timestamp, shift date,
kiosk, lead name, quality and quantity ratings (1-5), food concerns, recognition,
guest issues, operational notes, and a nonnegative unclaimed-lunch count. Parse
status and validation errors accompany the record. Missing reporting dates are
calculated against a separate kiosk/date schedule.

A future connector must preserve source identity and original text, normalize
dates and ratings, map kiosk names, flag incomplete records, and be tested against
realistic fixtures. Source references need provider identity before multiple
platforms coexist. No menu or financial facts should be inferred from absent data.

## What Runs Today

```powershell
uv run python demo/src/shiftnotes/cli.py fetch
uv run python demo/src/shiftnotes/cli.py analyze
```

These commands use `demo/.env` and write raw data, normalized records, basic
analysis, and a Markdown briefing under ignored local directories in `demo/data/`.
`fetch --limit` selects the requested page size; automatic pagination, incremental
syncing, and scheduled polling are not wired.

The richer `baseline`, `ai-run`, `briefings`, `product-assets`, and `gmail-*`
commands default to `demo/data/final_mock/`. The dashboard also reads that
directory. They do **not** automatically consume the latest `fetch` output.
Preparing a live dataset, its expected schedule, and its generated assets is
additional integration work. Do not overwrite the public synthetic fixture with
private workplace reports.

## Outputs and Authorization

Groq supplies semantic extraction when configured; deterministic fallback is
retained. Existing full-dataset evaluation includes both provider output and
fallback after rate limits. See [model evaluation](MODEL_SELECTION_AND_BENCHMARK.md).

Gmail sends multipart HTML/plain-text briefings through Desktop OAuth with
`gmail.send`. It does not read, label, or move incoming messages. The send command
requires `--confirm-send`. OAuth credentials, tokens, API keys, and live reports
stay outside Git. Weekly/monthly scheduling is metadata, not a background job.
