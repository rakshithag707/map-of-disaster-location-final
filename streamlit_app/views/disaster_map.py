"""Disaster Map page — per-hazard 4-state breakdown & black interactive Folium map."""
import html

import folium
import streamlit as st
import streamlit.components.v1 as components

from config import MAX_MAP_MARKERS
from data import CATEGORIES, COLORS, LEVEL_COLORS, LEVELS
from theme import render_disaster_state_cards

df = st.session_state["df"]

if df.empty:
    st.info("No disaster records match the current filter selection.")
    st.stop()

MAP_COLORS = {**COLORS, "Storm": "#FACC15", "Drought": "#D97706", "Other": "#94A3B8"}
RADIUS = {"Low": 4.5, "Moderate": 6.5, "High": 9.0, "Critical": 12.0}

present = [c for c in CATEGORIES if (df["type"] == c).any()]
render_disaster_state_cards(df, present)

# Intelligent map centering based on geographic scope
n_countries = df["country"].nunique()
n_continents = df["continent"].nunique()
if n_countries == 1 and df["country"].iloc[0] not in ("International Waters", "Unknown"):
    lat_span = float(df["lat"].max() - df["lat"].min())
    lon_span = float(df["lon"].max() - df["lon"].min())
    span = max(lat_span, lon_span)
    zoom = 6 if span < 4 else 5 if span < 12 else 4 if span < 28 else 3
    center = [float(df["lat"].median()), float(df["lon"].median())]
elif n_continents == 1:
    center = [float(df["lat"].median()), float(df["lon"].median())]
    zoom = 3
else:
    center, zoom = [18.0, 12.0], 2

m = folium.Map(
    location=center,
    zoom_start=zoom,
    tiles=None,
    prefer_canvas=True,
    world_copy_jump=True,
    min_zoom=2,
    max_zoom=18,
    control_scale=True,
)

# Official keyless public map tile APIs (Esri ArcGIS REST MapServer & NASA Earthdata GIBS WMTS)
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
    attr="Esri, HERE, Garmin, FAO, NOAA, USGS",
    name="Obsidian Black (Esri Official)",
    max_zoom=16,
    control=True,
    show=True,
    class_name="obsidian-base-tiles",
).add_to(m)

folium.TileLayer(
    tiles="https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_Black_Marble/default/2016-01-01/GoogleMapsCompatible_Level8/{z}/{y}/{x}.png",
    attr="NASA Earthdata GIBS · VIIRS Black Marble",
    name="Earth at Night (NASA GIBS Official)",
    max_native_zoom=8,
    max_zoom=16,
    control=True,
    show=False,
).add_to(m)

folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri, Maxar, Earthstar Geographics, USDA, USGS",
    name="Satellite Imagery (Esri/USGS Official)",
    max_zoom=18,
    control=True,
    show=False,
).add_to(m)

# Crisp geographic boundaries & country labels overlay
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}",
    attr="Esri",
    name="Geographic Labels",
    overlay=True,
    control=False,
    show=True,
    opacity=0.92,
).add_to(m)


import json

folium.LayerControl(position="topright", collapsed=True).add_to(m)

# Render historical events first so Critical & Active markers sit cleanly on top
state_rank = {"Low": 0, "Moderate": 1, "High": 2, "Critical": 3}
plot_df = (
    df.head(MAX_MAP_MARKERS)
    .assign(_sr=df["level"].map(state_rank).fillna(1))
    .sort_values(["active", "_sr"], ascending=[True, True])
)

records = [
    [
        round(float(r.lat), 4),
        round(float(r.lon), 4),
        str(r.type),
        str(r.level),
        1 if r.active else 0,
        str(r.title),
        str(r.country),
        str(r.continent),
        r.date.strftime("%Y-%m-%d %H:%M"),
        str(r.measure),
        str(r.source),
        str(r.url or ""),
        list(r.extra.items())[:8] if r.extra else [],
    ]
    for r in plot_df.itertuples()
]

map_var = m.get_name()
data_json = json.dumps(records).replace("</", "<\\/")
marker_script = f"""
<script>
(function() {{
  const COLORS = {json.dumps(MAP_COLORS)};
  const SCOLORS = {json.dumps(LEVEL_COLORS)};
  const RAD = {json.dumps(RADIUS)};
  const DATA = {data_json};
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));

  function mount() {{
    const map = window[{json.dumps(map_var)}];
    if (!map) {{ setTimeout(mount, 25); return; }}
    const renderer = L.canvas({{ padding: 0.5 }});
    for (let i = 0; i < DATA.length; i++) {{
      const [lat, lon, typ, lvl, act, title, country, cont, dt, meas, src, url, extra] = DATA[i];
      const clr = COLORS[typ] || "#94A3B8";
      const sclr = SCOLORS[lvl] || "#64748B";
      const marker = L.circleMarker([lat, lon], {{
        renderer,
        radius: RAD[lvl] || 6,
        color: act ? "#FFFFFF" : clr,
        weight: act ? 1.8 : 1.0,
        fill: true,
        fillColor: clr,
        fillOpacity: act ? 0.92 : 0.58
      }}).addTo(map);
      marker.bindTooltip(esc(typ + " (" + lvl + ") · " + title), {{ sticky: true }});
      marker.on("click", function() {{
        if (!marker.getPopup()) {{
          const badge = act
            ? "<span style='background:#16A34A;color:#fff;padding:1px 7px;border-radius:999px;font-size:10px;font-weight:700;margin-left:6px'>ACTIVE</span>"
            : "<span style='background:#334155;color:#CBD5E1;padding:1px 7px;border-radius:999px;font-size:10px;font-weight:600;margin-left:6px'>HISTORICAL</span>";
          const ex = extra.map(([k, v]) => "<tr><td class='k'>" + esc(k) + "</td><td>" + esc(v) + "</td></tr>").join("");
          const lnk = url ? "<a class='rep-link' href='" + esc(url) + "' target='_blank' rel='noopener'>Open official event report ↗</a>" : "";
          const html = "<div class='dm-pop'>"
            + "<div class='dm-pop-top'><span style='color:" + clr + ";font-weight:800'>" + esc(typ) + "</span>" + badge + "</div>"
            + "<div class='dm-pop-title'>" + esc(title) + "</div>"
            + "<table class='dm-pop-tbl'>"
            + "<tr><td class='k'>Location</td><td>" + esc(country) + " · " + esc(cont) + "</td></tr>"
            + "<tr><td class='k'>Coords</td><td class='mono'>" + lat.toFixed(3) + ", " + lon.toFixed(3) + "</td></tr>"
            + "<tr><td class='k'>Date</td><td class='mono'>" + esc(dt) + " UTC</td></tr>"
            + "<tr><td class='k'>State</td><td><span class='st-pill' style='background:" + sclr + "'>" + esc(lvl) + "</span></td></tr>"
            + "<tr><td class='k'>Measure</td><td>" + esc(meas) + "</td></tr>"
            + "<tr><td class='k'>Source</td><td>" + esc(src) + "</td></tr>"
            + ex + "</table>" + lnk + "</div>";
          marker.bindPopup(html, {{ maxWidth: 340 }}).openPopup();
        }}
      }});
    }}
  }}
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount);
  else mount();
}})();
</script>
"""
m.get_root().html.add_child(folium.Element(marker_script))

legend_cats = "".join(
    f"<div class='lg-item{' lg-dim' if c not in present else ''}'>"
    f"<span class='lg-dot' style='background:{MAP_COLORS[c]}'></span>{c}</div>"
    for c in CATEGORIES
)
legend_states = "".join(
    f"<span class='lg-st' style='background:{LEVEL_COLORS[l]}'>{l}</span>"
    for l in LEVELS
)

map_css_and_legend = f"""
<style>
html, body {{ margin: 0; padding: 0; background: #05070B; }}
.leaflet-container {{
    background: #05070B !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}
.obsidian-base-tiles {{
    filter: brightness(0.54) contrast(1.34) saturate(0.82);
}}
.leaflet-control-zoom a, .leaflet-control-layers {{
    background: rgba(10, 14, 23, 0.92) !important;
    color: #F8FAFC !important;
    border: 1px solid rgba(148, 163, 184, 0.24) !important;
    backdrop-filter: blur(8px);
}}
.leaflet-control-zoom a:hover {{
    background: #1E293B !important;
    color: #FFFFFF !important;
}}
.leaflet-control-layers-expanded {{
    padding: 8px 12px !important;
    border-radius: 10px !important;
    color: #E2E8F0 !important;
    font-size: 12px !important;
}}
.leaflet-control-attribution {{
    background: rgba(5, 7, 11, 0.78) !important;
    color: #94A3B8 !important;
    font-size: 10px !important;
}}
.leaflet-control-attribution a {{ color: #CBD5E1 !important; }}
.leaflet-popup-content-wrapper, .leaflet-popup-tip {{
    background: #0B1120 !important;
    color: #F1F5F9 !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.65) !important;
}}
.leaflet-popup-close-button {{ color: #94A3B8 !important; }}
.leaflet-tooltip {{
    background: rgba(11, 17, 32, 0.95) !important;
    color: #F8FAFC !important;
    border: 1px solid #334155 !important;
    border-radius: 6px !important;
    font-size: 11.5px !important;
    padding: 4px 8px !important;
}}
.dm-pop {{ min-width: 245px; font-size: 12px; line-height: 1.45; }}
.dm-pop-top {{ font-size: 11.5px; letter-spacing: 0.04em; text-transform: uppercase; margin-bottom: 4px; }}
.dm-pop-title {{ font-weight: 700; font-size: 13.5px; color: #FFFFFF; margin-bottom: 8px; }}
.dm-pop-tbl {{ width: 100%; border-collapse: collapse; }}
.dm-pop-tbl td {{ padding: 2.5px 0; color: #E2E8F0; vertical-align: top; }}
.dm-pop-tbl td.k {{ color: #94A3B8; width: 72px; font-weight: 500; padding-right: 8px; }}
.dm-pop-tbl td.mono {{ font-family: monospace; font-size: 11.5px; }}
.st-pill {{ display: inline-block; padding: 1px 8px; border-radius: 999px; color: #fff; font-weight: 700; font-size: 10.5px; }}
.rep-link {{ display: inline-block; margin-top: 8px; color: #60A5FA !important; font-weight: 600; text-decoration: none; font-size: 11.5px; }}
.rep-link:hover {{ text-decoration: underline; }}

.dm-legend {{
    position: fixed;
    bottom: 22px;
    left: 14px;
    z-index: 9999;
    background: rgba(8, 12, 20, 0.90);
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 10px;
    padding: 11px 13px;
    color: #F1F5F9;
    font-family: 'Inter', system-ui, sans-serif;
    font-size: 11.5px;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.55);
    max-width: 250px;
}}
.lg-hdr {{
    font-size: 9.5px;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #94A3B8;
    margin-bottom: 6px;
}}
.lg-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4px 12px;
}}
.lg-item {{ display: flex; align-items: center; gap: 6px; font-weight: 500; color: #F1F5F9; }}
.lg-dim {{ opacity: 0.35; }}
.lg-dot {{ width: 9px; height: 9px; border-radius: 50%; display: inline-block; flex-shrink: 0; }}
.lg-div {{ border-top: 1px solid rgba(148, 163, 184, 0.2); margin: 8px 0 6px; }}
.lg-states {{ display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 5px; }}
.lg-st {{ padding: 1.5px 7px; border-radius: 999px; font-size: 10px; font-weight: 700; color: #FFFFFF; }}
.lg-note {{ font-size: 10.5px; color: #94A3B8; line-height: 1.35; }}
</style>
<div class="dm-legend">
  <div class="lg-hdr">Disaster Category</div>
  <div class="lg-grid">{legend_cats}</div>
  <div class="lg-div"></div>
  <div class="lg-hdr">Disaster State</div>
  <div class="lg-states">{legend_states}</div>
  <div class="lg-note">Marker radius scales by state · White ring = Active event</div>
</div>
"""
m.get_root().html.add_child(folium.Element(map_css_and_legend))

components.html(m.get_root().render(), height=640)
if len(df) > MAX_MAP_MARKERS:
    st.caption(f"Displaying the {MAX_MAP_MARKERS:,} most recent records on the map. Narrow your date or location filter to inspect older events.")
