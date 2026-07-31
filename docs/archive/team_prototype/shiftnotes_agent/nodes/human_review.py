from langgraph.types import interrupt

from shiftnotes_agent.state import ShiftNotesState
from shiftnotes_agent.logger import get_logger, log_node_entry, log_node_exit, log_error

logger = get_logger("human_review")


def human_review(state: ShiftNotesState) -> ShiftNotesState:
    run_id = state.get("run_id", "unknown")
    log_node_entry(logger, "human_review", run_id)

    try:
        if state.get("error"):
            return state

        if not state.get("briefing_sent"):
            log_node_exit(logger, "human_review", run_id, "skipped — no briefing sent")
            return state

        briefing = state.get("generated_briefing", "")

        # --- HITL interrupt ---
        # LangGraph pauses here and waits for human input.
        # The graph state is saved. Execution resumes when
        # Ted responds with his decision.
        # before proceeding.
        ted_response = interrupt({
            "message": "Briefing has been delivered to Ted. Awaiting his decision.",
            "briefing_preview": briefing[:200] + "...",
            "options": ["accept", "drill_down", "escalate"],
            "instructions": "Reply with one of: accept | drill_down | escalate"
        })

        # Parse Ted's decision
        decision = ted_response.get("decision", "").lower().strip()

        if decision not in ["accept", "drill_down", "escalate"]:
            decision = "accept"  # default if unclear

        escalation_note = ted_response.get("note", "") if decision == "escalate" else None

        log_node_exit(logger, "human_review", run_id, f"ted_decision={decision}")

        return {
            **state,
            "ted_decision": decision,
            "escalation_note": escalation_note
        }

    except Exception as e:
        # Don't catch interrupt — let LangGraph handle it
        if "interrupt" in str(type(e).__name__).lower():
            raise
        log_error(logger, "human_review", run_id, str(e))
        return {
            **state,
            "error": f"human_review failed: {str(e)}"
        }