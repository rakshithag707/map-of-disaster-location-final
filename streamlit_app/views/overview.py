"""Overview page — executive KPIs, 4-state breakdown, and priority event register."""
import streamlit as st

from data import COLORS
from theme import card, render_category_bars, render_events_table, render_state_strip

df = st.session_state["df"]

if df.empty:
    st.info("No disaster records match the current filter selection.")
    st.stop()

top_type = df["type"].value_counts()
top_cont = df["continent"].value_counts()
land = df[~df["country"].isin(["Unknown", "International Waters"])]["country"].value_counts()
active_n = int(df["active"].sum())
high_crit_n = int(df["level"].isin(["High", "Critical"]).sum())

c1, c2, c3, c4 = st.columns(4)
with c1:
    card(
        "Total Recorded Events",
        f"{len(df):,}",
        f"{high_crit_n:,} high or critical · {len(df) - active_n:,} historical",
        "#0B5FFF",
    )
with c2:
    pct_active = active_n / len(df) * 100
    card(
        "Active Events",
        f"{active_n:,}",
        f"{pct_active:.1f}% currently active",
        "#16A34A",
    )
with c3:
    dom_cat = str(top_type.index[0])
    card(
        "Most Frequent Type",
        dom_cat,
        f"{int(top_type.iloc[0]):,} recorded events ({top_type.iloc[0] / len(df) * 100:.1f}%)",
        COLORS.get(dom_cat, "#0B5FFF"),
    )
with c4:
    dom_region = str(top_cont.index[0])
    sub_country = f"Top country: {land.index[0]} ({int(land.iloc[0]):,})" if len(land) else f"{int(top_cont.iloc[0]):,} events"
    card("Most Affected Region", dom_region, sub_country, "#7C3AED")

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
render_state_strip(df)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
left, right = st.columns([1.05, 2.15], gap="medium")
with left:
    render_category_bars(df)
    sample_extra = next((d for d in df["extra"] if d), None)
    if sample_extra:
        cols_txt = ", ".join(list(sample_extra.keys())[:8])
        st.markdown(
            f"<div class='panel-box' style='margin-top:12px'>"
            f"<div class='sec-hdr'><span>Custom CSV Fields</span></div>"
            f"<div style='font-size:12.5px;color:#475569'>Detected additional columns: <b>{cols_txt}</b>. "
            f"Click any map marker on the Disaster Map tab to inspect custom row fields.</div></div>",
            unsafe_allow_html=True,
        )

with right:
    priority = df[df["level"].isin(["Critical", "High"]) | df["active"]]
    if priority.empty:
        render_events_table(df, "Latest Recorded Events", limit=80)
    else:
        render_events_table(priority, "Priority Register · Critical, High & Active Events", limit=80)
