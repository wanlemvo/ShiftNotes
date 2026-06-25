from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from shiftnotes.product import append_correction_history, propose_correction


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CHECKPOINT_PATH = (
    ROOT / "final_project" / "data" / "checkpoints" / "corrections.sqlite"
)
DEFAULT_HISTORY_PATH = (
    ROOT / "final_project" / "data" / "corrections" / "correction_history.json"
)


class CorrectionState(TypedDict, total=False):
    thread_id: str
    claim: dict[str, Any]
    challenge_text: str
    reports: list[dict[str, Any]]
    history_path: str
    proposal: dict[str, Any]
    route: str
    decision: str
    audit_record: dict[str, Any]
    status: str
    execution_log: list[str]


def log(state: CorrectionState, message: str) -> list[str]:
    return [*state.get("execution_log", []), message]


def receive_challenge_node(state: CorrectionState) -> dict[str, Any]:
    return {
        "status": "challenge_received",
        "execution_log": log(
            state,
            f"receive_challenge: claim={state.get('claim', {}).get('claim_id', '')}",
        ),
    }


def propose_node(state: CorrectionState) -> dict[str, Any]:
    proposal = propose_correction(
        state["claim"],
        state["challenge_text"],
        state["reports"],
    )
    if proposal["safety_refusal"]:
        route = "refused"
    elif proposal["requires_confirmation"]:
        route = "confirm"
    else:
        route = "clarify"
    return {
        "proposal": proposal,
        "route": route,
        "status": proposal["status"],
        "execution_log": log(
            state,
            f"propose_correction: route={route}; proposal={proposal['proposal_id']}",
        ),
    }


def route_after_proposal(state: CorrectionState) -> str:
    return state.get("route", "clarify")


def confirmation_node(
    state: CorrectionState,
) -> Command[Literal["apply_correction", "cancel_correction"]]:
    proposal = state["proposal"]
    response = interrupt(
        {
            "action": "confirm_correction",
            "message": "Review the proposed correction before it is saved.",
            "options": ["confirm", "revise", "cancel"],
            "proposal": proposal,
        }
    )
    if not isinstance(response, dict):
        response = {"decision": str(response)}
    decision = str(response.get("decision", "cancel")).lower().strip()

    if decision == "confirm":
        return Command(
            update={
                "decision": "confirm",
                "execution_log": log(state, "confirmation: confirmed"),
            },
            goto="apply_correction",
        )
    return Command(
        update={
            "decision": decision if decision in {"revise", "cancel"} else "cancel",
            "execution_log": log(state, f"confirmation: {decision}"),
        },
        goto="cancel_correction",
    )


def apply_correction_node(state: CorrectionState) -> dict[str, Any]:
    history_path = Path(
        state.get("history_path") or str(DEFAULT_HISTORY_PATH)
    )
    record = append_correction_history(
        history_path,
        state["proposal"],
        "confirm",
    )
    return {
        "audit_record": record,
        "status": "confirmed",
        "execution_log": log(
            state,
            f"apply_correction: saved={record['proposal_id']}",
        ),
    }


def cancel_correction_node(state: CorrectionState) -> dict[str, Any]:
    history_path = Path(
        state.get("history_path") or str(DEFAULT_HISTORY_PATH)
    )
    record = append_correction_history(
        history_path,
        state["proposal"],
        state.get("decision", "cancel"),
    )
    return {
        "audit_record": record,
        "status": "cancelled",
        "execution_log": log(
            state,
            f"cancel_correction: decision={state.get('decision', 'cancel')}",
        ),
    }


def terminal_node(state: CorrectionState) -> dict[str, Any]:
    return {
        "status": state.get("proposal", {}).get("status", "needs_clarification"),
        "execution_log": log(
            state,
            f"terminal: {state.get('proposal', {}).get('status', 'unknown')}",
        ),
    }


def build_correction_graph(checkpointer: Any):
    builder = StateGraph(CorrectionState)
    builder.add_node("receive_challenge", receive_challenge_node)
    builder.add_node("propose_correction", propose_node)
    builder.add_node("confirm_correction", confirmation_node)
    builder.add_node("apply_correction", apply_correction_node)
    builder.add_node("cancel_correction", cancel_correction_node)
    builder.add_node("terminal", terminal_node)

    builder.add_edge(START, "receive_challenge")
    builder.add_edge("receive_challenge", "propose_correction")
    builder.add_conditional_edges(
        "propose_correction",
        route_after_proposal,
        {
            "confirm": "confirm_correction",
            "clarify": "terminal",
            "refused": "terminal",
        },
    )
    builder.add_edge("apply_correction", END)
    builder.add_edge("cancel_correction", END)
    builder.add_edge("terminal", END)
    return builder.compile(checkpointer=checkpointer)


def build_test_correction_graph():
    return build_correction_graph(InMemorySaver())


@dataclass
class PersistentCorrectionGraph:
    graph: Any
    connection: sqlite3.Connection

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "PersistentCorrectionGraph":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def build_persistent_correction_graph(
    path: Path = DEFAULT_CHECKPOINT_PATH,
) -> PersistentCorrectionGraph:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, check_same_thread=False)
    return PersistentCorrectionGraph(
        graph=build_correction_graph(SqliteSaver(connection)),
        connection=connection,
    )
