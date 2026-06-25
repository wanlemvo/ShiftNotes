import sys
from pathlib import Path

from langgraph.types import Command

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "final_project" / "src"))

from shiftnotes.graph import build_persistent_graph, build_test_graph


def config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def initial_state(
    thread_id: str,
    *,
    simulate_failures: int = 0,
    max_retries: int = 2,
) -> dict:
    return {
        "thread_id": thread_id,
        "mode": "demo",
        "reporting_period": "weekly",
        "expected_kiosks": ["Bowls & Buns"],
        "limit": 100,
        "max_retries": max_retries,
        "retry_count": 0,
        "simulate_failures": simulate_failures,
        "execution_log": [],
    }


def test_graph_retries_failed_tool_call_then_pauses_for_review():
    graph = build_test_graph()
    thread_id = "retry-success"

    result = graph.invoke(
        initial_state(thread_id, simulate_failures=1),
        config(thread_id),
    )

    assert result["status"] == "awaiting_review"
    assert result["retry_count"] == 1
    assert result["tool_result"]["success"] is True
    assert result["tool_result"]["submission_count"] == 4
    assert result["__interrupt__"]
    assert any("retrying ingestion" in entry for entry in result["execution_log"])
    assert any("ingest_tool: success" in entry for entry in result["execution_log"])
    assert result["analysis"]["missing_reports"] == [
        {"kiosk": "Bowls & Buns", "date": "2026-06-18"}
    ]


def test_graph_routes_to_fallback_after_retry_limit():
    graph = build_test_graph()
    thread_id = "retry-fallback"

    result = graph.invoke(
        initial_state(thread_id, simulate_failures=3, max_retries=2),
        config(thread_id),
    )

    assert result["status"] == "failed"
    assert result["retry_count"] == 2
    assert "simulated ingestion failure" in result["fallback_reason"]
    assert not result.get("final_briefing")
    assert any("retry limit reached" in entry for entry in result["execution_log"])


def test_human_correction_regenerates_and_interrupts_again():
    graph = build_test_graph()
    thread_id = "correction-loop"
    graph.invoke(initial_state(thread_id), config(thread_id))

    corrected = graph.invoke(
        Command(
            resume={
                "decision": "correct",
                "note": "Treat poke mentions as guest requests, not confirmed demand.",
            }
        ),
        config(thread_id),
    )

    assert corrected["status"] == "awaiting_review"
    assert corrected["__interrupt__"]
    assert "## Human Correction" in corrected["draft_briefing"]

    approved = graph.invoke(
        Command(resume={"decision": "approve"}),
        config(thread_id),
    )
    assert approved["status"] == "approved"
    assert approved["final_briefing"] == approved["draft_briefing"]


def test_sqlite_checkpoint_resumes_after_graph_restart(tmp_path: Path):
    checkpoint_path = tmp_path / "checkpoint.sqlite"
    thread_id = "persistent-resume"

    with build_persistent_graph(checkpoint_path) as first_runtime:
        paused = first_runtime.graph.invoke(
            initial_state(thread_id),
            config(thread_id),
        )
        assert paused["__interrupt__"]

    with build_persistent_graph(checkpoint_path) as second_runtime:
        approved = second_runtime.graph.invoke(
            Command(resume={"decision": "approve"}),
            config(thread_id),
        )

    assert approved["status"] == "approved"
    assert approved["review_decision"] == "approve"
    assert approved["final_briefing"]
