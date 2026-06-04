# ShiftNotes Specification

## Purpose

ShiftNotes is an AI-driven operational intelligence prototype that transforms freeform shift reports into structured signals, trend summaries, and actionable briefings.

The goal is to augment existing reporting workflows by extracting recurring operational patterns and surfacing the most important information for leadership.

---

## Problem Statement

Shift leads submit daily operational reports that capture food quality, inventory concerns, guest feedback, team performance, and operational issues.

Those reports are often delivered as email form submissions and reviewed manually, which makes historical analysis and trend detection slow, inconsistent, and prone to information loss.

ShiftNotes solves this by turning routine operational reporting into searchable intelligence and automated briefings.

---

## Product Vision

ShiftNotes should preserve the current intake workflow while reducing the manual effort required to:

- identify recurring issues
- detect operational trends
- summarize meaningful observations
- surface action items for leadership

It should behave as a passive intelligence layer rather than a new operational burden.

---

## Scope

### In scope for the prototype

- ingest synthetic shift reports representing daily kiosk operations
- transform unstructured report text into signal detections
- aggregate results by kiosk and weekly periods
- validate output against planted ground-truth patterns
- generate text-based operational briefings

### Out of scope for the prototype

- persistent database storage
- email delivery or dashboard UI
- active natural language querying
- predictive forecasting or autonomous scheduling
- multi-location comparison beyond the synthetic kiosk dataset

---

## Users

### Primary

- Operations leadership (e.g. general manager)
- Managers who need fast operational summaries
- Shift leads who submit reports but should not change behavior

### User needs

- understand what happened without reading every report
- identify which issues are recurring
- see where attention is most needed
- quickly consume a summary of key signals and trends

---

## Inputs

- synthetic `mock_shift_notes.csv`
- daily shift report fields such as:
  - kiosk
  - date
  - lead name
  - food quality ratings
  - food concerns or outages
  - guest issues
  - operational notes
  - team recognition entries

- ground truth validation file `ground_truth_targets.csv`

---

## Outputs

- signal classification per report
- audit trail showing regex and model-based detections
- kiosk-level and weekly aggregated metrics
- text-based weekly/daily briefings summarizing trends

---

## Core Signals

ShiftNotes prototype detects four primary operational signals:

- `chicken_shortage`: protein or menu item shortages during service
- `poke_request`: guest requests for poke or missing menu items
- `ops_issue`: equipment failures, supply delays, or workflow bottlenecks
- `team_recognition`: explicit positive recognition of team members

---

## Architecture

### Pipeline Overview

1. load synthetic shift reports
2. clean and combine text fields into a single signal input
3. run hybrid signal classification
   - regex fast-path
   - HuggingFace zero-shot fallback
4. aggregate signals by kiosk and week
5. validate results against ground truth patterns
6. generate operational briefing text

### Components

- `shiftnotes_agent/` — prototype agent pipeline files
- `prototype/` — initial notebook and synthetic dataset
- `prototype/signal_classifier.py` — hybrid signal detection module
- `prototype/ShiftNotes_Prototype.ipynb` — end-to-end prototype demonstration
- `run_pipeline.py` — execution entry point for the pipeline
- `streamlit_app.py` — future UI integration point

---

## Week 8 Checkpoint

### Agent Architecture Decisions

- ShiftNotes is implemented as a LangGraph agent pipeline with modular nodes for ingestion, intent classification, signal detection, retrieval/generation, briefing delivery, and human review.
- The current pipeline preserves the notebook prototype while adding an orchestration layer for agent-style execution and checkpoints.
- Node responsibilities:
  - `ingest_email`: ingest JotForm reports via Gmail MCP stub, with CSV fallback for offline development
  - `classify_intent`: route inputs as shift reports or conversational queries
  - `detect_signals`: apply hybrid regex + HuggingFace signal classification
  - `retrieve_and_generate`: aggregate context and generate briefing text
  - `send_briefing`: send output via Gmail MCP or fallback to file
  - `human_review`: provide a HITL checkpoint for Ted before final delivery
- The architecture intentionally keeps the signal classifier and validation modules separate from the delivery mechanism.

### MCP Integration Plan

- The primary MCP integration points are Node 1 (`ingest_email`) and Node 5 (`send_briefing`).
- `ingest_email` will swap `_read_from_csv()` with a Gmail MCP read call to ingest JotForm-based emails.
- `send_briefing` will swap `_save_to_file()` with a Gmail MCP send call to deliver briefings to Ted's inbox.
- The MCP connector will use the Gmail MCP endpoint and OAuth credentials configured in the local environment.
- Early development uses a fallback path so the pipeline can run without completed Gmail MCP wiring.

### Current Prototype Limitations

- The dataset is synthetic and not yet validated against real JotForm inputs.
- Signal detection relies on a small set of hand-authored patterns and a fallback zero-shot model.
- Gmail MCP is not fully wired; the pipeline currently uses CSV and file output stubs for ingestion and delivery.
- The UI layer is not built; briefings are generated as plain text files rather than delivered through a production interface.
- ChromaDB remains empty until reports are indexed; semantic retrieval and RAG are not yet active in the current prototype.
- First-run HuggingFace model download is large (~330MB), which may slow onboarding.
- Thresholds for signal detection may require tuning when switched from synthetic data to real shift reports.

### Week 9 Priorities

- Wire Gmail MCP for Node 1 ingestion and Node 5 briefing delivery, then validate end-to-end Gmail flows.
- Populate ChromaDB with indexed reports and verify RAG context is available instead of empty context.
- Test and tune signal classifier thresholds using sample real JotForm data.
- Build or prototype a Streamlit drill-down UI to support detail review for Ted.
- Document known risks, backlog items, and the MCP integration plan for the next checkpoint.

---

## Signal Detection Strategy

### Regex Fast-Path

- text is scanned using predefined patterns for each signal
- deterministic matches are accepted immediately

### HuggingFace Zero-Shot Fallback

- when regex does not fire, the system uses `cross-encoder/nli-MiniLM2-L6-H768`
- each signal has a threshold for acceptance
- signals are confirmed only when model confidence meets the threshold

### Thresholds

- `chicken_shortage`: 0.70
- `poke_request`: 0.50
- `ops_issue`: 0.70
- `team_recognition`: 0.95

---

## Validation

- compare pipeline output to `ground_truth_targets.csv`
- confirm counts for known planted patterns
- verify operational signatures across six kiosks

---

## Success Criteria

The prototype is successful if it can:

- extract meaningful operational signals from freeform reports
- identify recurring patterns in the synthetic dataset
- generate briefings that summarize important insight clearly
- provide a transparent audit trail for each detected signal

---

## Current Limitations

- dataset is synthetic and not yet connected to real submissions
- signal detection is rule-focused with only a fallback model
- no formal persistence, search, or UI layer
- briefings remain plain text and not yet delivered automatically

---

## Future Vision

Future versions of ShiftNotes may evolve to include:

- automated ingestion from JotForm or email APIs
- persistent historical storage and retrieval
- advanced LLM-based extraction and retrieval-augmented generation
- natural language querying of operational memory
- formatted email briefings and dashboards
- multi-location trend comparison and forecasting

---

## Glossary

- `report`: a single shift submission
- `signal`: a detected operational pattern or issue
- `briefing`: a generated operational summary
- `audit trail`: metadata describing how a signal was detected
- `ground truth`: expected values used to validate the prototype output
