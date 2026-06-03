# RAG BACKLOG

# Purpose

This document captures the planned RAG (Retrieval-Augmented Generation) implementation for ShiftNotes.

The current prototype uses rule-based signal detection, which only finds patterns it was explicitly programmed to look for.

RAG would allow leadership to ask any operational question in plain English and receive an answer grounded in actual historical shift reports.

---

# What RAG Enables

Instead of predefined signals, Ted could ask:

* What food issues occurred at Kiosk D in week 3?
* Which employee has been recognized the most this month?
* How has waste at Kiosk B changed over time?
* What guest complaints came up more than once?
* Which shifts had the most operational friction?

---

# Proposed Flow

```text
Shift Reports (JotForm → Gmail)
      ↓
Node 1 — ingest_email (MCP Gmail reads → CSV)
      ↓
Node 2 — classify_intent (route: shift report or query)
      ↓
Node 3 — detect_signals (Hybrid regex + HuggingFace)
      ↓
Node 4 — retrieve_and_generate (ChromaDB + Groq RAG)
      ↓
Node 5 — send_briefing (MCP Gmail → Ted's inbox)
      ↓
Node 6 — human_review (Ted reads email ← HITL 1)
      ↓
Ted satisfied? → Take action → END
Ted not satisfied? → Reply to ShiftNotes → RAG answers
Ted still not ok? → Order ShiftNotes to email shift lead
      ↓
Node 7 — draft_escalation (ShiftNotes drafts email)
      ↓
Ted approves draft ← HITL 2
      ↓
MCP Gmail sends to shift lead → cross-check → pipeline restarts
```

---

# Technology Stack

| Component | Tool | Reason |
| --- | --- | --- |
| Embeddings | sentence-transformers | Free, runs locally, no API key required |
| Vector store | ChromaDB | Lightweight, local, no server required |
| Metadata filtering | ChromaDB built-in | Filter by kiosk, week, or date before search |
| Generation | Groq API (llama-3.3-70b-versatile) | Answer questions using retrieved report context |
| Orchestration | LangGraph | Manages node execution, routing, and HITL interrupts |
| Email delivery | MCP Gmail | Reads JotForm emails and sends briefings to Ted |

---

# To-Do List

## 1. Embed the Reports

- Use `sentence-transformers` to embed the `full_text` column
- One report = one document (no chunking needed — reports are short)
- Output: one embedding vector per report

---

## 2. Set Up Vector Store

- Use ChromaDB to store embeddings locally
- Attach metadata to each document: `kiosk`, `week`, `date`, `lead_name`
- Metadata enables targeted filtering before semantic search runs
- Use PersistentClient to avoid re-embedding on every notebook restart:
  chroma_client = chromadb.PersistentClient(path="./chroma_db")
  Add chroma_db/ to .gitignore

---

## 3. Build a Query Function

- Input: natural language question plus optional filters (kiosk, week, date range)
- Step 1: apply metadata filters if provided
- Step 2: run semantic search against filtered subset
- Step 3: return top-N most relevant reports as context

---

## 4. Connect Claude API

- Send retrieved reports plus the original question to Claude
- Claude generates a grounded answer citing specific report content
- Use prompt caching for repeated context to reduce latency and cost

---

## 5. Test Sample Questions

Validate against the mock dataset using these example queries:

* What food issues occurred at Kiosk D in week 3?
* Which employee has been recognized the most?
* How has waste at Kiosk B changed over time?
* What guest complaints came up more than once?
* Which kiosk had the most operational concerns?

---

## 6. Add RAG as Step 9 in the Notebook

- Keep the existing 8-step pipeline intact
- Add Step 9 as an interactive query demonstration cell
- Demonstrate these 3 sample questions with generated answers:
    1. What food issues occurred at Kiosk D in week 3?
    2. Which employee has been recognized the most?
    3. What guest complaints came up more than once?
  - Each answer must cite the report_id and kiosk it was retrieved from

---

## 7. Acceptance Criteria

RAG will be considered working if:

- Answers are grounded — every answer references specific report content, not general knowledge
- Retrieval is relevant — top-3 retrieved reports are related to the question asked
- Sample questions pass — at least 4 out of 5 sample questions return accurate answers
- No hallucination — Claude does not invent kiosk names, employee names, or dates not in the data
- HITL 2 works — Ted can review and approve draft email before it is sent to shift lead
- Email delivery works — Ted receives weekly briefing in Gmail inbox

---

# Notes

The existing signal classifier stays in place.

RAG adds ad-hoc natural language querying on top of the pipeline — not instead of it.

The `full_text` column built in Step 3 of the notebook is already the correct input for embedding.

---

## Email Workflow

Ted interacts with ShiftNotes primarily through email:

- Ted receives weekly briefing email from shiftnotes@gmail.com
- Email contains summary of all kiosks with mailto links
- Ted clicks link → Gmail opens with pre-filled subject
- ShiftNotes reads reply via MCP Gmail → Node 2 routes to RAG
- RAG answers and sends reply back to Ted

### mailto Link Example

Each briefing email contains:
- "Tell me more about Kiosk D" → mailto:shiftnotes@gmail.com?subject=Tell me more about Kiosk D
- "Flag this briefing" → mailto:shiftnotes@gmail.com?subject=Flag Week 4 briefing
- "Open Streamlit" → link to Streamlit app for drill-down

---

## Secrets and API Key Management

- Local development: store ANTHROPIC_API_KEY in a .env file using python-dotenv
- Streamlit deployment: store key in Streamlit Secrets (st.secrets)
- Never hardcode API keys in source files
- Add .env to .gitignore before first commit

---

# Deployment — Streamlit

The final app can be deployed on Streamlit.

## What Maps to Streamlit

| ShiftNotes Feature | Streamlit Component |
| --- | --- |
| Upload shift reports (CSV) | st.file_uploader() |
| Signal detection results | st.dataframe() |
| Kiosk summary charts | st.bar_chart() / Plotly |
| Weekly trend charts | st.line_chart() |
| Operational briefings | st.text() / st.markdown() |
| RAG query input | st.text_input() + Claude API |
| Per-kiosk drill-down | st.selectbox() sidebar |

---

## One Concern

The HuggingFace model (~330MB) loads slowly on first run.

Streamlit Community Cloud has a 1GB memory limit which may be tight.

Fix: wrap the model load with `@st.cache_resource` so it loads once and stays in memory across interactions.

- Fallback: if memory exceeds 1GB limit, replace local HuggingFace model
  with the HuggingFace Inference API (no local model download required)

---

## Deployment Path

```text
GitHub repo
    ↓
Streamlit Community Cloud (free)
    ↓
Connect repo → deploy in ~2 minutes
```

No server setup needed.

---

## Recommendation

For the prototype demo — Streamlit is the right choice.

It converts the Jupyter notebook into a shareable web app with minimal additional code.

For production with live JotForm integration, Streamlit remains a valid front-end with a separate backend pipeline handling ingestion.
