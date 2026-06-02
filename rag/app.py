"""
app.py
ShiftNotes — Operational Intelligence Dashboard

Run with:
    streamlit run app.py
"""

import io
import os
import sys
import pathlib
import pandas as pd
import plotly.express as px
import streamlit as st

# ── Path setup ────────────────────────────────────────────────────────────────
RAG_DIR       = pathlib.Path(__file__).parent
PROTO_DIR     = RAG_DIR.parent / "prototype"
CHROMA_PATH   = RAG_DIR / "chroma_db"
MOCK_CSV      = PROTO_DIR / "mock_shift_notes.csv"

sys.path.insert(0, str(PROTO_DIR))
sys.path.insert(0, str(RAG_DIR))

from signal_classifier import apply_to_dataframe
from embed import build_index, prepare_dataframe
from retriever import get_embedding_model, get_collection, query

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ShiftNotes",
    page_icon="📋",
    layout="wide",
)

# ── Cached resources ──────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading embedding model...")
def load_embed_model():
    return get_embedding_model()

@st.cache_resource(show_spinner="Loading vector index...")
def load_collection():
    return get_collection(CHROMA_PATH)

@st.cache_data(show_spinner="Running signal detection...")
def run_signal_detection(_df_hash, df_json: str) -> str:
    df = pd.read_json(io.StringIO(df_json))
    result = apply_to_dataframe(df, text_col="full_text")
    return result.to_json()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📋 ShiftNotes")
    st.caption("Operational Intelligence System")
    st.divider()

    st.subheader("Data Source")
    use_mock = st.radio("Select dataset", ["Mock dataset", "Upload CSV"], index=0)

    uploaded_file = None
    if use_mock == "Upload CSV":
        uploaded_file = st.file_uploader("Upload shift reports", type="csv")

    st.divider()
    st.subheader("RAG Settings")
    api_key = st.text_input("Groq API Key", type="password",
                             help="Free at groq.com — required for the Ask ShiftNotes tab.")
    n_results = st.slider("Reports to retrieve", min_value=3, max_value=10, value=5)

# ── Load data ─────────────────────────────────────────────────────────────────
if use_mock == "Mock dataset":
    raw_df = pd.read_csv(MOCK_CSV)
elif uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)
else:
    st.info("Upload a CSV file in the sidebar to get started.")
    st.stop()

# Clean and build full_text
df_clean = prepare_dataframe(raw_df.copy())
df_clean["date"]   = pd.to_datetime(df_clean["date"])
df_clean["week"]   = df_clean["week"].astype(int)

# Signal detection (cached by dataframe content)
df_hash    = hash(df_clean["full_text"].str.cat())
df_signals = pd.read_json(io.StringIO(run_signal_detection(df_hash, df_clean.to_json())))
df_signals["date"] = pd.to_datetime(df_signals["date"])

# Kiosk summary
kiosk_summary = df_signals.groupby("kiosk").agg(
    reports             = ("report_id",               "count"),
    avg_food_quality    = ("food_quality_rating",      "mean"),
    avg_food_quantity   = ("food_quantity_rating",     "mean"),
    total_unclaimed     = ("number_of_unclaimed_lunches", "sum"),
    poke_mentions       = ("poke_request_mention",     "sum"),
    chicken_shortages   = ("chicken_shortage_mention", "sum"),
    ops_issues          = ("ops_issue_mention",        "sum"),
    recognition         = ("team_recognition_mention", "sum"),
).reset_index().sort_values("kiosk")

# Weekly summary
weekly_summary = df_signals.groupby("week").agg(
    reports           = ("report_id",                 "count"),
    poke_mentions     = ("poke_request_mention",       "sum"),
    chicken_shortages = ("chicken_shortage_mention",   "sum"),
    unclaimed_lunches = ("number_of_unclaimed_lunches","sum"),
    ops_issues        = ("ops_issue_mention",          "sum"),
).reset_index().sort_values("week")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Kiosk Summary",
    "📈 Weekly Trends",
    "📝 Briefings",
    "💬 Ask ShiftNotes",
])

# ── Tab 1: Kiosk Summary ──────────────────────────────────────────────────────
with tab1:
    st.header("Kiosk Summary")
    st.caption(f"{len(df_signals)} reports across {df_signals['kiosk'].nunique()} kiosks")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Reports",        len(df_signals))
    col2.metric("Poke Requests",        int(df_signals["poke_request_mention"].sum()))
    col3.metric("Chicken Shortages",    int(df_signals["chicken_shortage_mention"].sum()))
    col4.metric("Ops Issues",           int(df_signals["ops_issue_mention"].sum()))

    st.divider()

    # Summary table
    display_cols = {
        "kiosk":             "Kiosk",
        "reports":           "Reports",
        "avg_food_quality":  "Avg Quality",
        "avg_food_quantity": "Avg Quantity",
        "total_unclaimed":   "Unclaimed Lunches",
        "poke_mentions":     "Poke Requests",
        "chicken_shortages": "Chicken Shortages",
        "ops_issues":        "Ops Issues",
        "recognition":       "Recognition",
    }
    st.dataframe(
        kiosk_summary.rename(columns=display_cols).style.format({
            "Avg Quality":  "{:.2f}",
            "Avg Quantity": "{:.2f}",
        }),
        width='stretch',
        hide_index=True,
    )

    st.divider()
    col_a, col_b = st.columns(2)

    with col_a:
        fig = px.bar(kiosk_summary, x="kiosk", y="total_unclaimed",
                     title="Total Unclaimed Lunches by Kiosk",
                     color="total_unclaimed", color_continuous_scale="Reds",
                     labels={"kiosk": "Kiosk", "total_unclaimed": "Unclaimed Lunches"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width='stretch')

    with col_b:
        signal_data = kiosk_summary.melt(
            id_vars="kiosk",
            value_vars=["poke_mentions", "chicken_shortages", "ops_issues", "recognition"],
            var_name="Signal", value_name="Count"
        )
        signal_labels = {
            "poke_mentions":     "Poke Requests",
            "chicken_shortages": "Chicken Shortages",
            "ops_issues":        "Ops Issues",
            "recognition":       "Recognition",
        }
        signal_data["Signal"] = signal_data["Signal"].map(signal_labels)
        fig2 = px.bar(signal_data, x="kiosk", y="Count", color="Signal",
                      barmode="group", title="Signal Counts by Kiosk",
                      labels={"kiosk": "Kiosk"})
        st.plotly_chart(fig2, width='stretch')

    col_c, col_d = st.columns(2)

    with col_c:
        fig3 = px.bar(kiosk_summary, x="kiosk", y="avg_food_quality",
                      title="Average Food Quality Rating by Kiosk",
                      color="avg_food_quality", color_continuous_scale="Greens",
                      range_y=[0, 5],
                      labels={"kiosk": "Kiosk", "avg_food_quality": "Avg Quality (1-5)"})
        fig3.update_layout(showlegend=False)
        st.plotly_chart(fig3, width='stretch')

    with col_d:
        fig4 = px.bar(kiosk_summary, x="kiosk", y="avg_food_quantity",
                      title="Average Food Quantity Rating by Kiosk",
                      color="avg_food_quantity", color_continuous_scale="Blues",
                      range_y=[0, 5],
                      labels={"kiosk": "Kiosk", "avg_food_quantity": "Avg Quantity (1-5)"})
        fig4.update_layout(showlegend=False)
        st.plotly_chart(fig4, width='stretch')

# ── Tab 2: Weekly Trends ──────────────────────────────────────────────────────
with tab2:
    st.header("Weekly Trends")

    st.dataframe(
        weekly_summary.rename(columns={
            "week":             "Week",
            "reports":          "Reports",
            "poke_mentions":    "Poke Requests",
            "chicken_shortages":"Chicken Shortages",
            "unclaimed_lunches":"Unclaimed Lunches",
            "ops_issues":       "Ops Issues",
        }),
        width='stretch',
        hide_index=True,
    )

    st.divider()
    col_a, col_b = st.columns(2)

    with col_a:
        fig5 = px.line(weekly_summary, x="week", y="unclaimed_lunches",
                       markers=True, title="Unclaimed Lunches by Week",
                       labels={"week": "Week", "unclaimed_lunches": "Total Unclaimed"})
        st.plotly_chart(fig5, width='stretch')

    with col_b:
        trend_data = weekly_summary.melt(
            id_vars="week",
            value_vars=["poke_mentions", "chicken_shortages", "ops_issues"],
            var_name="Signal", value_name="Count"
        )
        signal_labels = {
            "poke_mentions":     "Poke Requests",
            "chicken_shortages": "Chicken Shortages",
            "ops_issues":        "Ops Issues",
        }
        trend_data["Signal"] = trend_data["Signal"].map(signal_labels)
        fig6 = px.line(trend_data, x="week", y="Count", color="Signal",
                       markers=True, title="Signal Trends by Week",
                       labels={"week": "Week"})
        st.plotly_chart(fig6, width='stretch')

# ── Tab 3: Briefings ──────────────────────────────────────────────────────────
with tab3:
    st.header("Weekly Operational Briefings")

    weeks = sorted(df_signals["week"].unique())
    selected_week = st.selectbox("Select week", weeks, index=len(weeks) - 1)

    wk = df_signals[df_signals["week"] == selected_week]
    waste_by_kiosk = wk.groupby("kiosk")["number_of_unclaimed_lunches"].sum().sort_values(ascending=False)
    top_waste      = waste_by_kiosk.index[0]

    st.subheader(f"Week {selected_week} Operations Summary")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Reports",            len(wk))
    col2.metric("Poke Requests",      int(wk["poke_request_mention"].sum()))
    col3.metric("Chicken Shortages",  int(wk["chicken_shortage_mention"].sum()))
    col4.metric("Ops Issues",         int(wk["ops_issue_mention"].sum()))
    col5.metric("Unclaimed Lunches",  int(wk["number_of_unclaimed_lunches"].sum()))

    st.divider()
    st.markdown(f"""
**Highest Waste Kiosk:** {top_waste}

**Recommended Attention:**
1. Review prep planning at **{top_waste}** to reduce unclaimed lunches.
2. Track recurring menu requests to evaluate demand opportunities.
3. Review recurring shortage and ops-friction notes for root causes.
""")

    st.divider()
    st.subheader("Manager Review")
    st.caption("Review the briefing above before it is marked as approved.")

    col_approve, col_flag = st.columns(2)

    approved = col_approve.button("✅ Approve Briefing", type="primary")
    flagged = col_flag.button("🚩 Flag for Review")

    if approved:
        st.success(f"Week {selected_week} briefing approved.")
        if "approvals" not in st.session_state:
            st.session_state["approvals"] = []
        st.session_state["approvals"].append({
            "week": selected_week,
            "action": "approved",
            "top_waste_kiosk": top_waste,
        })

    if flagged:
        reason = st.text_input("What needs review?", key="flag_reason")
        if reason:
            st.warning(f"Week {selected_week} briefing flagged: {reason}")
            if "approvals" not in st.session_state:
                st.session_state["approvals"] = []
            st.session_state["approvals"].append({
                "week": selected_week,
                "action": "flagged",
                "reason": reason,
                "top_waste_kiosk": top_waste,
            })

    st.divider()
    st.subheader("Reports This Week")
    st.dataframe(
        wk[["report_id", "date", "kiosk", "lead_name",
            "food_quality_rating", "food_quantity_rating",
            "number_of_unclaimed_lunches"]].sort_values("date"),
        width='stretch',
        hide_index=True,
    )

# ── Tab 4: Ask ShiftNotes (RAG) ───────────────────────────────────────────────
with tab4:
    st.header("Ask ShiftNotes")
    st.caption("Ask any question about the shift reports. Answers are grounded in retrieved report data.")

    if not api_key:
        st.warning("Enter your Groq API key in the sidebar to use this feature. Free at groq.com — no credit card required.")
        st.stop()

    if not CHROMA_PATH.exists():
        st.info("Building vector index for the first time — this may take a moment...")
        with st.spinner("Indexing reports..."):
            build_index(chroma_path=CHROMA_PATH)
        st.success("Index ready.")

    embed_model = load_embed_model()
    collection  = load_collection()

    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        kiosk_filter = st.selectbox(
            "Filter by kiosk (optional)",
            ["All"] + sorted(df_signals["kiosk"].unique().tolist())
        )
    with col_filter2:
        week_filter = st.selectbox(
            "Filter by week (optional)",
            [0] + sorted(df_signals["week"].unique().tolist()),
            format_func=lambda x: "All weeks" if x == 0 else f"Week {x}"
        )

    st.divider()

    # Sample questions
    st.markdown("**Sample questions:**")
    sample_questions = [
        "What food issues occurred at Kiosk D?",
        "Which employee has been recognized the most?",
        "How has waste at Kiosk B changed over time?",
        "What guest complaints came up more than once?",
        "Which kiosk had the most operational concerns?",
    ]
    if "question_input" not in st.session_state:
        st.session_state["question_input"] = ""

    cols = st.columns(len(sample_questions))
    for i, (col, q) in enumerate(zip(cols, sample_questions)):
        if col.button(q, key=f"sample_{i}", width='stretch'):
            st.session_state["question_input"] = q

    question = st.text_input(
        "Your question",
        key="question_input",
        placeholder="e.g. What food shortages occurred this month?",
    )

    if st.button("Ask", type="primary") and question.strip():
        with st.spinner("Retrieving reports and generating answer..."):
            try:
                answer, hits = query(
                    question=question,
                    kiosk=kiosk_filter if kiosk_filter != "All" else None,
                    week=week_filter if week_filter != 0 else None,
                    n_results=n_results,
                    api_key=api_key,
                    model=embed_model,
                    collection=collection,
                )

                st.subheader("Answer")
                st.markdown(answer)

                with st.expander(f"Source reports ({len(hits)} retrieved)"):
                    for h in hits:
                        m = h["meta"]
                        st.markdown(
                            f"**Report {m['report_id']}** | {m['kiosk']} | {m['date']} | Lead: {m['lead_name']}"
                        )
                        st.text(h["text"][:300] + ("..." if len(h["text"]) > 300 else ""))
                        st.divider()

            except Exception as e:
                st.error(f"Error: {e}")
