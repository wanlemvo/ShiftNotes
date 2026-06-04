# BACKLOG

## Week 8 — Completed Items

- Completed the Week 8 checkpoint deliverable by updating the specification and architecture documentation.
- Transitioned the active design from the original Jupyter notebook prototype to a LangGraph agent pipeline.
- Defined the six-node pipeline:
  - `ingest_email`
  - `classify_intent`
  - `detect_signals`
  - `retrieve_and_generate`
  - `send_briefing`
  - `human_review`
- Documented the Gmail MCP integration plan and identified the two MCP swap points: Node 1 ingestion and Node 5 briefing delivery.
- Added a known risks document with Week 9 risk tracking.
- Preserved the notebook-based prototype in `prototype/` while making the agent pipeline the primary architecture.
- Created and updated `SPEC.MD` and `ARCHITECTURE.md` to reflect the current LangGraph design, HITL checkpoint, RAG pipeline, and MCP integration.
- Added a RAG backlog and roadmap in `prototype/ROADMAP.md` for future retrieval-augmented generation work.

## Week 9 — Planned Priorities

- Populate ChromaDB with indexed reports and validate that RAG retrieval context is available.
- Tune the hybrid signal classifier on sample real JotForm data, adjusting regex patterns and model thresholds as needed.
- Prototype the Streamlit drill-down review interface for Ted to inspect details when he requests it.
- Validate the full LangGraph execution path, including the human review checkpoint and decision routing.
- Confirm that briefing delivery works reliably with Gmail MCP and falls back cleanly to file output when needed.
- Continue documenting risks, limitations, and progress so the next checkpoint remains aligned with the project plan.

## Week 9 QA Checkpoint Artifacts

The Week 9 submission will include the following artifacts:

- Peer review feedback received and response actions taken.
- HITL validation evidence with a non-team user.
- Backlog completion report targeting 80% or more of planned work.
- Technical report draft covering sections 1 through 3.

### Artifact integration plan

- Collect peer review notes on the LangGraph architecture, MCP plan, and risk/backlog documentation.
- Capture non-team HITL validation using a structured checklist and evidence notes.
- Track completed backlog items as a percentage of planned Week 9 priorities.
- Draft the first three sections of the technical report to document architecture, implementation, and validation approach.
