"""Regional Analysis page — continental comparison, top countries, and country deep-dive."""
import html
import plotly.express as px
import streamlit as st

from data import COLORS, LEVEL_BG, LEVEL_COLORS, LEVELS
from theme import card, plotly_layout

df = st.session_state["df"]

if df.empty:
    st.info("No disaster records match the current filter selection.")
    st.stop()

r1, r2 = st.columns(2, gap="medium")
with r1:
    by_cont = df.groupby(["continent", "type"]).size().reset_index(name="events")
    fig_cont = px.bar(
        by_cont,
        x="continent",
        y="events",
        color="type",
        color_discrete_map=COLORS,
        title="Continents Compared by Disaster Category",
        labels={"continent": "", "events": "Events", "type": "Category"},
    )
    fig_cont.update_layout(xaxis=dict(categoryorder="total descending"))
    st.plotly_chart(plotly_layout(fig_cont, height=370), use_container_width=True)

with r2:
    lv_cont = df.groupby(["continent", "level"]).size().reset_index(name="events")
    fig_lv = px.bar(
        lv_cont,
        x="continent",
        y="events",
        color="level",
        color_discrete_map=LEVEL_COLORS,
        category_orders={"level": LEVELS},
        title="Disaster States Across Continents (Low · Moderate · High · Critical)",
        labels={"continent": "", "events": "Events", "level": "State"},
    )
    fig_lv.update_layout(xaxis=dict(categoryorder="total descending"))
    st.plotly_chart(plotly_layout(fig_lv, height=370), use_container_width=True)

land_df = df[~df["country"].isin(["Unknown", "International Waters"])]
country_pool = land_df if not land_df.empty else df

c1, c2 = st.columns([1.15, 1.0], gap="medium")
with c1:
    top_countries = country_pool["country"].value_counts().head(15).reset_index()
    top_countries.columns = ["country", "events"]
    fig_top = px.bar(
        top_countries,
        x="events",
        y="country",
        orientation="h",
        text="events",
        title="Most Affected Countries & Territories (Top 15)",
        labels={"events": "Recorded Events", "country": ""},
        color_discrete_sequence=["#0B5FFF"],
    )
    fig_top.update_traces(texttemplate="%{text:,}", textposition="outside", cliponaxis=False)
    fig_top.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(plotly_layout(fig_top, height=455, show_legend=False), use_container_width=True)

with c2:
    st.markdown(
        "<div class='sec-hdr' style='margin:4px 0 8px'><span>Country Profile</span></div>",
        unsafe_allow_html=True,
    )
    ordered_countries = list(country_pool["country"].value_counts().index)
    chosen_country = st.selectbox("Inspect country", ordered_countries, label_visibility="collapsed")
    sub = df[df["country"] == chosen_country]
    dom_mode = sub["type"].mode()
    dom_type = str(dom_mode.iloc[0]) if len(dom_mode) else "-"
    high_crit = int(sub["level"].isin(["High", "Critical"]).sum())

    k1, k2 = st.columns(2)
    with k1:
        card("Country Events", f"{len(sub):,}", f"{len(sub) / len(df) * 100:.1f}% of selection", "#0B5FFF")
    with k2:
        card("Active Events", f"{int(sub['active'].sum()):,}", f"{high_crit:,} high or critical", "#16A34A")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    k3, k4 = st.columns(2)
    with k3:
        card("Dominant Disaster", dom_type, f"Continent: {sub['continent'].iloc[0]}", COLORS.get(dom_type, "#0B5FFF"))
    with k4:
        crit_cnt = int((sub["level"] == "Critical").sum())
        card("Critical Events", f"{crit_cnt:,}", "Highest severity tier", LEVEL_COLORS["Critical"])

    chips = "".join(
        f"<div class='dtype-chip' style='background:{LEVEL_BG[l]};border:1px solid {LEVEL_COLORS[l]}38'>"
        f"<div class='dtype-chip-val' style='color:{LEVEL_COLORS[l]}'>{int((sub['level'] == l).sum()):,}</div>"
        f"<div class='dtype-chip-lbl' style='color:{LEVEL_COLORS[l]}'>{l}</div></div>"
        for l in LEVELS
    )
    st.markdown(
        f"<div class='panel-box' style='margin-top:12px'>"
        f"<div class='sec-hdr'><span>{html.escape(str(chosen_country))} · State Breakdown</span></div>"
        f"<div class='dtype-grid'>{chips}</div></div>",
        unsafe_allow_html=True,
    )

# Continental Summary Table (includes all 4 states: Critical, High, Moderate, Low)
stats = (
    df.groupby("continent")
    .agg(
        events=("id", "count"),
        active=("active", "sum"),
        critical=("level", lambda s: int((s == "Critical").sum())),
        high=("level", lambda s: int((s == "High").sum())),
        moderate=("level", lambda s: int((s == "Moderate").sum())),
        low=("level", lambda s: int((s == "Low").sum())),
        countries=("country", lambda s: int(s[~s.isin(["Unknown", "International Waters"])].nunique())),
        dominant=("type", lambda s: str(s.mode().iloc[0])),
    )
    .sort_values("events", ascending=False)
    .reset_index()
)

rows_html = []
for r in stats.itertuples():
    d_clr = COLORS.get(r.dominant, "#64748B")
    rows_html.append(
        f"<tr>"
        f"<td style='font-weight:700'>{html.escape(str(r.continent))}</td>"
        f"<td style='font-family:JetBrains Mono,monospace;font-weight:700'>{r.events:,}</td>"
        f"<td style='font-family:JetBrains Mono,monospace;color:#15803D;font-weight:600'>{int(r.active):,}</td>"
        f"<td><span class='pill-state' style='background:{LEVEL_COLORS['Critical']}'>{r.critical:,}</span></td>"
        f"<td><span class='pill-state' style='background:{LEVEL_COLORS['High']}'>{r.high:,}</span></td>"
        f"<td><span class='pill-state' style='background:{LEVEL_COLORS['Moderate']}'>{r.moderate:,}</span></td>"
        f"<td><span class='pill-state' style='background:{LEVEL_COLORS['Low']}'>{r.low:,}</span></td>"
        f"<td style='font-family:JetBrains Mono,monospace'>{r.countries:,}</td>"
        f"<td><span class='pill-type' style='background:{d_clr}16;color:{d_clr}'>"
        f"<span class='cat-dot' style='background:{d_clr}'></span>{html.escape(r.dominant)}</span></td>"
        f"</tr>"
    )

st.markdown(
    f"<div class='panel-box' style='margin-top:16px'>"
    f"<div class='sec-hdr'><span>Regional Summary Statistics</span>"
    f"<span>{len(stats)} regions</span></div>"
    f"<div class='reg-wrap'><table class='reg-table'>"
    f"<thead><tr><th>Continent / Region</th><th>Total Events</th><th>Active</th>"
    f"<th>Critical</th><th>High</th><th>Moderate</th><th>Low</th>"
    f"<th>Countries</th><th>Dominant Category</th></tr></thead>"
    f"<tbody>{''.join(rows_html)}</tbody></table></div></div>",
    unsafe_allow_html=True,
)
