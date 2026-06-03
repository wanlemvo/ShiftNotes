from datetime import datetime
from pathlib import Path

from shiftnotes_agent.state import ShiftNotesState
from shiftnotes_agent.logger import get_logger, log_node_entry, log_node_exit, log_error

logger = get_logger("send_briefing")

# Where briefings get saved locally
OUTPUT_DIR = Path("briefings")


def send_briefing(state: ShiftNotesState) -> ShiftNotesState:
    run_id = state.get("run_id", "unknown")
    log_node_entry(logger, "send_briefing", run_id)

    try:
        if state.get("error"):
            return state

        briefing = state.get("generated_briefing", "")

        if not briefing:
            log_node_exit(logger, "send_briefing", run_id, "no briefing to send")
            return {**state, "briefing_sent": False}

        # --- Deliver briefing ---
        # NOTE: swap _save_to_file() for Gmail MCP call when ready
        _save_to_file(briefing, run_id)

        log_node_exit(logger, "send_briefing", run_id, "briefing delivered")

        return {
            **state,
            "briefing_sent": True
        }

    except Exception as e:
        log_error(logger, "send_briefing", run_id, str(e))
        return {
            **state,
            "briefing_sent": False,
            "error": f"send_briefing failed: {str(e)}"
        }


def _save_to_file(briefing: str, run_id: str):
    """
    Saves briefing to a local file.
    Replace this with Gmail MCP send when ready for production.
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = OUTPUT_DIR / f"briefing_{timestamp}_{run_id}.txt"

    with open(filepath, "w") as f:
        f.write(f"ShiftNotes Weekly Briefing\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write(f"Run ID: {run_id}\n")
        f.write("=" * 50 + "\n\n")
        f.write(briefing)

    logger.info(f"Briefing saved to {filepath}")