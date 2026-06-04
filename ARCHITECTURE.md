# ARCHITECTURE

## Purpose

This document describes the current ShiftNotes architecture after the Week 8 transition from a notebook prototype to a LangGraph agent pipeline.

ShiftNotes is now explicitly designed as a six-node LangGraph workflow with a human-in-the-loop checkpoint and Gmail MCP integration points.

---

# System Overview

ShiftNotes is implemented as a LangGraph agent pipeline that ingests shift report email content, detects operational signals, optionally performs retrieval-augmented generation, delivers briefings, and then pauses for Ted's review.

The architecture is intentionally modular, with clear separation between:

- data ingestion
- intent routing
- signal detection
- retrieval and generation
- delivery
- human review

---

# High-Level Data Flow

```text
Shift lead writes report
    ↓
JotForm → Gmail inbox
    ↓
Node 1 — ingest_email
    ↓
Node 2 — classify_intent
    ↓
Node 3 — detect_signals
    ↓
Node 4 — retrieve_and_generate (RAG)
    ↓
Node 5 — send_briefing
    ↓
Node 6 — human_review (HITL)
    ↓
Ted either accepts, drills down, or escalates
```

---

# The 6-Node Pipeline

## Node 1 — ingest_email

**Role:** Ingests incoming JotForm report emails.

- **Current implementation:** Reads from `mock_shift_notes.csv`
- **Goal:** Swap the CSV fallback with Gmail MCP reads
- **Output:** Structured report records added to pipeline state

### MCP integration point

- Replace `_read_from_csv()` with a Gmail MCP email read call
- This node is the primary live-input gateway for the agent

---

## Node 2 — classify_intent

**Role:** Determines whether the pipeline is handling a report signal batch or a conversational RAG query.

- **Input:** ingested report data or incoming user query
- **Output:** intent label `signals` or `rag_query`
- **Routing:** `signals` → Node 3, `rag_query` → Node 4

---

## Node 3 — detect_signals

**Role:** Detects operational signals from shift report text.

- **Detection approach:** hybrid regex fast-path plus HuggingFace zero-shot fallback
- **Signals:**
  - `chicken_shortage`
  - `poke_request`
  - `ops_issue`
  - `team_recognition`

### Implementation details

- Regex stage captures deterministic cases and short-circuits the model call
- HuggingFace stage uses `cross-encoder/nli-MiniLM2-L6-H768`
- Per-signal thresholds ensure conservative classification

### Thresholds

| Signal | Threshold |
|--------|-----------|
| `chicken_shortage` | 0.70 |
| `poke_request` | 0.50 |
| `ops_issue` | 0.70 |
| `team_recognition` | 0.95 |

---

## Node 4 — retrieve_and_generate (RAG)

**Role:** Retrieves relevant historical context and generates plain-English briefing content.

- **Retrieval:** ChromaDB vector search over indexed reports
- **Generation:** OpenAI prompt-based briefing construction

### Important note

ChromaDB is empty until reports are indexed. When empty, RAG context is unavailable and the system falls back to current briefing generation behavior.

---

## Node 5 — send_briefing

**Role:** Delivers generated briefings to Ted.

- **Current implementation:** Saves briefings to `briefings/`
- **Goal:** replace file output with Gmail MCP send
- **MCP integration point:** `_save_to_file()` → Gmail MCP send call
- **Gmail MCP URL:** `https://gmailmcp.googleapis.com/mcp/v1`

---

## Node 6 — human_review (HITL)

**Role:** Provides the human-in-the-loop checkpoint after briefing delivery.

- **Input:** delivered briefing
- **Output:** Ted's decision logged for downstream action

### Decision paths

| Decision | Result |
|----------|--------|
| `accept` | Ted understands and takes action |
| `drill_down` | Ted opens Streamlit review interface (pending) |
| `escalate` | Ted requests source verification, pipeline restarts |

This design preserves the product principle that intelligence should be delivered passively and then reviewed, rather than requiring Ted to request it first.

---

# Project Structure

```
ShiftNotes/
├── prototype/                  ← original notebook prototype
├── shiftnotes_agent/           ← LangGraph agent pipeline
│   ├── nodes/
│   │   ├── ingest_email.py
│   │   ├── classify_intent.py
│   │   ├── detect_signals.py
│   │   ├── retrieve_and_generate.py
│   │   ├── send_briefing.py
│   │   └── human_review.py
│   ├── tools/
│   │   └── signal_classifier.py
│   ├── graph.py
│   ├── state.py
│   └── logger.py
├── briefings/                  ← generated briefing files
├── run_pipeline.py            ← pipeline entrypoint
├── streamlit_app.py           ← future drill-down UI
├── RISKS.md                   ← known risks list
├── SPEC.MD                    ← current specification
├── README.md
├── PRODUCT_VISION.md
└── pyproject.toml
```

---

# Technology Stack

| Aspect | Technology |
|--------|------------|
| Orchestration | LangGraph |
| HITL | LangGraph interrupt |
| Signal detection | Regex + HuggingFace Transformers |
| Zero-shot model | cross-encoder/nli-MiniLM2-L6-H768 |
| Retrieval | ChromaDB |
| Briefing generation | OpenAI |
| Email integration | Gmail MCP (pending) |
| Drill-down UI | Streamlit (pending) |

---

# MCP Integration Points

| Node | Current behavior | MCP target |
|------|------------------|------------|
| Node 1 — ingest_email | CSV read fallback | Gmail MCP email ingestion |
| Node 5 — send_briefing | Save file in `briefings/` | Gmail MCP send to Ted |

Both integration points are designed as isolated swaps so that the LangGraph pipeline remains unchanged.

---

# Current Limitations

- Gmail MCP is not fully wired yet; the pipeline uses CSV stubs for ingestion and file output for briefing delivery.
- ChromaDB is empty until the first reports are indexed, so RAG retrieval is not available immediately.
- The HuggingFace model download is large (~330MB) on first run and requires stable internet.
- Signal detection thresholds are tuned for synthetic data and may need adjustment for real JotForm reports.
- The Streamlit drill-down experience is not implemented yet; Option A is still pending.

---

# Week 9 Priorities

- Populate ChromaDB and validate RAG retrieval.
- Tune signal thresholds against real JotForm sample data.
- Prototype the Streamlit drill-down review interface.
- Validate end-to-end LangGraph execution with HITL.

---

# Notes

The original notebook prototype remains available under `prototype/` for reference, but the active architecture now centers on the LangGraph agent pipeline.
