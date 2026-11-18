"""Design system, CSS overrides, and reusable UI components."""
from __future__ import annotations

import html
import pandas as pd
import streamlit as st

from data import COLORS, LEVEL_BG, LEVEL_COLORS, LEVELS

BG = "#F6F8FB"
PANEL = "#FFFFFF"
BORDER = "#E2E8F0"
TEXT = "#0F172A"
SECONDARY = "#475569"
MUTED = "#64748B"
ACCENT = "#0B5FFF"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

html, body, [class*="css"], [data-testid="stAppViewContainer"] * {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
}}

[data-testid="stAppViewContainer"] {{
    background: {BG};
    color: {TEXT};
}}

[data-testid="stHeader"] {{
    background: {PANEL} !important;
    border-bottom: 1px solid {BORDER};
}}

#MainMenu, .stDeployButton, [data-testid="stToolbarActions"], [data-testid="stDecoration"] {{
    display: none !important;
}}

.block-container {{
    padding-top: 1.35rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1520px !important;
}}

/* Sidebar polish */
[data-testid="stSidebar"] {{
    background: {PANEL} !important;
    border-right: 1px solid {BORDER} !important;
}}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
    color: {SECONDARY};
}}

.sb-brand {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 0 12px;
    border-bottom: 1px solid {BORDER};
    margin-bottom: 12px;
}}

.sb-dot {{
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: {ACCENT};
    box-shadow: 0 0 0 4px rgba(11, 95, 255, 0.14);
    flex-shrink: 0;
}}

.sb-title {{
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.06em;
    color: {TEXT};
    text-transform: uppercase;
}}

.sb-scope {{
    background: #F8FAFC;
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 10px;
    font-size: 12px;
    color: {SECONDARY};
    margin-bottom: 10px;
    line-height: 1.45;
}}

.sb-scope b {{
    color: {TEXT};
    font-weight: 600;
}}

.sb-sec {{
    font-size: 10.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.13em;
    color: {MUTED};
    margin: 16px 0 6px;
    padding-top: 12px;
    border-top: 1px solid #EEF2F6;
}}

/* Multiselect chips & inputs */
[data-baseweb="tag"] {{
    background-color: #EFF6FF !important;
    border: 1px solid #BFDBFE !important;
    border-radius: 6px !important;
}}

[data-baseweb="tag"] span {{
    color: #1E40AF !important;
    font-weight: 600 !important;
    font-size: 12px !important;
}}

[data-baseweb="tag"] svg {{
    fill: #1E40AF !important;
}}

[data-testid="stDownloadButton"] button {{
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border: 1px solid {BORDER} !important;
    transition: all 0.15s ease !important;
}}

[data-testid="stDownloadButton"]:first-of-type button {{
    background: {ACCENT} !important;
    color: #FFFFFF !important;
    border-color: {ACCENT} !important;
}}

[data-testid="stDownloadButton"]:first-of-type button * {{
    color: #FFFFFF !important;
}}

[data-testid="stDownloadButton"]:first-of-type button:hover {{
    background: #084CD6 !important;
    border-color: #084CD6 !important;
}}

/* Executive KPI & State Cards */
.kpi-card {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 18px 20px;
    position: relative;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03), 0 4px 12px rgba(15, 23, 42, 0.03);
    height: 100%;
}}

.kpi-card::before {{
    content: "";
    position: absolute;
    left: 0;
    top: 14px;
    bottom: 14px;
    width: 3.5px;
    border-radius: 0 4px 4px 0;
    background: var(--accent, {ACCENT});
}}

.kpi-lbl {{
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.11em;
    color: {MUTED};
}}

.kpi-val {{
    font-size: 27px;
    font-weight: 800;
    color: {TEXT};
    margin-top: 7px;
    line-height: 1.15;
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.kpi-sub {{
    font-size: 12.5px;
    color: {SECONDARY};
    margin-top: 5px;
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.state-bar-track {{
    height: 5px;
    background: #F1F5F9;
    border-radius: 999px;
    overflow: hidden;
    margin-top: 10px;
}}

.state-bar-fill {{
    height: 100%;
    border-radius: 999px;
}}

/* Section panels */
.panel-box {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03), 0 4px 12px rgba(15, 23, 42, 0.03);
}}

.sec-hdr {{
    font-size: 11.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.11em;
    color: {SECONDARY};
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}

/* Category progress rows */
.cat-row {{
    margin-bottom: 13px;
}}
.cat-row:last-child {{
    margin-bottom: 0;
}}
.cat-top {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 13px;
    margin-bottom: 5px;
}}
.cat-name {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    color: {TEXT};
}}
.cat-dot {{
    width: 9px;
    height: 9px;
    border-radius: 50%;
    display: inline-block;
}}
.cat-num {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: {SECONDARY};
}}

/* Disaster per-type 4-state card */
.dtype-card {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-top: 3px solid var(--c, {ACCENT});
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
}}
.dtype-head {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
}}
.dtype-title {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-weight: 700;
    font-size: 14px;
    color: {TEXT};
}}
.dtype-total {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 600;
    color: {SECONDARY};
    background: #F1F5F9;
    padding: 2px 8px;
    border-radius: 999px;
}}
.dtype-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 6px;
}}
.dtype-chip {{
    border-radius: 8px;
    padding: 7px 4px;
    text-align: center;
}}
.dtype-chip-val {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    font-weight: 700;
    line-height: 1.2;
}}
.dtype-chip-lbl {{
    font-size: 10.5px;
    font-weight: 600;
    margin-top: 2px;
}}

/* Styled HTML register table */
.reg-wrap {{
    max-height: 410px;
    overflow-y: auto;
    border: 1px solid {BORDER};
    border-radius: 10px;
}}
.reg-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 12.5px;
    background: {PANEL};
}}
.reg-table th {{
    position: sticky;
    top: 0;
    background: #F8FAFC;
    color: {MUTED};
    text-transform: uppercase;
    letter-spacing: 0.09em;
    font-size: 10.5px;
    font-weight: 700;
    text-align: left;
    padding: 10px 12px;
    border-bottom: 1px solid {BORDER};
    z-index: 2;
}}
.reg-table td {{
    padding: 9px 12px;
    border-bottom: 1px solid #F1F5F9;
    color: {TEXT};
    vertical-align: middle;
}}
.reg-table tr:hover td {{
    background: #F8FAFC;
}}
.pill-type {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 2px 8px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 11.5px;
    white-space: nowrap;
}}
.pill-state {{
    display: inline-block;
    padding: 2.5px 9px;
    border-radius: 999px;
    font-weight: 700;
    font-size: 11px;
    color: #FFFFFF;
    letter-spacing: 0.02em;
    white-space: nowrap;
}}
.status-active {{
    color: #15803D;
    font-weight: 600;
    font-size: 11.5px;
    white-space: nowrap;
}}
.status-hist {{
    color: {MUTED};
    font-size: 11.5px;
    white-space: nowrap;
}}

/* Plotly & Map containers */
[data-testid="stPlotlyChart"] {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 8px 10px 4px;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03), 0 4px 12px rgba(15, 23, 42, 0.03);
}}

iframe {{
    border: 1px solid #1E293B !important;
    border-radius: 12px !important;
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.12) !important;
}}
</style>
"""


def apply():
    st.markdown(CSS, unsafe_allow_html=True)


def card(label: str, value, sub: str = "", color: str = ACCENT):
    val_txt = html.escape(str(value))
    sub_txt = html.escape(str(sub))
    st.markdown(
        f'<div class="kpi-card" style="--accent:{color}">'
        f'<div class="kpi-lbl">{html.escape(label)}</div>'
        f'<div class="kpi-val" title="{val_txt}">{val_txt}</div>'
        f'<div class="kpi-sub" title="{sub_txt}">{sub_txt}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_state_strip(df: pd.DataFrame):
    """Render Low / Moderate / High / Critical state cards in distinct colours."""
    total = max(len(df), 1)
    cols = st.columns(4)
    for col, lvl in zip(cols, LEVELS):
        n = int((df["level"] == lvl).sum()) if not df.empty else 0
        pct = n / total * 100
        clr = LEVEL_COLORS[lvl]
        with col:
            st.markdown(
                f'<div class="kpi-card" style="--accent:{clr}">'
                f'<div style="display:flex;justify-content:space-between;align-items:center">'
                f'<span class="kpi-lbl">State · {lvl}</span>'
                f'<span class="pill-state" style="background:{clr}">{lvl}</span>'
                f'</div>'
                f'<div class="kpi-val">{n:,}</div>'
                f'<div class="kpi-sub">{pct:.1f}% of filtered events</div>'
                f'<div class="state-bar-track"><div class="state-bar-fill" style="width:{max(pct, 2 if n else 0):.1f}%;background:{clr}"></div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )


def render_disaster_state_cards(df: pd.DataFrame, categories: list[str]):
    """For each active disaster category, show Low / Moderate / High / Critical in 4 distinct colours."""
    if not categories:
        return
    ncols = min(len(categories), 4)
    cols = st.columns(ncols)
    for idx, cat in enumerate(categories):
        sub = df[df["type"] == cat]
        chips = []
        for lvl in LEVELS:
            cnt = int((sub["level"] == lvl).sum())
            c_fg = LEVEL_COLORS[lvl]
            c_bg = LEVEL_BG[lvl]
            chips.append(
                f'<div class="dtype-chip" style="background:{c_bg};border:1px solid {c_fg}38">'
                f'<div class="dtype-chip-val" style="color:{c_fg}">{cnt:,}</div>'
                f'<div class="dtype-chip-lbl" style="color:{c_fg}">{lvl}</div>'
                f'</div>'
            )
        with cols[idx % ncols]:
            st.markdown(
                f'<div class="dtype-card" style="--c:{COLORS[cat]}">'
                f'<div class="dtype-head">'
                f'<span class="dtype-title"><span class="cat-dot" style="background:{COLORS[cat]}"></span>{cat}</span>'
                f'<span class="dtype-total">{len(sub):,} events</span>'
                f'</div>'
                f'<div class="dtype-grid">{"".join(chips)}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


def render_category_bars(df: pd.DataFrame):
    """Render proportional horizontal bars per disaster category inside a sleek panel."""
    counts = df["type"].value_counts()
    total = max(len(df), 1)
    top_n = max(int(counts.iloc[0]), 1) if len(counts) else 1
    rows = []
    for cat, n in counts.items():
        pct = n / total * 100
        w = n / top_n * 100
        clr = COLORS.get(cat, "#64748B")
        rows.append(
            f'<div class="cat-row">'
            f'<div class="cat-top">'
            f'<span class="cat-name"><span class="cat-dot" style="background:{clr}"></span>{html.escape(str(cat))}</span>'
            f'<span class="cat-num">{int(n):,} ({pct:.1f}%)</span>'
            f'</div>'
            f'<div class="state-bar-track"><div class="state-bar-fill" style="width:{w:.1f}%;background:{clr}"></div></div>'
            f'</div>'
        )
    st.markdown(
        f'<div class="panel-box"><div class="sec-hdr"><span>Category Distribution</span>'
        f'<span>{len(counts)} types</span></div>{"".join(rows)}</div>',
        unsafe_allow_html=True,
    )


def render_events_table(df: pd.DataFrame, title: str, limit: int = 80):
    """Render a clean, high-contrast scrollable event register with distinct state pills."""
    subset = df.head(limit)
    body = []
    for r in subset.itertuples():
        t_clr = COLORS.get(r.type, "#64748B")
        s_clr = LEVEL_COLORS.get(r.level, "#64748B")
        status_html = (
            '<span class="status-active">● Active</span>'
            if r.active else '<span class="status-hist">Historical</span>'
        )
        title_cell = html.escape(str(r.title))
        if r.url:
            safe_url = html.escape(str(r.url), quote=True)
            title_cell = f'<a href="{safe_url}" target="_blank" style="color:{TEXT};text-decoration:none;font-weight:600">{title_cell} ↗</a>'
        else:
            title_cell = f'<span style="font-weight:600">{title_cell}</span>'
        body.append(
            f"<tr>"
            f"<td><span class='pill-type' style='background:{t_clr}16;color:{t_clr}'>"
            f"<span class='cat-dot' style='background:{t_clr}'></span>{html.escape(str(r.type))}</span></td>"
            f"<td style='max-width:290px'>{title_cell}</td>"
            f"<td>{html.escape(str(r.country))}<div style='font-size:11px;color:{MUTED}'>{html.escape(str(r.continent))}</div></td>"
            f"<td style='font-family:JetBrains Mono,monospace;font-size:11.5px;white-space:nowrap'>{r.date:%Y-%m-%d %H:%M}</td>"
            f"<td><span class='pill-state' style='background:{s_clr}'>{html.escape(str(r.level))}</span></td>"
            f"<td style='color:{SECONDARY};max-width:220px'>{html.escape(str(r.measure))}</td>"
            f"<td>{status_html}</td>"
            f"</tr>"
        )
    st.markdown(
        f'<div class="panel-box">'
        f'<div class="sec-hdr"><span>{html.escape(title)}</span>'
        f'<span>Showing {len(subset):,} of {len(df):,}</span></div>'
        f'<div class="reg-wrap"><table class="reg-table">'
        f'<thead><tr><th>Type</th><th>Event</th><th>Location</th><th>Date (UTC)</th>'
        f'<th>State</th><th>Measurement</th><th>Status</th></tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table></div></div>',
        unsafe_allow_html=True,
    )


def plotly_layout(fig, height: int = 350, show_legend: bool = True):
    """Apply consistent light-mode executive styling to a Plotly figure."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        height=height,
        showlegend=show_legend,
        font=dict(color=TEXT, size=12, family="Inter, system-ui, sans-serif"),
        margin=dict(l=12, r=14, t=46, b=16),
        title=dict(font=dict(size=14, color=TEXT, family="Inter, sans-serif"), x=0.01),
        legend=dict(
            font=dict(color=SECONDARY, size=11.5),
            orientation="h",
            yanchor="top",
            y=-0.14,
            xanchor="left",
            x=0,
            title_text="",
        ),
        hoverlabel=dict(
            bgcolor="#0F172A",
            bordercolor="#1E293B",
            font=dict(color="#FFFFFF", size=12, family="Inter, sans-serif"),
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor=BORDER,
        tickfont=dict(color=SECONDARY, size=11),
        title_font=dict(color=MUTED, size=11.5),
    )
    fig.update_yaxes(
        gridcolor="#F1F5F9",
        linecolor=BORDER,
        tickfont=dict(color=SECONDARY, size=11),
        title_font=dict(color=MUTED, size=11.5),
    )
    return fig
