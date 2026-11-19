"""
TE3 Engine: resilience settings

get_with_retry  Retries an HTTP GET after a connection error or a temporary
                server answer (429 too many requests, 500, 502, 503, 504),
                waiting 1, then 2 seconds (Retry-After is respected up to 5 s).
                Other answers, such as 403 or 404, are returned at once.
lookup_solrad   Reads the annual average daily solar resource for a ZIP from
                data/ny_solar_resource.csv when that file exists (built once by
                scripts/build_solar_table.py). Returns None when the file or the
                ZIP is absent, so the app falls back to the live PVWatts call.

Configuration (environment variables, used by the tests)
    TE3_RETRY_BASE_DELAY  Seconds before the first retry (default 1).
    TE3_SOLAR_TABLE       Path to the solar table; empty string turns it off.
"""

import csv
import os
import time

import requests

RETRY_STATUSES = {429, 500, 502, 503, 504}
MAX_RETRY_AFTER = 5.0

_HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SOLAR_TABLE = os.path.join(_HERE, "data", "ny_solar_resource.csv")
_SOLAR = {}


def _base_delay():
    try:
        return max(0.0, float(os.getenv("TE3_RETRY_BASE_DELAY", "1")))
    except ValueError:
        return 1.0


def get_with_retry(url, attempts=3, **kwargs):
    """requests.get with retries. Returns the last response, or raises the last
    requests.RequestException if no attempt reached the server."""
    response, error = None, None
    for i in range(attempts):
        try:
            response, error = requests.get(url, **kwargs), None
        except requests.RequestException as e:
            response, error = None, e
        if response is not None and response.status_code not in RETRY_STATUSES:
            return response
        if i < attempts - 1:
            delay = _base_delay() * (2 ** i)
            headers = getattr(response, "headers", None) or {}
            retry_after = headers.get("Retry-After") if hasattr(headers, "get") else None
            if retry_after:
                try:
                    delay = min(max(delay, float(retry_after)), MAX_RETRY_AFTER)
                except ValueError:
                    pass
            if delay:
                time.sleep(delay)
    if response is not None:
        return response
    raise error


def solar_table_path():
    return os.getenv("TE3_SOLAR_TABLE", DEFAULT_SOLAR_TABLE)


def lookup_solrad(zipcode, path=None):
    """Annual average daily solar resource (kWh/m2/day) for a ZIP, or None."""
    path = solar_table_path() if path is None else path
    if not path or not os.path.exists(path):
        return None
    if path not in _SOLAR:
        table = {}
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    table[str(row["zip"]).strip().zfill(5)] = float(row["solrad_annual"])
                except (KeyError, TypeError, ValueError):
                    continue
        _SOLAR[path] = table
    return _SOLAR[path].get(str(zipcode).strip().zfill(5))
