"""CSV dataset loading, cleaning, normalisation, and export."""
from __future__ import annotations

import os
from datetime import date

import pandas as pd
import streamlit as st

import config

CATEGORIES = [
    "Earthquake", "Flood", "Wildfire", "Volcano", "Storm", "Drought", "Landslide", "Other",
]

COLORS = {
    "Earthquake": "#EF4444",
    "Flood": "#3B82F6",
    "Wildfire": "#F97316",
    "Volcano": "#A855F7",
    "Storm": "#EAB308",
    "Drought": "#B45309",
    "Landslide": "#14B8A6",
    "Other": "#64748B",
}

LEVELS = ["Low", "Moderate", "High", "Critical"]

LEVEL_COLORS = {
    "Low": "#16A34A",
    "Moderate": "#D97706",
    "High": "#EA580C",
    "Critical": "#DC2626",
}

LEVEL_BG = {
    "Low": "#DCFCE7",
    "Moderate": "#FEF3C7",
    "High": "#FFEDD5",
    "Critical": "#FEE2E2",
}

COLUMNS = [
    "id", "type", "title", "country", "continent", "lat", "lon", "date",
    "end_date", "level", "measure", "magnitude", "active", "source", "url", "extra",
]

EXPORT_COLUMNS = [
    "id", "type", "title", "country", "continent", "lat", "lon", "date", "end_date",
    "level", "measure", "magnitude", "active", "source", "url",
]


def continent_of(lat: float, lon: float) -> str:
    """Fallback continent assignment when a CSV row omits continent."""
    if lat < -60:
        return "Antarctica"
    if -170 <= lon < -30:
        return "North America" if lat >= 8 else "South America"
    if -30 <= lon < 60 and lat >= 36:
        return "Europe"
    if -20 <= lon < 52 and -36 <= lat < 36:
        return "Asia" if (lat > 12 and lon > 34) else "Africa"
    if 26 <= lon <= 180 and lat >= -11:
        return "Asia"
    if lon >= 110 or lon < -150:
        return "Oceania"
    return "Ocean"


def to_level(value) -> str:
    """Normalise any severity/alert label or numeric score into Low / Moderate / High / Critical."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "Moderate"
    s = str(value).strip().lower()
    if s in {"red", "critical", "severe", "extreme", "catastrophic", "4"}:
        return "Critical"
    if s in {"orange", "high", "major", "3"}:
        return "High"
    if s in {"moderate", "medium", "yellow", "amber", "2"}:
        return "Moderate"
    if s in {"green", "low", "minor", "1"}:
        return "Low"
    try:
        n = float(s)
        return "Critical" if n >= 4 else "High" if n >= 3 else "Moderate" if n >= 2 else "Low"
    except ValueError:
        return "Moderate"


def to_type(value) -> str:
    """Map raw hazard labels to one of the canonical disaster categories."""
    s = str(value or "").strip().lower()
    if s.capitalize() in CATEGORIES:
        return s.capitalize()
    pairs = [
        ("quake", "Earthquake"), ("seismic", "Earthquake"), ("eq", "Earthquake"),
        ("flood", "Flood"), ("inundation", "Flood"), ("fl", "Flood"),
        ("fire", "Wildfire"), ("bushfire", "Wildfire"), ("wf", "Wildfire"),
        ("volcan", "Volcano"), ("eruption", "Volcano"), ("vo", "Volcano"),
        ("storm", "Storm"), ("cyclone", "Storm"), ("hurricane", "Storm"),
        ("typhoon", "Storm"), ("tornado", "Storm"), ("tc", "Storm"),
        ("drought", "Drought"), ("dr", "Drought"),
        ("landslide", "Landslide"), ("mudslide", "Landslide"), ("avalanche", "Landslide"),
    ]
    for key, cat in pairs:
        if (len(key) <= 2 and s == key) or (len(key) > 2 and key in s):
            return cat
    return "Other"


def _resolve_csv_path(configured: str) -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        configured,
        os.path.join(here, configured),
        os.path.join(here, "data", os.path.basename(configured)),
        os.path.join(here, "..", configured),
        os.path.join(here, "..", os.path.basename(configured)),
        os.path.join(here, "..", "public", os.path.basename(configured)),
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            return path
    raise FileNotFoundError(f"CSV dataset not found at '{configured}'.")


def _clean_str_series(series: pd.Series, fallback: str = "") -> pd.Series:
    return (
        series.fillna(fallback)
        .astype(str)
        .replace({"nan": fallback, "None": fallback, "<NA>": fallback})
        .str.strip()
    )


@st.cache_data(show_spinner=False)
def load_dataset(csv_path: str | None = None) -> pd.DataFrame:
    """Read and normalise the configured CSV file once into memory."""
    target = csv_path or config.CSV_PATH
    if not target:
        return pd.DataFrame(columns=COLUMNS + ["day", "last_day"])

    resolved = _resolve_csv_path(target)
    raw = pd.read_csv(resolved, low_memory=False)
    if raw.empty:
        return pd.DataFrame(columns=COLUMNS + ["day", "last_day"])

    lower = {c.lower().strip(): c for c in raw.columns}
    found: dict[str, str] = {}
    for key, aliases in config.CSV_COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in lower:
                found[key] = lower[alias]
                break

    if "lat" not in found or "lon" not in found or "date" not in found:
        raise ValueError("CSV must contain latitude, longitude, and date columns.")

    used = set(found.values())
    extra_cols = [c for c in raw.columns if c not in used]
    col = lambda k: raw[found[k]] if k in found else pd.Series([None] * len(raw))

    mag_num = pd.to_numeric(col("magnitude"), errors="coerce")
    if "measure" in found:
        raw_measure = _clean_str_series(col("measure"), "")
        fallback_measure = mag_num.map(lambda m: f"Magnitude / Value {m:g}" if pd.notna(m) else "Recorded event")
        measure = raw_measure.where(raw_measure != "", fallback_measure)
    else:
        measure = mag_num.map(lambda m: f"Magnitude / Value {m:g}" if pd.notna(m) else "Recorded event")

    active_col = (
        _clean_str_series(col("active"), "false")
        .str.lower()
        .isin({"true", "1", "yes", "y", "active", "ongoing", "open", "current"})
    )

    ids = (
        _clean_str_series(col("id"), "")
        if "id" in found
        else pd.Series([f"row-{i}" for i in range(len(raw))])
    )
    ids = ids.where(ids != "", pd.Series([f"row-{i}" for i in range(len(raw))]))

    df = pd.DataFrame({
        "id": ids,
        "type": col("type").map(to_type) if "type" in found else "Other",
        "title": _clean_str_series(col("title"), "Recorded disaster event") if "title" in found else "Recorded disaster event",
        "country": _clean_str_series(col("country"), "Unknown").replace("", "Unknown"),
        "continent": _clean_str_series(col("continent"), "") if "continent" in found else "",
        "lat": pd.to_numeric(col("lat"), errors="coerce"),
        "lon": pd.to_numeric(col("lon"), errors="coerce"),
        "date": pd.to_datetime(col("date"), errors="coerce", utc=True, format="ISO8601"),
        "end_date": pd.to_datetime(col("end_date"), errors="coerce", utc=True, format="ISO8601"),
        "level": col("severity").map(to_level) if "severity" in found else "Moderate",
        "measure": measure,
        "magnitude": mag_num,
        "active": active_col,
        "source": _clean_str_series(col("source"), "CSV").replace("", "CSV") if "source" in found else "CSV",
        "url": _clean_str_series(col("url"), "") if "url" in found else "",
    })

    if df["date"].isna().all():
        df["date"] = pd.to_datetime(col("date"), errors="coerce", utc=True)

    if extra_cols:
        extra_df = raw[extra_cols].fillna("").astype(str)
        df["extra"] = [
            {k: v for k, v in rec.items() if v.strip() and v != "nan"}
            for rec in extra_df.to_dict("records")
        ]
    else:
        df["extra"] = [{}] * len(raw)

    df = df.dropna(subset=["lat", "lon", "date"])
    df = df[df["lat"].between(-90, 90) & df["lon"].between(-180, 180)].copy()

    df["continent"] = [
        c if c else continent_of(la, lo)
        for c, la, lo in zip(df["continent"], df["lat"], df["lon"])
    ]
    df["type"] = df["type"].where(df["type"].isin(CATEGORIES), "Other")
    df["level"] = df["level"].where(df["level"].isin(LEVELS), "Moderate")
    df["day"] = df["date"].dt.date
    df["last_day"] = df["end_date"].dt.date.where(df["end_date"].notna(), df["day"])

    return df.drop_duplicates("id").sort_values("date", ascending=False).reset_index(drop=True)


def filter_by_date(df: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    """Return events occurring or active within [start, end] inclusive."""
    if df.empty:
        return df
    mask = (df["day"] <= end) & (df["last_day"] >= start)
    return df.loc[mask].reset_index(drop=True)


def to_csv(df: pd.DataFrame) -> bytes:
    """Serialise events to UTF-8 CSV bytes with BOM for clean Excel opening."""
    if df.empty:
        empty = pd.DataFrame(columns=[
            "id", "type", "title", "country", "continent", "latitude", "longitude",
            "date", "end_date", "state", "measure", "magnitude", "active", "source", "url",
        ])
        return empty.to_csv(index=False).encode("utf-8-sig")

    out = df[EXPORT_COLUMNS].rename(columns={"lat": "latitude", "lon": "longitude", "level": "state"}).copy()
    out["date"] = out["date"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    out["end_date"] = out["end_date"].dt.strftime("%Y-%m-%dT%H:%M:%SZ").fillna("")
    out["active"] = out["active"].map({True: "Active", False: "Historical"})
    return out.to_csv(index=False).encode("utf-8-sig")
