from shiftnotes_agent.state import ShiftNotesState
from shiftnotes_agent.logger import get_logger, log_node_entry, log_node_exit, log_error, log_signal_detected
from shiftnotes_agent.tools.signal_classifier import classify_report

logger = get_logger("detect_signals")


def detect_signals(state: ShiftNotesState) -> ShiftNotesState:
    run_id = state.get("run_id", "unknown")
    log_node_entry(logger, "detect_signals", run_id)

    try:
        # Skip if upstream error or wrong intent
        if state.get("error"):
            return state

        if state.get("intent") != "signals":
            log_node_exit(logger, "detect_signals", run_id, "skipped — intent is not signals")
            return state

        raw_reports = state.get("raw_reports", [])
        detected_signals = []

        for report in raw_reports:
            result = classify_report(report)

            if result["has_signal"]:
                detected_signals.append(result)

                # Log each signal we find
                for signal in result["signals_found"]:
                    log_signal_detected(
                        logger,
                        signal=signal["name"],
                        method=signal["method"],
                        run_id=run_id
                    )

        log_node_exit(
            logger,
            "detect_signals",
            run_id,
            f"found signals in {len(detected_signals)}/{len(raw_reports)} reports"
        )

        return {
            **state,
            "detected_signals": detected_signals
        }

    except Exception as e:
        log_error(logger, "detect_signals", run_id, str(e))
        return {
            **state,
            "error": f"detect_signals failed: {str(e)}"
        }
        