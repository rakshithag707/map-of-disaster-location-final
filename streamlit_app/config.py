"""Application configuration.

To load a different CSV dataset, change ONLY the single line below:
    CSV_PATH = "data/disaster_data.csv"
"""

CSV_PATH = "data/disaster_data.csv"

# ---------------------------------------------------------------------------
# Automatic CSV column recognition (case-insensitive).
# Any additional columns in your CSV are preserved and shown in event details.
# ---------------------------------------------------------------------------
CSV_COLUMN_ALIASES = {
    "id": ["id", "event_id", "uid", "record_id"],
    "lat": ["latitude", "lat", "y", "coord_lat"],
    "lon": ["longitude", "lon", "lng", "long", "x", "coord_lon"],
    "date": ["date", "date_utc", "time", "datetime", "start_date", "event_date", "timestamp"],
    "end_date": ["end_date", "end_date_utc", "enddate", "to_date", "closed"],
    "type": ["type", "disaster_type", "category", "event_type", "hazard"],
    "title": ["title", "name", "event", "event_name", "description", "location"],
    "country": ["country", "nation", "country_name", "area"],
    "continent": ["continent", "region", "world_region"],
    "severity": ["state", "severity", "level", "alert", "alert_level", "status_level", "risk"],
    "measure": ["measure", "measurement", "details", "summary", "severity_text"],
    "magnitude": ["magnitude", "mag", "intensity", "value", "score"],
    "active": ["active", "status", "is_active", "current", "ongoing"],
    "source": ["source", "provider", "agency", "origin"],
    "url": ["url", "link", "report_url", "source_url"],
}

MAX_MAP_MARKERS = 4000
