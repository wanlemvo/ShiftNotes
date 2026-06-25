from __future__ import annotations

import sys
import uuid
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from langgraph.types import Command


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "final_project" / "src"
sys.path.insert(0, str(SRC))

from shiftnotes.correction_graph import (
    DEFAULT_HISTORY_PATH,
    build_persistent_correction_graph,
)
from shiftnotes.product import (
    apply_correction_history,
    build_claim_catalog,
    build_source_bundle,
    load_correction_history,
)
from shiftnotes.baseline import load_schedule
from shiftnotes.storage import read_json


DATASET_DIR = ROOT / "final_project" / "data" / "final_mock"
CHECKPOINT_PATH = (
    ROOT / "final_project" / "data" / "checkpoints" / "corrections.sqlite"
)


st.set_page_config(
    page_title="ShiftNotes",
    page_icon="SN",
    layout="wide",
    initial_sidebar_state="auto",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
          --sn-ink: #17212b;
          --sn-muted: #66727d;
          --sn-line: #dce2e7;
          --sn-teal: #0f766e;
          --sn-teal-soft: #e7f5f2;
          --sn-amber: #a16207;
          --sn-red: #b42318;
        }
        .stApp { background: #f6f8f9; color: var(--sn-ink); }
        [data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid var(--sn-line); }
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div { color: var(--sn-ink); }
        [data-testid="stSidebar"] hr { border-color: var(--sn-line); }
        .block-container { max-width: 1320px; padding-top: 1.4rem; }
        h1, h2, h3 { letter-spacing: 0; color: var(--sn-ink); }
        .sn-brand { font-size: 1.35rem; font-weight: 800; color: var(--sn-ink); }
        .sn-sub { font-size: .82rem; color: var(--sn-muted); margin-top: -4px; }
        .sn-bar {
          border-left: 4px solid var(--sn-teal);
          background: #ffffff;
          padding: 14px 18px;
          border-top: 1px solid var(--sn-line);
          border-right: 1px solid var(--sn-line);
          border-bottom: 1px solid var(--sn-line);
          margin-bottom: 18px;
        }
        .sn-callout {
          background: var(--sn-teal-soft);
          border-left: 4px solid var(--sn-teal);
          padding: 14px 16px;
          margin: 12px 0;
        }
        .sn-warning {
          background: #fef3c7;
          border-left: 4px solid var(--sn-amber);
          padding: 14px 16px;
          margin: 12px 0;
        }
        .sn-danger {
          background: #fee4e2;
          border-left: 4px solid var(--sn-red);
          padding: 14px 16px;
          margin: 12px 0;
        }
        div[data-testid="stMetric"] {
          background: #ffffff;
          border: 1px solid var(--sn-line);
          padding: 12px 14px;
          min-height: 104px;
        }
        div[data-testid="stMetric"] label { color: var(--sn-muted); }
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
          background: #ffffff;
          border: 1px solid var(--sn-line);
          height: 42px;
          padding: 0 16px;
        }
        .stTabs [aria-selected="true"] { border-color: var(--sn-teal); color: var(--sn-teal); }
        button[kind="primary"] { background: var(--sn-teal); border-color: var(--sn-teal); }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_product_data():
    reports = read_json(DATASET_DIR / "normalized_reports.json")
    schedule = load_schedule(DATASET_DIR / "expected_reporting_schedule.csv")
    claims_path = DATASET_DIR / "claims.json"
    ai_path = DATASET_DIR / "ai_extractions.json"
    semantic_extractions = read_json(ai_path) if ai_path.exists() else None
    claims = (
        read_json(claims_path)
        if claims_path.exists()
        else build_claim_catalog(
            reports,
            schedule,
            semantic_extractions=semantic_extractions,
        )
    )
    manifest_path = DATASET_DIR / "email_manifest.json"
    manifest = read_json(manifest_path) if manifest_path.exists() else []
    return reports, schedule, claims, manifest


def selected_claim_from_query(claims):
    claim_id = st.query_params.get("claim")
    if not claim_id:
        return None
    return next((claim for claim in claims if claim["claim_id"] == claim_id), None)


def graph_config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


inject_styles()
reports, schedule, claims, manifest = load_product_data()
history = load_correction_history(DEFAULT_HISTORY_PATH)
claims = apply_correction_history(claims, history)

with st.sidebar:
    st.markdown('<div class="sn-brand">ShiftNotes</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sn-sub">Operational intelligence workspace</div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.caption("Primary delivery")
    st.write("Weekly and monthly briefing emails")
    st.caption("Workspace role")
    st.write("Inspect sources, challenge claims, and review corrections")
    st.divider()
    st.caption("Schedule")
    st.write("Weekly: Thursday, 3:30 PM Pacific")
    st.write("Monthly: day before final expected reporting day")
    st.divider()
    st.caption("Dataset")
    st.write(f"{len(reports)} submitted records")
    st.write(f"{len(claims)} source-backed claims")

st.markdown(
    """
    <div class="sn-bar">
      <strong>Email-first operations intelligence</strong><br>
      Briefings are delivered automatically. This workspace is used only when a manager wants to inspect evidence or challenge a claim.
    </div>
    """,
    unsafe_allow_html=True,
)

requested_action = st.query_params.get("action")
requested_view = st.query_params.get("view")
default_tab = "Briefings"
if requested_action == "challenge" or st.session_state.get("go_to_challenge"):
    default_tab = "Challenge Review"
elif requested_view == "sources" or st.query_params.get("claim"):
    default_tab = "Claims & Sources"

tab_briefings, tab_claims, tab_challenge, tab_history = st.tabs(
    ["Briefings", "Claims & Sources", "Challenge Review", "Correction History"],
    default=default_tab,
    key=f"main_tabs_{default_tab}",
)

with tab_briefings:
    st.header("Briefing Preview")
    if not manifest:
        st.warning(
            "Email previews have not been generated. Run "
            "`python final_project/src/shiftnotes/cli.py product-assets`."
        )
    else:
        type_col, period_col = st.columns([1, 2])
        briefing_type = type_col.segmented_control(
            "Briefing type",
            ["weekly", "monthly"],
            default="weekly",
        )
        options = [
            item for item in manifest if item["type"] == briefing_type
        ]
        selected_period = period_col.selectbox(
            "Period",
            [item["period"] for item in options],
            index=max(0, len(options) - 1),
        )
        selected = next(
            item for item in options if item["period"] == selected_period
        )
        st.subheader(selected["subject"])
        html_path = DATASET_DIR / selected["html_path"]
        if html_path.exists():
            components.html(
                html_path.read_text(encoding="utf-8"),
                height=920,
                scrolling=True,
            )
        markdown_path = (
            DATASET_DIR
            / "briefings"
            / briefing_type
            / (
                f"{selected_period.replace('-', '_')}.md"
                if briefing_type == "weekly"
                else f"{selected_period}.md"
            )
        )
        with st.expander("View full briefing text"):
            st.markdown(markdown_path.read_text(encoding="utf-8"))

with tab_claims:
    st.header("Claims and Supporting Reports")
    requested_claim = selected_claim_from_query(claims)
    filter_col, kiosk_col = st.columns(2)
    period_type = filter_col.selectbox(
        "Period type",
        ["weekly", "monthly"],
        index=(
            ["weekly", "monthly"].index(requested_claim["period_type"])
            if requested_claim
            else 0
        ),
    )
    kiosks = sorted({claim["kiosk"] for claim in claims})
    kiosk = kiosk_col.selectbox("Kiosk", ["All"] + kiosks)
    filtered = [
        claim
        for claim in claims
        if claim["period_type"] == period_type
        and (kiosk == "All" or claim["kiosk"] == kiosk)
    ]
    query_claim = selected_claim_from_query(filtered)
    claim_labels = {
        f"{claim['period']} | {claim['kiosk']} | {claim['label']}": claim
        for claim in filtered
    }
    default_index = 0
    if query_claim:
        labels = list(claim_labels)
        default_index = next(
            (
                index
                for index, label in enumerate(labels)
                if claim_labels[label]["claim_id"] == query_claim["claim_id"]
            ),
            0,
        )
    selected_label = st.selectbox(
        "Claim",
        list(claim_labels),
        index=default_index,
    )
    selected_claim = claim_labels[selected_label]

    c1, c2, c3 = st.columns(3)
    c1.metric("Supporting reports", selected_claim["source_count"])
    c2.metric("Kiosk", selected_claim["kiosk"])
    c3.metric("Period", selected_claim["period"])
    callout_class = "sn-danger" if selected_claim["sensitive"] else "sn-callout"
    st.markdown(
        f'<div class="{callout_class}"><strong>{selected_claim["claim_text"]}</strong></div>',
        unsafe_allow_html=True,
    )
    if selected_claim.get("status") == "corrected":
        st.caption(
            "This claim includes a manager-confirmed correction. "
            f"Audit ID: {selected_claim.get('correction_id', '')}"
        )
    source_bundle = build_source_bundle(selected_claim, reports)
    for source in source_bundle:
        with st.expander(
            f"{source['source_submission_id']} | {source['date']} | {source['lead_name']}"
        ):
            m1, m2, m3 = st.columns(3)
            m1.metric("Food quality", source["food_quality_rating"])
            m2.metric("Food quantity", source["food_quantity_rating"])
            m3.metric("Unclaimed", source["number_of_unclaimed_lunches"])
            st.markdown("**Food concerns or outages**")
            st.write(source["food_concerns_or_outages"])
            st.markdown("**Team recognition**")
            st.write(source["team_members_who_did_well"])
            st.markdown("**Guest issues**")
            st.write(source["guest_issues_for_the_day"])
            st.markdown("**Operational notes**")
            st.write(source["operational_notes"])
    if st.button("Challenge this claim", type="primary"):
        st.session_state["challenge_claim_id"] = selected_claim["claim_id"]
        st.session_state["go_to_challenge"] = True
        st.rerun()

with tab_challenge:
    st.header("Challenge Review")
    claim_by_id = {claim["claim_id"]: claim for claim in claims}
    initial_claim_id = st.session_state.get(
        "challenge_claim_id",
        selected_claim_from_query(claims)["claim_id"]
        if selected_claim_from_query(claims)
        else claims[0]["claim_id"],
    )
    claim_id = st.selectbox(
        "Claim to review",
        list(claim_by_id),
        index=list(claim_by_id).index(initial_claim_id),
        format_func=lambda item: claim_by_id[item]["claim_text"],
    )
    active_claim = claim_by_id[claim_id]
    st.markdown(
        f'<div class="sn-callout"><strong>Original claim</strong><br>{active_claim["claim_text"]}</div>',
        unsafe_allow_html=True,
    )
    challenge_text = st.text_area(
        "Explain what is wrong in ordinary English",
        placeholder=(
            "Example: This is wrong. FM-0158 describes a register issue, "
            "not a separate waste concern. Remove it from this claim."
        ),
        height=120,
    )
    if st.button("Review challenge", type="primary", disabled=not challenge_text.strip()):
        thread_id = f"correction-{uuid.uuid4().hex[:10]}"
        initial = {
            "thread_id": thread_id,
            "claim": active_claim,
            "challenge_text": challenge_text,
            "reports": reports,
            "history_path": str(DEFAULT_HISTORY_PATH),
            "execution_log": [],
        }
        with build_persistent_correction_graph(CHECKPOINT_PATH) as runtime:
            result = runtime.graph.invoke(initial, graph_config(thread_id))
        st.session_state["correction_thread_id"] = thread_id
        st.session_state["correction_result"] = result
        st.rerun()

    result = st.session_state.get("correction_result")
    if result:
        proposal = result.get("proposal", {})
        if proposal.get("safety_refusal"):
            st.markdown(
                f'<div class="sn-danger"><strong>Request refused</strong><br>{proposal["rationale"]}</div>',
                unsafe_allow_html=True,
            )
        elif proposal.get("status") == "needs_clarification":
            st.markdown(
                f'<div class="sn-warning"><strong>Clarification needed</strong><br>{proposal["rationale"]}</div>',
                unsafe_allow_html=True,
            )
        elif result.get("status") == "confirmed":
            st.success("Correction confirmed and saved to audit history.")
            st.markdown("**Original claim**")
            st.write(proposal.get("original_claim_text", ""))
            st.markdown("**Confirmed correction**")
            st.write(proposal.get("proposed_claim_text", ""))
        elif result.get("status") == "cancelled":
            st.info("The proposed correction was not applied.")
        elif result.get("__interrupt__"):
            st.subheader("Proposed Correction")
            original, revised = st.columns(2)
            original.markdown("**Original**")
            original.write(proposal["original_claim_text"])
            revised.markdown("**Revised**")
            revised.write(proposal["proposed_claim_text"])
            st.write(proposal["rationale"])
            st.caption(
                "Removed sources: "
                + ", ".join(proposal["removed_source_ids"])
            )
            confirm_col, revise_col, cancel_col = st.columns(3)
            if confirm_col.button("Confirm correction", type="primary"):
                thread_id = st.session_state["correction_thread_id"]
                with build_persistent_correction_graph(CHECKPOINT_PATH) as runtime:
                    completed = runtime.graph.invoke(
                        Command(resume={"decision": "confirm"}),
                        graph_config(thread_id),
                    )
                st.session_state["correction_result"] = completed
                st.success("Correction confirmed and recorded.")
                st.rerun()
            if revise_col.button("Revise challenge"):
                thread_id = st.session_state["correction_thread_id"]
                with build_persistent_correction_graph(CHECKPOINT_PATH) as runtime:
                    runtime.graph.invoke(
                        Command(resume={"decision": "revise"}),
                        graph_config(thread_id),
                    )
                st.session_state.pop("correction_result", None)
                st.info("The proposal was cancelled. Submit a revised challenge.")
                st.rerun()
            if cancel_col.button("Cancel"):
                thread_id = st.session_state["correction_thread_id"]
                with build_persistent_correction_graph(CHECKPOINT_PATH) as runtime:
                    runtime.graph.invoke(
                        Command(resume={"decision": "cancel"}),
                        graph_config(thread_id),
                    )
                st.session_state.pop("correction_result", None)
                st.rerun()

with tab_history:
    st.header("Correction History")
    history = load_correction_history(DEFAULT_HISTORY_PATH)
    if not history:
        st.info("No correction decisions have been recorded yet.")
    else:
        history_df = pd.DataFrame(history)
        display_columns = [
            "decided_at",
            "actor",
            "decision",
            "claim_id",
            "challenge_text",
            "status",
        ]
        st.dataframe(
            history_df[[column for column in display_columns if column in history_df]],
            hide_index=True,
            width="stretch",
        )
        for record in reversed(history):
            with st.expander(
                f"{record.get('decided_at', '')} | {record.get('decision', '')} | {record.get('claim_id', '')}"
            ):
                st.markdown("**Challenge**")
                st.write(record.get("challenge_text", ""))
                st.markdown("**Original**")
                st.write(record.get("original_claim_text", ""))
                st.markdown("**Proposed**")
                st.write(record.get("proposed_claim_text", ""))
                st.markdown("**Removed sources**")
                st.write(", ".join(record.get("removed_source_ids", [])) or "None")
