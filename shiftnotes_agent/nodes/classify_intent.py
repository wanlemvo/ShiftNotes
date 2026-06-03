from shiftnotes_agent.state import ShiftNotesState
from shiftnotes_agent.logger import get_logger, log_node_entry, log_node_exit, log_error

logger = get_logger("classify_intent")


def classify_intent(state: ShiftNotesState) -> ShiftNotesState:
    run_id = state.get("run_id", "unknown")
    log_node_entry(logger, "classify_intent", run_id)

    try:
        # If there's already an error upstream, skip and pass it forward
        if state.get("error"):
            return state

        raw_reports = state.get("raw_reports", [])

        # For the prototype, intent is always "signals" —
        # RAG query mode is triggered when Ted asks a natural
        # language question like "what happened at Kiosk A this month?"
        # That's a future feature — for now we always run signal detection
        if len(raw_reports) > 0:
            intent = "signals"
        else:
            intent = "unknown"

        log_node_exit(logger, "classify_intent", run_id, f"intent={intent}")

        return {
            **state,
            "intent": intent
        }

    except Exception as e:
        log_error(logger, "classify_intent", run_id, str(e))
        return {
            **state,
            "error": f"classify_intent failed: {str(e)}"
        }