# ShiftNotes RAG App

Streamlit dashboard with hybrid signal detection and RAG-powered natural language querying.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## First-Time Index Build

The vector index builds automatically when you open the Ask ShiftNotes tab for the first time.

To build it manually in advance:

```bash
python embed.py
```

To index a custom CSV:

```bash
python embed.py --csv path/to/your/reports.csv
```

## Tabs

| Tab | Description |
|---|---|
| Kiosk Summary | Signal counts, ratings, and waste charts per kiosk |
| Weekly Trends | How operational patterns shift week over week |
| Briefings | Plain-text operational briefing for any selected week |
| Ask ShiftNotes | Natural language querying powered by ChromaDB + Claude API |

## API Key

The Ask ShiftNotes tab requires an Anthropic API key.

Enter it in the sidebar or set it as an environment variable:

```bash
export ANTHROPIC_API_KEY=your_key_here
```

## Stack

| Component | Tool |
|---|---|
| UI | Streamlit |
| Charts | Plotly |
| Signal detection | Regex + HuggingFace (signal_classifier.py) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector store | ChromaDB |
| Generation | Claude API (claude-sonnet-4-6) |
