import uuid
from datetime import datetime
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from shiftnotes_agent.state import ShiftNotesState
from shiftnotes_agent.nodes.ingest_email import ingest_email
from shiftnotes_agent.nodes.classify_intent import classify_intent
from shiftnotes_agent.nodes.detect_signals import detect_signals
from shiftnotes_agent.nodes.retrieve_and_generate import retrieve_and_generate
from shiftnotes_agent.nodes.send_briefing import send_briefing
from shiftnotes_agent.nodes.human_review import human_review
from shiftnotes_agent.logger import get_logger

load_dotenv()
logger = get_logger("graph")


def route_after_review(state: ShiftNotesState) -> str:
    """
    Conditional routing after Ted's decision.
    BCPolicyPal connection: same conditional edge pattern
    you used in Week 6 to route based on agent output.
    """
    decision = state.get("ted_decision", "accept")
    error = state.get("error")

    if error:
        return "end"

    if decision == "accept":
        return "end"
    elif decision == "drill_down":
        return "end"  # Streamlit handles this outside the graph
    elif decision == "escalate":
        return "end"  # escalation handled outside the graph
    else:
        return "end"


def build_graph():
    """Builds and compiles the ShiftNotes LangGraph."""

    # --- Define the graph ---
    builder = StateGraph(ShiftNotesState)

    # --- Add nodes ---
    builder.add_node("ingest_email", ingest_email)
    builder.add_node("classify_intent", classify_intent)
    builder.add_node("detect_signals", detect_signals)
    builder.add_node("retrieve_and_generate", retrieve_and_generate)
    builder.add_node("send_briefing", send_briefing)
    builder.add_node("human_review", human_review)

    # --- Define edges (the flow) ---
    builder.set_entry_point("ingest_email")
    builder.add_edge("ingest_email", "classify_intent")
    builder.add_edge("classify_intent", "detect_signals")
    builder.add_edge("detect_signals", "retrieve_and_generate")
    builder.add_edge("retrieve_and_generate", "send_briefing")
    builder.add_edge("send_briefing", "human_review")

    # --- Conditional edge after Ted's review ---
    builder.add_conditional_edges(
        "human_review",
        route_after_review,
        {
            "end": END
        }
    )

    # --- Checkpointer enables HITL ---
    # This is what saves graph state so it can pause
    # and resume when Ted responds.
    checkpointer = MemorySaver()

    return builder.compile(checkpointer=checkpointer)


# Build the graph on import
graph = build_graph()