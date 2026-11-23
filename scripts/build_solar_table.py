"""
# Copyright (c) 2026 Stephen Olumide Akindipe
# SPDX-License-Identifier: MIT

Build data/ny_solar_resource.csv: the PVWatts v8 annual solar resource for every
New York ZIP code in data/us_zip_centroids.csv, with the app's exact parameters.

Run once from the TE3 Build folder, with NREL_API_KEY set in .env:
    python scripts/build_solar_table.py

About 2,154 requests at one every 4 seconds (900 per hour, under the 1,000 per
hour key limit): roughly 2.5 hours. Safe to stop and restart; ZIP codes already
in the output file are skipped. Rerun only when NLR releases a new NSRDB
typical-year dataset.
"""

import csv
import datetime
import os
import sys
import time

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP_TABLE = os.path.join(ROOT, "data", "us_zip_centroids.csv")
OUT = os.path.join(ROOT, "data", "ny_solar_resource.csv")
URL = "https://developer.nlr.gov/api/pvwatts/v8.json"
PAUSE = float(os.getenv("TE3_BUILD_PAUSE", "4"))


def main():
    key = os.getenv("NREL_API_KEY")
    if not key:
        sys.exit("NREL_API_KEY is not set. Add it to .env first.")
    with open(ZIP_TABLE, newline="", encoding="utf-8") as f:
        ny = [r for r in csv.DictReader(f) if r["state_code"].upper() == "NY"]
    done = set()
    new_file = not os.path.exists(OUT)
    if not new_file:
        with open(OUT, newline="", encoding="utf-8") as f:
            done = {r["zip"] for r in csv.DictReader(f)}
    today = datetime.date.today().isoformat()
    todo = [r for r in ny if r["zip"] not in done]
    print(f"{len(ny)} New York ZIP codes; {len(done)} already done; {len(todo)} to fetch.")
    with open(OUT, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["zip", "lat", "lon", "solrad_annual", "retrieved", "source"])
        for n, r in enumerate(todo, 1):
            params = {"api_key": key, "lat": r["lat"], "lon": r["lon"], "system_capacity": 4,
                      "azimuth": 180, "tilt": 20, "array_type": 1, "module_type": 0, "losses": 14}
            for attempt in range(3):
                try:
                    res = requests.get(URL, params=params, timeout=20)
                except requests.RequestException as e:
                    print(f"{r['zip']}: network error ({type(e).__name__}); retrying")
                    time.sleep(30)
                    continue
                if res.status_code == 429:
                    print("Hourly limit reached; waiting 10 minutes")
                    time.sleep(600)
                    continue
                break
            else:
                print(f"{r['zip']}: skipped after 3 attempts; rerun later")
                continue
            if res.status_code != 200:
                print(f"{r['zip']}: HTTP {res.status_code}; skipped")
                time.sleep(PAUSE)
                continue
            value = (res.json().get("outputs") or {}).get("solrad_annual")
            if value is None:
                print(f"{r['zip']}: no value returned; skipped")
            else:
                w.writerow([r["zip"], r["lat"], r["lon"], value, today, "PVWatts v8 (NSRDB typical year)"])
                f.flush()
            if n % 50 == 0:
                print(f"{n} of {len(todo)} done")
            time.sleep(PAUSE)
    print(f"Finished. Output: {OUT}")


if __name__ == "__main__":
    main()
