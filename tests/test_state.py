from shiftnotes_agent.state import ShiftNotesState

def test_state_has_required_keys():
    required_keys = [
        "raw_reports", "intent", "detected_signals",
        "retrieved_context", "generated_briefing", "briefing_sent",
        "ted_decision", "escalation_note", "run_id", "timestamp", "error"
    ]
    state_keys = ShiftNotesState.__annotations__.keys()
    for key in required_keys:
        assert key in state_keys, f"Missing key: {key}"