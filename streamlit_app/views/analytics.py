"""Analytics page — interactive Plotly charts for temporal, category, and 4-state analysis."""
import plotly.express as px
import streamlit as st

from data import COLORS, LEVEL_COLORS, LEVELS
from theme import plotly_layout

df = st.session_state["df"]

if df.empty:
    st.info("No disaster records match the current filter selection.")
    st.stop()

span_days = max((df["date"].max() - df["date"].min()).days, 0)
if span_days > 400:
    freq, freq_lbl = "M", "Monthly"
elif span_days > 90:
    freq, freq_lbl = "W", "Weekly"
else:
    freq, freq_lbl = "D", "Daily"

ts = (
    df.assign(period=df["date"].dt.tz_localize(None).dt.to_period(freq).dt.start_time)
    .groupby(["period", "type"])
    .size()
    .reset_index(name="events")
)
fig_ts = px.area(
    ts,
    x="period",
    y="events",
    color="type",
    color_discrete_map=COLORS,
    title=f"Disaster Occurrence Over Time ({freq_lbl})",
    labels={"period": "", "events": "Recorded Events", "type": "Category"},
)
fig_ts.update_traces(line=dict(width=1.8))
st.plotly_chart(plotly_layout(fig_ts, height=370), use_container_width=True)

c1, c2 = st.columns(2, gap="medium")
counts = df["type"].value_counts().reset_index()
counts.columns = ["type", "events"]

with c1:
    fig_bar = px.bar(
        counts,
        x="events",
        y="type",
        orientation="h",
        color="type",
        text="events",
        color_discrete_map=COLORS,
        title="Disaster Frequency by Category",
        labels={"events": "Events", "type": ""},
    )
    fig_bar.update_traces(texttemplate="%{text:,}", textposition="outside", cliponaxis=False)
    fig_bar.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(plotly_layout(fig_bar, height=350, show_legend=False), use_container_width=True)

with c2:
    fig_pie = px.pie(
        counts,
        names="type",
        values="events",
        hole=0.60,
        color="type",
        color_discrete_map=COLORS,
        title="Share by Disaster Category",
    )
    fig_pie.update_traces(
        marker=dict(line=dict(color="#FFFFFF", width=2)),
        textposition="inside",
        textinfo="percent",
        insidetextorientation="horizontal",
    )
    fig_pie.add_annotation(
        text=f"<b>{len(df):,}</b><br><span style='font-size:11px;color:#64748B'>Total</span>",
        showarrow=False,
        font=dict(size=16, color="#0F172A"),
    )
    st.plotly_chart(plotly_layout(fig_pie, height=350), use_container_width=True)

c3, c4 = st.columns(2, gap="medium")
with c3:
    sev_by_type = df.groupby(["level", "type"]).size().reset_index(name="events")
    fig_sev = px.bar(
        sev_by_type,
        x="level",
        y="events",
        color="type",
        color_discrete_map=COLORS,
        category_orders={"level": LEVELS},
        title="Disaster State Breakdown by Category (Low · Moderate · High · Critical)",
        labels={"level": "Disaster State", "events": "Events", "type": "Category"},
    )
    st.plotly_chart(plotly_layout(fig_sev, height=350), use_container_width=True)

with c4:
    lv_counts = df["level"].value_counts().reindex(LEVELS, fill_value=0).reset_index()
    lv_counts.columns = ["level", "events"]
    fig_lv = px.pie(
        lv_counts,
        names="level",
        values="events",
        hole=0.60,
        color="level",
        category_orders={"level": LEVELS},
        color_discrete_map=LEVEL_COLORS,
        title="Overall State Distribution",
    )
    fig_lv.update_traces(marker=dict(line=dict(color="#FFFFFF", width=2)), textinfo="percent+label")
    st.plotly_chart(plotly_layout(fig_lv, height=350), use_container_width=True)

c5, c6 = st.columns(2, gap="medium")
with c5:
    act_df = (
        df.assign(status=df["active"].map({True: "Active", False: "Historical"}))
        .groupby(["type", "status"])
        .size()
        .reset_index(name="events")
    )
    fig_act = px.bar(
        act_df,
        x="type",
        y="events",
        color="status",
        barmode="group",
        color_discrete_map={"Active": "#16A34A", "Historical": "#94A3B8"},
        title="Active vs Historical Events by Category",
        labels={"type": "", "events": "Events", "status": "Status"},
    )
    st.plotly_chart(plotly_layout(fig_act, height=340), use_container_width=True)

with c6:
    eq = df[(df["type"] == "Earthquake") & df["magnitude"].notna()]
    if not eq.empty:
        fig_mag = px.histogram(
            eq,
            x="magnitude",
            color="level",
            nbins=28,
            category_orders={"level": LEVELS},
            color_discrete_map=LEVEL_COLORS,
            title="Earthquake Magnitude & State Profile",
            labels={"magnitude": "Magnitude (Mw / mb)", "count": "Events", "level": "State"},
        )
        st.plotly_chart(plotly_layout(fig_mag, height=340), use_container_width=True)
    else:
        num = df[df["magnitude"].notna()]
        if not num.empty:
            fig_mag = px.histogram(
                num,
                x="magnitude",
                color="level",
                nbins=24,
                category_orders={"level": LEVELS},
                color_discrete_map=LEVEL_COLORS,
                title="Recorded Intensity / Magnitude Distribution",
                labels={"magnitude": "Measured Value", "level": "State"},
            )
            st.plotly_chart(plotly_layout(fig_mag, height=340), use_container_width=True)
        else:
            st.info("No numeric magnitude measurements available in the current selection.")
