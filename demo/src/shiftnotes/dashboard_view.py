"""Streamlit dashboard backed by normalized reports and the claim catalog."""

from datetime import date
from html import escape
from urllib.parse import urlencode

import pandas as pd
import streamlit as st

from shiftnotes.dashboard import dashboard_snapshot


def render_dashboard(reports, schedule, claims, *, compare_only=False):
    prefix = "compare" if compare_only else "dashboard"
    title = "Kiosk comparison" if compare_only else "Operations overview"
    st.header(title)
    weeks = sorted({int(r["week"]) for r in schedule})
    dates = sorted({r["date"] for r in schedule})
    first, last = date.fromisoformat(dates[0]), date.fromisoformat(dates[-1])
    controls = st.columns([1.2, 1.2, 2])
    mode = controls[0].selectbox("Date range", ["Latest week", "Previous week", "Latest month", "Last 3 months", "Custom"], key=f"{prefix}_range")
    kiosk = controls[1].selectbox("Kiosk", ["All kiosks"] + sorted({r["kiosk"] for r in schedule}), key=f"{prefix}_kiosk")
    if mode in ("Latest week", "Previous week"):
        week = weeks[-1] if mode == "Latest week" else weeks[max(0, len(weeks) - 2)]
        selected_dates = sorted(r["date"] for r in schedule if int(r["week"]) == week)
        start, end = date.fromisoformat(selected_dates[0]), date.fromisoformat(selected_dates[-1])
    elif mode == "Latest month":
        start, end = last.replace(day=1), last
    else:
        start, end = first, last
    if mode == "Custom":
        selected = controls[2].date_input("Reporting dates", (first, last), min_value=first, max_value=last, key=f"{prefix}_dates")
        if len(selected) != 2:
            st.info("Select an end date.")
            return
        start, end = selected
    else:
        controls[2].caption(f"{start:%b %d, %Y} to {end:%b %d, %Y} | Synthetic dataset")
    snapshot = dashboard_snapshot(reports, schedule, claims, start, end, None if kiosk == "All kiosks" else kiosk)
    if compare_only:
        render_comparison(snapshot, detailed=True)
        return

    m = snapshot["summary"]
    cards = [("Reports received", m["received"], "received"),
             ("Missing reports", m["missing"], "missing"),
             ("Avg. food quality", f'{m["quality"]:.2f}/5' if m["quality"] is not None else "N/A", "quality"),
             ("Avg. food quantity", f'{m["quantity"]:.2f}/5' if m["quantity"] is not None else "N/A", "quantity"),
             ("Unclaimed lunches", m["unclaimed"], "unclaimed"),
             ("Urgent findings", m["urgent"], "urgent"),
             ("Recurring issues", m["recurring"], "recurring"),
             ("Recognition reports", m["recognition"], "recognition")]
    st.markdown('<div class="sn-kpis">' + ''.join(
        f'<div class="sn-kpi sn-kpi-{kind}"><span>{escape(label)}</span><strong>{escape(str(value))}</strong></div>'
        for label, value, kind in cards) + '</div>', unsafe_allow_html=True)

    left, right = st.columns([1.35, 1], gap="large")
    with left:
        st.subheader("Priority queue")
        default_tier = "Urgent" if m["urgent"] else "Follow-up"
        tier = st.segmented_control("Priority", ["Urgent", "Follow-up", "Monitor"], default=default_tier, key="priority_tier") or default_tier
        urgency = {"Urgent": "urgent", "Follow-up": "important", "Monitor": "monitor"}[tier]
        queue = [f for f in snapshot["findings"] if f["priority"] == urgency and not f["recognition"]]
        if not queue:
            st.info("No findings in this priority tier for the selected dates.")
        else:
            for finding in queue:
                label = escape(finding["label"][:1].upper() + finding["label"][1:])
                st.markdown(f'<div class="sn-finding"><span class="sn-priority {urgency}">{escape(tier)}</span> <strong>{label}</strong><div>{escape(finding["kiosk"])} &middot; {finding["source_count"]} supporting reports &middot; {finding["weeks_observed"]} week(s)</div></div>', unsafe_allow_html=True)
                with st.expander(f"Inspect sources: {finding['label']} | {finding['kiosk']}"):
                    render_finding_sources(finding, reports, claims)
        st.divider()
        st.subheader("Recognition highlights")
        recognition = [f for f in snapshot["findings"] if f["recognition"]]
        if not recognition:
            st.caption("No recognition findings in this period.")
        for finding in recognition:
            with st.expander(f"{finding['label']} | {finding['kiosk']} | {finding['source_count']} reports"):
                render_finding_sources(finding, reports, claims)
        st.subheader("Missing reports")
        if snapshot["missing"]:
            st.dataframe(pd.DataFrame(snapshot["missing"])[["date", "kiosk"]].rename(columns={"date": "Expected date", "kiosk": "Kiosk"}), hide_index=True, width="stretch")
        else:
            st.caption("All expected reporting dates have a submission.")
    with right:
        st.subheader("Trend analytics")
        frame = pd.DataFrame(snapshot["trends"])
        if not frame.empty:
            frame["Date"] = pd.to_datetime(frame["Date"])
            charts = st.columns(2)
            with charts[0]:
                st.caption("Average food quality / 5")
                st.line_chart(frame, x="Date", y="quality", height=175, color="#238474")
                st.caption("Unclaimed lunches")
                st.bar_chart(frame, x="Date", y="unclaimed", height=175, color="#547ba4")
            with charts[1]:
                st.caption("Average food quantity / 5")
                st.line_chart(frame, x="Date", y="quantity", height=175, color="#547ba4")
                st.caption("Missing reports")
                st.bar_chart(frame, x="Date", y="missing", height=175, color="#bc454a")
            st.caption("Issue observations by " + ("day" if snapshot["daily"] else "week"))
            st.bar_chart(frame, x="Date", y="issues", height=175, color="#bf873c")
        else:
            st.info("No scheduled reports in this date range.")
        render_comparison(snapshot)

    with st.expander("Data quality and metric definitions"):
        st.write(f'{m["valid_reports"]} valid reports; {m["invalid"]} invalid submissions; {m["duplicates"]} duplicate submissions excluded. {m["received_slots"]} of {m["expected"]} scheduled kiosk/date slots received.')
        st.write("Averages and lunch counts use valid, deduplicated reports. Missing means no submission for an expected kiosk/date; invalid submissions are listed separately. Recurring issues appear on two or more reporting dates. Recognition counts distinct supporting reports, not people. Priority uses the same category rules as briefing emails.")
        st.write("Range totals combine weekly claims once per category and source. Confirmed weekly corrections affect these totals; monthly claim corrections remain scoped to their original claim. Unclaimed lunches are not a measured dollar loss or productivity score.")
        if snapshot["invalid_reports"]:
            st.dataframe(pd.DataFrame(snapshot["invalid_reports"])[["source_submission_id", "date", "kiosk", "validation_errors"]], hide_index=True)


def render_comparison(snapshot, *, detailed=False):
    st.subheader("Kiosk performance comparison")
    frame = pd.DataFrame(snapshot["comparison"])
    if frame.empty:
        st.info("No kiosk reports for the selected dates.")
        return
    columns = list(frame) if detailed else ["Kiosk", "Quality", "Unclaimed / report", "Missing", "Urgent findings"]
    st.dataframe(frame[columns], hide_index=True, width="stretch", column_config={
        "Quality": st.column_config.ProgressColumn("Quality / 5", min_value=0, max_value=5, format="%.2f"),
        "Quantity": st.column_config.ProgressColumn("Quantity / 5", min_value=0, max_value=5, format="%.2f"),
    })
    if detailed:
        st.bar_chart(frame, x="Kiosk", y="Unclaimed / report", color="#547ba4", height=300)
        st.download_button("Download comparison", frame.to_csv(index=False), "shiftnotes-kiosk-comparison.csv", "text/csv", icon=":material/download:")


def render_finding_sources(finding, reports, claims):
    lookup = {r["source_submission_id"]: r for r in reports}
    by_id = {c["claim_id"]: c for c in claims}
    if finding["sensitive"]:
        st.warning("Sensitive note: private human review required. This is not evidence of misconduct.")
    for source_id in finding["source_ids"]:
        source = lookup[source_id]
        st.markdown(f'**{source_id} | {source["date"]}**')
        for label, field in (
            ("Food concerns", "food_concerns_or_outages"),
            ("Recognition", "team_members_who_did_well"),
            ("Guest issues", "guest_issues_for_the_day"),
            ("Operations", "operational_notes"),
        ):
            st.markdown(f"**{label}**")
            st.write(source[field] or "No note recorded.")
    for claim_id in finding["claim_ids"]:
        claim = by_id[claim_id]
        st.link_button(f'Review / challenge {claim["period"]}', "?" + urlencode({"claim": claim_id, "action": "challenge"}), icon=":material/rate_review:")
