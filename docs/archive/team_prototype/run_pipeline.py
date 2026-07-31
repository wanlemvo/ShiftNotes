import uuid
from dotenv import load_dotenv
from shiftnotes_agent.graph import graph
from shiftnotes_agent.logger import get_logger

load_dotenv()
logger = get_logger("pipeline")


def run():
    # Unique ID for this pipeline run
    run_id = str(uuid.uuid4())[:8]
    thread_id = {"configurable": {"thread_id": run_id}}

    print("\n" + "="*50)
    print("SHIFTNOTES PIPELINE STARTING")
    print("="*50 + "\n")

    # --- Initial state ---
    initial_state = {
        "run_id": run_id,
        "timestamp": "",
        "raw_reports": [],
        "intent": "",
        "detected_signals": [],
        "retrieved_context": "",
        "generated_briefing": "",
        "briefing_sent": False,
        "ted_decision": None,
        "escalation_note": None,
        "error": None
    }

    # --- Run until HITL interrupt ---
    print("Running pipeline... (this takes ~30 seconds)\n")
    for event in graph.stream(initial_state, thread_id):
        for node_name, node_output in event.items():
            if node_name != "__interrupt__":
                print(f"✓ Node completed: {node_name}")

    # --- Check if we're paused at HITL ---
    snapshot = graph.get_state(thread_id)

    if snapshot.next and "human_review" in snapshot.next:
        print("\n" + "="*50)
        print("PIPELINE PAUSED — AWAITING TED'S DECISION")
        print("="*50)

        # Show Ted the briefing
        briefing = snapshot.values.get("generated_briefing", "")
        print(f"\nBRIEFING PREVIEW:\n{briefing[:300]}...\n")

        # Get Ted's decision
        print("Ted's options: accept | drill_down | escalate")
        decision = input("Enter Ted's decision: ").strip().lower()

        note = ""
        if decision == "escalate":
            note = input("Enter escalation note: ").strip()

        # --- Resume graph with Ted's decision ---
        graph.update_state(
            thread_id,
            {"ted_decision": decision, "escalation_note": note},
            as_node="human_review"
        )

        for event in graph.stream(None, thread_id):
            for node_name, node_output in event.items():
                print(f"✓ Node completed: {node_name}")

    # --- Final state ---
    final = graph.get_state(thread_id)
    print("\n" + "="*50)
    print("PIPELINE COMPLETE")
    print("="*50)
    print(f"Run ID:        {run_id}")
    print(f"Briefing sent: {final.values.get('briefing_sent')}")
    print(f"Ted's decision: {final.values.get('ted_decision')}")
    error = final.values.get('error')
    if error:
        print(f"Error: {error}")


if __name__ == "__main__":
    run()