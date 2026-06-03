import pandas as pd
import uuid
from datetime import datetime
from pathlib import Path

from shiftnotes_agent.state import ShiftNotesState
from shiftnotes_agent.logger import get_logger, log_node_entry, log_node_exit, log_error

logger = get_logger("ingest_email")

# Path to the mock CSV — same data the prototype used
MOCK_CSV_PATH = Path(__file__).parent.parent.parent / "prototype" / "mock_shift_notes.csv"


def ingest_email(state: ShiftNotesState) -> ShiftNotesState:
    run_id = state.get("run_id", str(uuid.uuid4()))
    log_node_entry(logger, "ingest_email", run_id)

    try:
        # --- Read reports ---
        # NOTE: swap this function out for Gmail MCP later
        reports = _read_from_csv()

        log_node_exit(logger, "ingest_email", run_id, f"loaded {len(reports)} reports")

        return {
            **state,
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "raw_reports": reports,
            "error": None
        }

    except Exception as e:
        log_error(logger, "ingest_email", run_id, str(e))
        return {
            **state,
            "run_id": run_id,
            "error": f"ingest_email failed: {str(e)}"
        }


def _read_from_csv() -> list[dict]:
    """
    Reads mock shift reports from CSV.
    Replace this with Gmail MCP call when ready for production.
    """
    df = pd.read_csv(MOCK_CSV_PATH)
    return df.to_dict(orient="records")