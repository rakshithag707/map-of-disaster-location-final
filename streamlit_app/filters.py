"""Sidebar controls shared across all four pages."""
from __future__ import annotations

from datetime import date, timedelta
import html

import pandas as pd
import streamlit as st

from data import CATEGORIES, LEVELS, filter_by_date, load_dataset, to_csv


def _sorted_countries(values) -> list[str]:
    tail = {"International Waters", "Unknown"}
    main = sorted(v for v in values if v and v not in tail)
    rest = [v for v in ("International Waters", "Unknown") if v in values]
    return main + rest


def sidebar() -> tuple[pd.DataFrame, str]:
    sb = st.sidebar
    sb.markdown(
        '<div class="sb-brand"><span class="sb-dot"></span>'
        '<span class="sb-title">Disaster Monitor</span></div>',
        unsafe_allow_html=True,
    )

    try:
        full_df = load_dataset()
    except Exception as exc:
        sb.error(f"Dataset error: {exc}")
        st.stop()

    if full_df.empty:
        sb.warning("The configured CSV dataset contains no valid records.")
        return full_df, "Empty dataset"

    min_day: date = full_df["day"].min()
    max_day: date = max(full_df["day"].max(), full_df["last_day"].max())
    default_start = max(min_day, max_day - timedelta(days=30))

    sb.markdown('<div class="sb-sec">Date Filter</div>', unsafe_allow_html=True)
    mode = sb.radio(
        "Date mode",
        ["Date range", "Single day"],
        horizontal=True,
        label_visibility="collapsed",
    )
    if mode == "Single day":
        chosen_day = sb.date_input(
            "Select date",
            value=max_day,
            min_value=min_day,
            max_value=max_day,
        )
        start = end = chosen_day
    else:
        c_s, c_e = sb.columns(2)
        with c_s:
            start = st.date_input(
                "Start date",
                value=default_start,
                min_value=min_day,
                max_value=max_day,
            )
        with c_e:
            end = st.date_input(
                "End date",
                value=max_day,
                min_value=min_day,
                max_value=max_day,
            )

    if start > end:
        sb.error("Start date must be on or before end date.")
        st.stop()

    dated_df = filter_by_date(full_df, start, end)

    sb.markdown('<div class="sb-sec">Location</div>', unsafe_allow_html=True)
    continents = sorted(c for c in dated_df["continent"].unique() if c)
    cont = sb.selectbox("Continent", ["All"] + continents)
    scope = dated_df if cont == "All" else dated_df[dated_df["continent"] == cont]

    countries = _sorted_countries(set(scope["country"].unique()))
    country = sb.selectbox("Country", ["All"] + countries)

    sb.markdown('<div class="sb-sec">Disaster Categories</div>', unsafe_allow_html=True)
    available_cats = [c for c in CATEGORIES if c in set(full_df["type"].unique())] or CATEGORIES
    if "sel_types" not in st.session_state:
        st.session_state["sel_types"] = list(available_cats)
    if len(st.session_state["sel_types"]) < len(available_cats):
        if sb.button("Select all categories", key="reset_cats"):
            st.session_state["sel_types"] = list(available_cats)
            st.rerun()
    types = sb.multiselect(
        "Categories",
        options=available_cats,
        key="sel_types",
        label_visibility="collapsed",
    )

    sb.markdown('<div class="sb-sec">Disaster State & Status</div>', unsafe_allow_html=True)
    levels = sb.multiselect("State", options=LEVELS, default=LEVELS, label_visibility="collapsed")
    status = sb.radio("Event status", ["All", "Active", "Historical"], horizontal=True)

    filtered = scope if country == "All" else scope[scope["country"] == country]
    filtered = filtered[filtered["type"].isin(types) & filtered["level"].isin(levels)]
    if status != "All":
        filtered = filtered[filtered["active"] == (status == "Active")]
    filtered = filtered.reset_index(drop=True)

    label = start.isoformat() if start == end else f"{start.isoformat()} → {end.isoformat()}"
    loc_txt = "Global"
    if cont != "All" and country != "All":
        loc_txt = f"{country}, {cont}"
    elif cont != "All":
        loc_txt = cont
    elif country != "All":
        loc_txt = country

    sb.markdown(
        f'<div class="sb-sec">Active Selection</div>'
        f'<div class="sb-scope">'
        f'<div><b>Window:</b> {html.escape(label)}</div>'
        f'<div><b>Scope:</b> {html.escape(loc_txt)}</div>'
        f'<div><b>Matched:</b> {len(filtered):,} events</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    sb.markdown('<div class="sb-sec">CSV Dataset</div>', unsafe_allow_html=True)
    sb.download_button(
        label="Download Filtered CSV",
        data=to_csv(filtered),
        file_name=f"disasters_{start}_{end}.csv",
        mime="text/csv",
        disabled=filtered.empty,
    )
    sb.download_button(
        label="Download Full CSV Dataset",
        data=to_csv(full_df),
        file_name="disaster_data.csv",
        mime="text/csv",
    )

    full_label = f"{label} · {loc_txt}"
    return filtered, full_label
