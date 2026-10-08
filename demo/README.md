# ShiftNotes Demo

This folder contains the runnable ShiftNotes prototype.

The demo proves the core workflow:

```text
JotForm-style reports
-> clean ShiftNotes records
-> source-backed weekly/monthly briefings
-> Gmail delivery
-> optional Streamlit inspection and correction
```

The project documentation lives in `docs/`. Older class and team artifacts live
in `docs/archive/`.

## Setup

From the repository root, use the locked environment:

```powershell
uv sync --locked
uv run streamlit run streamlit_app.py
```

The bundled dashboard needs no credentials. For pip-based development instead:

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e . pytest
.venv/Scripts/python -m streamlit run streamlit_app.py
```

Only for live provider calls, copy the environment template. The remaining
commands assume the installed environment is active (or prefix them with `uv run`).

```bash
copy demo\.env.example demo\.env
```

Fill in the values you need:

```env
JOTFORM_API_KEY=your_api_key_here
JOTFORM_FORM_ID=your_form_id_here
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
GMAIL_CLIENT_SECRET_PATH=demo/google_credentials.json
GMAIL_TOKEN_PATH=demo/.gmail_token.json
GMAIL_DEFAULT_RECIPIENT=manager@example.com
```

Do not commit `.env`, Google credentials, or Gmail tokens.

## Run The Dashboard

```bash
python -m streamlit run streamlit_app.py
```

The hosted synthetic-data demo is available at:

```text
https://shiftnotes.streamlit.app
```

## Generate Demo Artifacts

```bash
python scripts/generate_final_mock_dataset.py
python demo/src/shiftnotes/cli.py baseline
python demo/src/shiftnotes/cli.py briefings
python demo/src/shiftnotes/cli.py product-assets --base-url http://localhost:8501
```

Outputs are written under:

```text
demo/data/final_mock/
```

Useful email previews:

```text
demo/data/final_mock/email_previews/weekly/week_01.html
demo/data/final_mock/email_previews/monthly/2026-03.html
```

## Fetch Live JotForm Data

This live path is separate from the bundled dashboard dataset. See
[integration boundaries](../docs/INTEGRATIONS.md). It does not automatically
replace dashboard reports or schedule background ingestion.

```bash
python demo/src/shiftnotes/cli.py fetch
python demo/src/shiftnotes/cli.py analyze
```

Outputs:

```text
demo/data/raw/jotform_submissions.json
demo/data/processed/reports.json
demo/data/processed/weekly_analysis.json
demo/data/briefings/weekly_briefing.md
```

## Run AI Semantic Extraction

Start small:

```bash
python demo/src/shiftnotes/cli.py ai-run --limit 3
```

Then run the full synthetic dataset when quota allows:

```bash
python demo/src/shiftnotes/cli.py ai-run
```

The semantic layer validates exact evidence excerpts, retries malformed
responses, falls back after repeated failure, caches successful outputs, and
benchmarks against source-level ground truth.

## Gmail Delivery

Authorize once:

```bash
python demo/src/shiftnotes/cli.py gmail-auth
```

Preview without sending:

```bash
python demo/src/shiftnotes/cli.py gmail-preview --type weekly --period week-01
```

Send with explicit confirmation:

```bash
python demo/src/shiftnotes/cli.py gmail-send --type weekly --period week-01 --confirm-send
```

ShiftNotes requests only the `gmail.send` scope. It does not read the mailbox.

## Test

```bash
python -m pytest -q
```

## Related Docs

- [Documentation index](../docs/README.md)
- [Demo guide](../docs/DEMO_GUIDE.md)
- [Prototype status](../docs/PROTOTYPE_STATUS.md)
- [Architecture](../docs/ARCHITECTURE_OVERVIEW.md)
- [Product workflow](../docs/PRODUCT_WORKFLOW.md)
- [Model evaluation](../docs/MODEL_SELECTION_AND_BENCHMARK.md)
