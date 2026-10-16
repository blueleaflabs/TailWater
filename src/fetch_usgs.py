#!/usr/bin/env python3
"""TailWater: download 15-min USGS continuous records for the Pacheco Creek gauges.
    python3 src/fetch_usgs.py          (from the repository root, or anywhere)
Writes data/<site>.csv with columns time_utc, parameter_code, value, approval, qualifiers.
Resumable: progress is kept in data/<site>.csv.next; finished sites are skipped.
Note: the frozen data/ shipped with the repository were retrieved 15 Oct 2026; re-running
may return revised values if USGS re-approves or edits a record."""
import sys, os, pathlib; ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'src')); os.chdir(ROOT)  # run from any cwd
import csv, json, os, sys, time, urllib.request, urllib.parse

BASE = "https://api.waterdata.usgs.gov/ogcapi/v0/collections/continuous/items"
PARAMS = "00300,00010,00060,00095"   # DO, water temp, discharge, specific conductance
SITES = {
    # Santa Clara County — Pacheco Creek cluster + Arroyo Hondo (full records)
    "USGS-11152850": ("2024-01-01", "2026-01-01"),  # NF Pacheco ABOVE reservoir (unregulated)
    "USGS-11152870": ("2024-01-01", "2026-01-01"),  # NF Pacheco BELOW reservoir (regulated)
    "USGS-11152880": ("2024-01-01", "2026-01-01"),  # SF Pacheco abv Hwy 152
    "USGS-11152900": ("2024-01-01", "2026-01-01"),  # Cedar Creek
    "USGS-11152890": ("2024-01-01", "2026-01-01"),  # Pacheco at Bell Station
    "USGS-11153000": ("2024-01-01", "2026-01-01"),  # Pacheco nr Dunneville (downstream)
    "USGS-11173200": ("2021-01-01", "2023-07-01"),  # Arroyo Hondo nr San Jose (part A; API caps a query at 1100 days)
    "USGS-11173200_B": ("2023-07-01", "2026-01-01"),  # Arroyo Hondo part B
}

def get(url, tries=5):
    req = urllib.request.Request(url, headers={"User-Agent": "TailWater/1.0 (student research)"})
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except Exception as e:
            wait = 5 * (i + 1)
            print(f"   retry {i+1}/{tries} after error: {e} (sleep {wait}s)")
            time.sleep(wait)
    raise SystemExit("giving up on " + url)

os.makedirs("data", exist_ok=True)
for site, (t0, t1) in SITES.items():
    out = f"data/{site}.csv"
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        print(f"skip {site} (exists)"); continue
    q = {"f": "json", "skipGeometry": "true", "monitoring_location_id": site.split("_")[0],
         "parameter_code": PARAMS, "time": f"{t0}T00:00:00Z/{t1}T00:00:00Z", "limit": "50000",
         "properties": "time,parameter_code,value,approval_status,qualifier"}
    url = BASE + "?" + urllib.parse.urlencode(q, safe=",:/")
    nxt = out + ".next"
    resume = os.path.exists(nxt) and open(nxt).read().strip()
    mode = "a" if resume else "w"
    if resume: url = resume
    n = 0; page = 0
    with open(out + ".part", mode, newline="") as fh:
        w = csv.writer(fh)
        if mode == "w": w.writerow(["time_utc", "parameter_code", "value", "approval", "qualifiers"])
        while url:
            page += 1
            d = get(url)
            feats = d.get("features", [])
            for f in feats:
                p = f["properties"]
                w.writerow([p.get("time"), p.get("parameter_code"), p.get("value"),
                            p.get("approval_status"), json.dumps(p.get("qualifier")) if p.get("qualifier") else ""])
            fh.flush()
            n += len(feats)
            print(f"{site} page {page}: {len(feats)} rows (+{n})", flush=True)
            url = next((l["href"] for l in d.get("links", []) if l.get("rel") == "next"), None)
            if url and feats:
                open(nxt, "w").write(url)
            else:
                url = None
    if os.path.exists(nxt): open(nxt, "w").write("")
    os.replace(out + ".part", out)
    print(f"done {site} -> {out}", flush=True)
print("ALL DONE")
