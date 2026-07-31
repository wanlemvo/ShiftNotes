from typing import TypedDict, Optional
from datetime import datetime


class ShiftNotesState(TypedDict):
    """State container for the ShiftNotes pipeline."""

    # --- Input ---
    raw_reports: list[dict]        # reports ingested from email
    intent: str                    # "signals" or "rag_query"

    # --- Signal Detection ---
    detected_signals: list[dict]   # output from detect_signals node

    # --- RAG ---
    retrieved_context: str         # relevant past reports from ChromaDB
    generated_briefing: str        # final briefing text from OpenAI

    # --- Human Review ---
    briefing_sent: bool            # did Node 5 send the email?
    ted_decision: Optional[str]    # "accept", "drill_down", or "escalate"
    escalation_note: Optional[str]  # Ted's note if escalating

    # --- Meta ---
    run_id: str                    # unique ID for this pipeline run
    timestamp: str                 # when the run started
    error: Optional[str]           # captures any failure in the pipeline