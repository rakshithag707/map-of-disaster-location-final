"""Build the clean global disaster CSV dataset from official USGS, GDACS, and NASA EONET feeds.

Uses Python standard library only. Saves the resulting CSV to:
  - streamlit_app/data/disaster_data.csv
  - disaster_data.csv
  - public/disaster_data.csv

Usage:
    python3 export_data.py
    python3 export_data.py 2025-11-18 2026-11-18
"""
import csv
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone

FIELDS = [
    "id", "type", "title", "country", "continent", "latitude", "longitude",
    "date", "end_date", "state", "measure", "magnitude", "active", "source", "url",
]

US_STATES = {
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut",
    "delaware", "florida", "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa",
    "kansas", "kentucky", "louisiana", "maine", "maryland", "massachusetts", "michigan",
    "minnesota", "mississippi", "missouri", "montana", "nebraska", "nevada", "new hampshire",
    "new jersey", "new mexico", "new york", "north carolina", "north dakota", "ohio",
    "oklahoma", "oregon", "pennsylvania", "rhode island", "south carolina", "south dakota",
    "tennessee", "texas", "utah", "vermont", "virginia", "washington", "west virginia",
    "wisconsin", "wyoming", "puerto rico", "u.s. virgin islands", "guam",
    "northern mariana islands", "ca", "nv", "or", "wa", "id", "mt", "az", "nm", "tx", "fl", "ak", "hi",
}

CA_PROVINCES = {
    "alberta", "british columbia", "manitoba", "new brunswick", "newfoundland and labrador",
    "northwest territories", "nova scotia", "nunavut", "ontario", "prince edward island",
    "quebec", "saskatchewan", "yukon",
}

AU_STATES = {
    "new south wales", "queensland", "south australia", "tasmania", "victoria",
    "western australia", "northern territory",
}

COUNTRY_ALIASES = {
    "russian federation": "Russia",
    "russia region": "Russia",
    "kuril islands": "Russia",
    "kamchatka": "Russia",
    "the fiji islands": "Fiji",
    "fiji region": "Fiji",
    "south of the fiji islands": "Fiji",
    "the kermadec islands": "New Zealand",
    "kermadec islands region": "New Zealand",
    "kermadec islands": "New Zealand",
    "the democratic republic of congo": "DR Congo",
    "democratic republic of the congo": "DR Congo",
    "congo, the democratic republic of the": "DR Congo",
    "united states of america": "United States",
    "usa": "United States",
    "u.s.": "United States",
    "viet nam": "Vietnam",
    "iran (islamic republic of)": "Iran",
    "bolivia (plurinational state of)": "Bolivia",
    "venezuela (bolivarian republic of)": "Venezuela",
    "tanzania, united republic of": "Tanzania",
    "korea, republic of": "South Korea",
    "syrian arab republic": "Syria",
    "lao people's democratic republic": "Laos",
    "turkiye": "Turkey",
    "türkiye": "Turkey",
    "philippine islands region": "Philippines",
    "mindanao": "Philippines",
    "luzon": "Philippines",
    "taiwan region": "Taiwan",
    "japan region": "Japan",
    "bonin islands": "Japan",
    "izu islands": "Japan",
    "ryukyu islands": "Japan",
    "indonesia region": "Indonesia",
    "tonga region": "Tonga",
    "vanuatu region": "Vanuatu",
    "solomon islands": "Solomon Islands",
    "santa cruz islands": "Solomon Islands",
    "papua new guinea": "Papua New Guinea",
    "new britain region": "Papua New Guinea",
    "chile": "Chile",
    "off the coast of central chile": "Chile",
    "peru": "Peru",
    "near the coast of central peru": "Peru",
    "mexico": "Mexico",
    "off the coast of chiapas": "Mexico",
}

# Approximate country bounding boxes used only when the source record omits a country name.
COUNTRY_BOXES = [
    ("United States", 24.4, 49.4, -125.0, -66.9),
    ("United States", 51.2, 71.5, -168.0, -130.0),
    ("United States", 18.8, 22.4, -160.5, -154.7),
    ("Canada", 49.0, 83.0, -141.0, -52.5),
    ("Mexico", 14.5, 32.5, -117.2, -86.7),
    ("Brazil", -33.8, 5.3, -74.0, -34.7),
    ("Argentina", -55.1, -21.8, -73.6, -53.6),
    ("Chile", -56.0, -17.5, -76.0, -66.5),
    ("Colombia", -4.2, 12.5, -79.0, -66.9),
    ("Peru", -18.4, -0.1, -81.4, -68.7),
    ("Bolivia", -22.9, -9.7, -69.6, -57.5),
    ("Australia", -43.7, -10.5, 112.9, 153.7),
    ("New Zealand", -47.5, -34.0, 166.0, 179.0),
    ("Indonesia", -11.0, 6.0, 95.0, 141.0),
    ("Philippines", 4.6, 21.1, 116.9, 126.6),
    ("Japan", 24.0, 45.6, 122.9, 146.0),
    ("China", 18.2, 53.5, 73.6, 134.8),
    ("India", 6.7, 35.5, 68.1, 97.4),
    ("Russia", 41.2, 81.9, 27.0, 180.0),
    ("Turkey", 35.8, 42.1, 26.0, 44.8),
    ("Greece", 34.8, 41.8, 19.3, 28.3),
    ("Italy", 36.6, 47.1, 6.6, 18.6),
    ("Spain", 36.0, 43.8, -9.3, 3.3),
    ("Portugal", 36.9, 42.2, -9.5, -6.2),
    ("France", 42.3, 51.1, -4.8, 8.2),
    ("Algeria", 19.0, 37.1, -8.7, 12.0),
    ("Angola", -18.0, -4.4, 11.7, 24.1),
    ("Zambia", -18.1, -8.2, 22.0, 33.7),
    ("Mozambique", -26.9, -10.5, 30.2, 40.9),
    ("DR Congo", -13.5, 5.4, 12.2, 31.3),
    ("South Africa", -34.9, -22.1, 16.4, 32.9),
    ("Madagascar", -25.6, -11.9, 43.2, 50.5),
]


def continent_of(lat: float, lon: float) -> str:
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


def infer_country(raw: str, lat: float, lon: float) -> str:
    c = (raw or "").strip().strip(",")
    if ";" in c:
        c = c.split(";")[0].strip()
    low = c.lower()
    if low in US_STATES:
        return "United States"
    if low in CA_PROVINCES:
        return "Canada"
    if low in AU_STATES:
        return "Australia"
    if low in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[low]
    for k, v in COUNTRY_ALIASES.items():
        if len(k) > 5 and k in low:
            return v
    if c and low not in {"unknown", "none", "n/a", "-"} and not any(
        w in low for w in ["ridge", "rise", "trench", "ocean", "sea", "fire", "rx ", "prescribed", "wildfire", "complex"]
    ) and len(c) <= 36:
        return c
    for name, la0, la1, lo0, lo1 in COUNTRY_BOXES:
        if la0 <= lat <= la1 and lo0 <= lon <= lo1:
            return name
    return "International Waters"


def get(url: str, params: dict) -> dict:
    req = urllib.request.Request(
        url + "?" + urllib.parse.urlencode(params),
        headers={"User-Agent": "disaster-dataset-builder/1.0"},
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def eq_state(mag: float) -> str:
    return "Critical" if mag >= 7.0 else "High" if mag >= 6.0 else "Moderate" if mag >= 5.0 else "Low"


def usgs_earthquakes(start: date, end: date) -> list[dict]:
    rows, now, cur = [], datetime.now(timezone.utc), start
    while cur <= end:
        stop = min(cur + timedelta(days=30), end)
        j = get("https://earthquake.usgs.gov/fdsnws/event/1/query", {
            "format": "geojson", "starttime": cur.isoformat(), "endtime": f"{stop.isoformat()}T23:59:59",
            "minmagnitude": 4.5, "orderby": "time", "limit": 20000,
        })
        for f in j.get("features", []):
            p, g = f["properties"], f["geometry"]["coordinates"]
            if g[0] is None or g[1] is None or p.get("time") is None:
                continue
            mag = round(float(p.get("mag") or 0.0), 1)
            place = p.get("place") or "Unknown location"
            raw_country = place.split(",")[-1].strip() if "," in place else place.split(" of ")[-1].strip()
            lat, lon = round(float(g[1]), 4), round(float(g[0]), 4)
            t = datetime.fromtimestamp(p["time"] / 1000, tz=timezone.utc)
            rows.append({
                "id": f"usgs-{f['id']}",
                "type": "Earthquake",
                "title": p.get("title") or place,
                "country": infer_country(raw_country, lat, lon),
                "continent": continent_of(lat, lon),
                "latitude": lat,
                "longitude": lon,
                "date": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end_date": "",
                "state": eq_state(mag),
                "measure": f"Magnitude {mag:.1f} {p.get('magType') or ''}, depth {(g[2] or 0):.1f} km"
                           + (", tsunami warning" if p.get("tsunami") else ""),
                "magnitude": mag,
                "active": "Active" if (now - t) < timedelta(hours=72) else "Historical",
                "source": "USGS",
                "url": p.get("url") or "",
            })
        cur = stop + timedelta(days=1)
    return rows


def usgs_landslides(start: date, end: date) -> list[dict]:
    j = get("https://earthquake.usgs.gov/fdsnws/event/1/query", {
        "format": "geojson", "eventtype": "landslide",
        "starttime": (start - timedelta(days=365)).isoformat(), "endtime": f"{end.isoformat()}T23:59:59",
        "orderby": "time", "limit": 500,
    })
    now = datetime.now(timezone.utc)
    rows = []
    for f in j.get("features", []):
        p, g = f["properties"], f["geometry"]["coordinates"]
        if g[0] is None or g[1] is None or p.get("time") is None:
            continue
        mag = round(float(p.get("mag") or 0.0), 1)
        place = p.get("place") or "Landslide event"
        raw_country = place.split(",")[-1].strip() if "," in place else place.split(" of ")[-1].strip()
        lat, lon = round(float(g[1]), 4), round(float(g[0]), 4)
        t = datetime.fromtimestamp(p["time"] / 1000, tz=timezone.utc)
        state = "Critical" if mag >= 4.0 else "High" if mag >= 3.0 else "Moderate" if mag >= 2.0 else "Low"
        rows.append({
            "id": f"usgs-ls-{f['id']}",
            "type": "Landslide",
            "title": p.get("title") or f"Landslide - {place}",
            "country": infer_country(raw_country, lat, lon),
            "continent": continent_of(lat, lon),
            "latitude": lat,
            "longitude": lon,
            "date": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end_date": "",
            "state": state,
            "measure": f"Seismic eq. M{mag:.1f}, depth {(g[2] or 0):.1f} km",
            "magnitude": mag,
            "active": "Active" if (now - t) < timedelta(days=7) else "Historical",
            "source": "USGS",
            "url": p.get("url") or "",
        })
    return rows


GDACS_TYPES = {"FL": "Flood", "TC": "Storm", "VO": "Volcano", "DR": "Drought", "WF": "Wildfire"}


def gdacs_events(start: date, end: date) -> list[dict]:
    feats, ids = [], set()
    for page in range(1, 40):
        j = get("https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH", {
            "eventlist": "FL;TC;VO;DR;WF", "fromDate": start.isoformat(), "toDate": end.isoformat(),
            "alertlevel": "green;orange;red", "pageNumber": page,
        })
        pf = j.get("features", [])
        new = [f for f in pf if (f["properties"].get("eventtype"), f["properties"].get("eventid")) not in ids]
        if not new:
            break
        ids.update((f["properties"].get("eventtype"), f["properties"].get("eventid")) for f in new)
        feats += new
        if len(pf) < 100:
            break
    rows = []
    for f in feats:
        p, geo = f["properties"], f.get("geometry") or {}
        if geo.get("type") != "Point":
            continue
        lon, lat = round(float(geo["coordinates"][0]), 4), round(float(geo["coordinates"][1]), 4)
        sd = p.get("severitydata") or {}
        sev = sd.get("severity")
        alert = str(p.get("alertlevel") or "Green").capitalize()
        score = float(p.get("alertscore") or 0)
        if p.get("eventtype") == "TC" and isinstance(sev, (int, float)):
            state = "Critical" if sev >= 178 else "High" if sev >= 119 else "Moderate" if sev >= 63 else "Low"
        elif alert == "Red":
            state = "Critical"
        elif alert == "Orange":
            state = "High"
        elif score >= 0.6 or (isinstance(sev, (int, float)) and sev >= 5000):
            state = "Moderate"
        else:
            state = "Low"
        dtype = GDACS_TYPES.get(p.get("eventtype"), "Other")
        rows.append({
            "id": f"gdacs-{p.get('eventtype')}-{p.get('eventid')}",
            "type": dtype,
            "title": (p.get("name") or f"{dtype} event").strip(),
            "country": infer_country(p.get("country") or "", lat, lon),
            "continent": continent_of(lat, lon),
            "latitude": lat,
            "longitude": lon,
            "date": p.get("fromdate") or "",
            "end_date": p.get("todate") or "",
            "state": state,
            "measure": f"{sd.get('severitytext') or dtype} (GDACS {alert})",
            "magnitude": round(float(sev), 2) if isinstance(sev, (int, float)) else "",
            "active": "Active" if str(p.get("iscurrent")).lower() == "true" else "Historical",
            "source": "GDACS",
            "url": (p.get("url") or {}).get("report", ""),
        })
    return rows


EONET_TYPES = {
    "wildfires": "Wildfire",
    "severeStorms": "Storm",
    "volcanoes": "Volcano",
    "floods": "Flood",
    "landslides": "Landslide",
    "drought": "Drought",
}


def _parse_eonet(events: list[dict]) -> list[dict]:
    rows = []
    for e in events:
        cat = EONET_TYPES.get((e.get("categories") or [{}])[0].get("id"))
        pts = [g for g in e.get("geometry", []) if g.get("type") == "Point"]
        if not cat or not pts:
            continue
        last = pts[-1]
        lon, lat = round(float(last["coordinates"][0]), 4), round(float(last["coordinates"][1]), 4)
        mv, unit = last.get("magnitudeValue"), last.get("magnitudeUnit")
        if mv is not None and unit == "kts":
            state = "Critical" if mv >= 96 else "High" if mv >= 64 else "Moderate" if mv >= 34 else "Low"
        elif mv is not None and unit == "acres":
            state = "Critical" if mv >= 100000 else "High" if mv >= 20000 else "Moderate" if mv >= 2500 else "Low"
        elif len(pts) >= 12:
            state = "High"
        elif len(pts) >= 4:
            state = "Moderate"
        else:
            state = "Low"
        title = (e.get("title") or cat).strip()
        raw_country = title.split(",")[-1].strip() if "," in title else ""
        rows.append({
            "id": f"eonet-{e['id']}",
            "type": cat,
            "title": title,
            "country": infer_country(raw_country, lat, lon),
            "continent": continent_of(lat, lon),
            "latitude": lat,
            "longitude": lon,
            "date": pts[0].get("date", ""),
            "end_date": e.get("closed") or "",
            "state": state,
            "measure": f"{mv:g} {unit}" if isinstance(mv, (int, float)) else f"Satellite-tracked {cat.lower()}",
            "magnitude": mv if mv is not None else "",
            "active": "Historical" if e.get("closed") else "Active",
            "source": "NASA EONET",
            "url": (e.get("sources") or [{}])[0].get("url", ""),
        })
    return rows


def eonet_events(start: date, end: date) -> list[dict]:
    # Query non-wildfire hazards explicitly first so wildfires never crowd out floods, storms, volcanoes, landslides.
    j_other = get("https://eonet.gsfc.nasa.gov/api/v3/events", {
        "status": "all", "category": "volcanoes,landslides,floods,severeStorms,drought",
        "start": start.isoformat(), "end": end.isoformat(), "limit": 2500,
    })
    j_fire = get("https://eonet.gsfc.nasa.gov/api/v3/events", {
        "status": "all", "category": "wildfires",
        "start": start.isoformat(), "end": end.isoformat(), "limit": 3500,
    })
    return _parse_eonet(j_other.get("events", []) + j_fire.get("events", []))


def main():
    end = date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else date.today()
    start = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else end - timedelta(days=365)
    rows, seen = [], set()
    for name, fn in (
        ("USGS Earthquakes", usgs_earthquakes),
        ("USGS Landslides", usgs_landslides),
        ("GDACS", gdacs_events),
        ("NASA EONET", eonet_events),
    ):
        try:
            got = fn(start, end)
            print(f"{name}: {len(got)} records")
            for r in got:
                if r["id"] not in seen and r["date"]:
                    seen.add(r["id"])
                    rows.append(r)
        except Exception as exc:
            print(f"{name}: failed ({exc})")
    rows.sort(key=lambda r: r["date"], reverse=True)

    here = os.path.dirname(os.path.abspath(__file__))
    targets = [
        os.path.join(here, "data", "disaster_data.csv"),
        os.path.join(here, "..", "disaster_data.csv"),
        os.path.join(here, "..", "public", "disaster_data.csv"),
    ]
    for path in targets:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
        print(f"Saved {len(rows)} rows -> {os.path.normpath(path)}")


if __name__ == "__main__":
    main()
