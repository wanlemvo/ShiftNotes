from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph

from shiftnotes.graph_nodes import (
    analysis_node,
    draft_briefing_node,
    evaluator_node,
    fallback_node,
    finalize_node,
    human_review_node,
    ingest_tool_node,
    normalize_node,
    planner_node,
    reject_node,
    route_after_evaluation,
)
from shiftnotes.graph_state import ShiftNotesGraphState


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CHECKPOINT_PATH = ROOT / "final_project" / "data" / "checkpoints" / "shiftnotes.sqlite"


def build_graph(checkpointer: Any):
    builder = StateGraph(ShiftNotesGraphState)
    builder.add_node("planner", planner_node)
    builder.add_node("ingest_tool", ingest_tool_node)
    builder.add_node("evaluator", evaluator_node)
    builder.add_node("normalize", normalize_node)
    builder.add_node("analyze", analysis_node)
    builder.add_node("draft_briefing", draft_briefing_node)
    builder.add_node("human_review", human_review_node)
    builder.add_node("finalize", finalize_node)
    builder.add_node("reject", reject_node)
    builder.add_node("fallback", fallback_node)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "ingest_tool")
    builder.add_edge("ingest_tool", "evaluator")
    builder.add_conditional_edges(
        "evaluator",
        route_after_evaluation,
        {
            "retry": "ingest_tool",
            "normalize": "normalize",
            "fallback": "fallback",
        },
    )
    builder.add_edge("normalize", "analyze")
    builder.add_edge("analyze", "draft_briefing")
    builder.add_edge("draft_briefing", "human_review")
    builder.add_edge("finalize", END)
    builder.add_edge("reject", END)
    builder.add_edge("fallback", END)
    return builder.compile(checkpointer=checkpointer)


def build_test_graph():
    return build_graph(InMemorySaver())


@dataclass
class PersistentGraph:
    graph: Any
    connection: sqlite3.Connection

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "PersistentGraph":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def build_persistent_graph(path: Path = DEFAULT_CHECKPOINT_PATH) -> PersistentGraph:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, check_same_thread=False)
    checkpointer = SqliteSaver(connection)
    return PersistentGraph(graph=build_graph(checkpointer), connection=connection)
