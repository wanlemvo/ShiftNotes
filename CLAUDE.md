# ShiftNotes — Agent Pipeline

## Setup

1. Clone the repo
2. Install uv if not already: `pip install uv`
3. Install dependencies: `uv sync`
4. Copy `.env.example` to `.env` and add your OpenAI API key
5. Run the pipeline: `uv run python run_pipeline.py`

## Project Structure

- `shiftnotes_agent/` — LangGraph agent pipeline
  - `nodes/` — one file per graph node
  - `tools/` — signal classifier
  - `state.py` — shared state definition
  - `graph.py` — graph wiring and compilation
  - `logger.py` — structured logging
- `prototype/` — original Jupyter notebook prototype
- `run_pipeline.py` — end-to-end demo runner
- `briefings/` — generated briefing output files

## Running the demo

```bash
uv run python run_pipeline.py
```

When prompted, enter one of: `accept` | `drill_down` | `escalate`

## Environment variables

| Variable | Description |
|---|---|
| OPENAI_API_KEY | Your OpenAI API key |

## Notes

- Gmail MCP integration is stubbed in Node 1 and Node 5
- HuggingFace model downloads ~330MB on first run
- ChromaDB persists to `chroma_db/` folder locally