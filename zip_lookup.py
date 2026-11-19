"""
TE3 Engine: ZIP code lookup (Offline mode)

Resolves a 5-digit ZIP code to coordinates, place name and state from a file deployed with the app. 
This ensures that a run does not depend on a public geocoding service.
As built, the app calls this service first and uses Nominatim only for a ZIP not in the file.

Data
    data/us_zip_centroids.csv  (columns: zip, place, state, state_code, lat, lon)
    Built from the GeoNames postal code file for the United States
    (https://download.geonames.org/export/zip/US.zip), retrieved 2026-11-18,
    41,488 unique ZIP codes. Licensed under Creative Commons Attribution 4.0
    (https://creativecommons.org/licenses/by/4.0/); attribution is required.
    Coordinates are approximate ZIP centroids, adequate for selecting the
    NSRDB solar resource cell.

Configuration
    TE3_ZIP_TABLE  Optional environment variable with another path to the file.
                   Set it to an empty string to turn the local lookup off
                   (the test suite does this to exercise the Nominatim path).
"""

import csv
import os

ZIP_SOURCE = "GeoNames postal code data (CC BY 4.0), retrieved 2026-11-18"

_HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ZIP_TABLE = os.path.join(_HERE, "data", "us_zip_centroids.csv")

_TABLES = {}


def zip_table_path():
    return os.getenv("TE3_ZIP_TABLE", DEFAULT_ZIP_TABLE)


def _load(path):
    table = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            z = str(row.get("zip", "")).strip().zfill(5)
            if z and z not in table:  # first row wins where a ZIP appears twice
                table[z] = row
    return table


def lookup_zip(zipcode, path=None):
    """Return a location dict in the same shape as the app's geocoder, or None
    when the file is absent or the ZIP is not in it."""
    path = zip_table_path() if path is None else path
    if not path or not os.path.exists(path):
        return None
    if path not in _TABLES:
        _TABLES[path] = _load(path)
    row = _TABLES[path].get(str(zipcode).strip().zfill(5))
    if not row:
        return None
    try:
        lat, lon = float(row["lat"]), float(row["lon"])
    except (KeyError, TypeError, ValueError):
        return None
    place = (row.get("place") or "").strip() or f"Region {zipcode}"
    state = (row.get("state") or "").strip()
    code = (row.get("state_code") or "").strip().upper()
    return {
        "lat": lat,
        "lon": lon,
        "display_name": f"{place}, {state}".strip(", "),
        "state": state,
        "state_code": f"US-{code}" if code else "",
        "source": "local",
    }
