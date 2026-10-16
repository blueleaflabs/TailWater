# data/ — frozen USGS records

All files were retrieved on **15 October 2026** from the USGS Water Data for the Nation API,
continuous collection (`https://api.waterdata.usgs.gov/ogcapi/v0/collections/continuous/items`),
by `src/fetch_usgs.py`. They are the exact inputs behind every number in `analysis/AUDIT.md` and
the papers. Do not edit them; re-download to a different folder if you want fresh data.

## Files

| File | Site | Record requested | Notes |
|---|---|---|---|
| `USGS-11152850.csv` | NF Pacheco Creek above Pacheco Reservoir | 2024-01-01 → 2026-01-01 | DO, temperature |
| `USGS-11152870.csv` | NF Pacheco Creek below Pacheco Reservoir | 2024-01-01 → 2026-01-01 | DO, temperature. Values end 2025-10-01 08:00 UTC; rows after that are placeholders (see below) |
| `USGS-11152880.csv` | SF Pacheco Creek above Hwy 152 | 2024-01-01 → 2026-01-01 | DO, temperature |
| `USGS-11152890.csv` | Pacheco Creek at Bell Station | 2024-01-01 → 2026-01-01 | DO, temperature |
| `USGS-11152900.csv` | Cedar Creek | 2024-01-01 → 2026-01-01 | DO, temperature, discharge |
| `USGS-11153000.csv` | Pacheco Creek near Dunneville (Walnut Ave) | 2024-01-01 → 2026-01-01 | DO, temperature, discharge |
| `USGS-11173200.csv`, `USGS-11173200_B.csv` | Arroyo Hondo near San José | 2021-01-01 → 2023-07-01, 2023-07-01 → 2026-01-01 | split in two because the API caps one request at 1,100 days; `metrics.load()` concatenates them |
| `meta/scc_do_meta.json` | — | — | USGS time-series metadata for the Santa Clara County continuous-DO sites (locations, drainage areas, altitudes) used to identify and describe the gauges |

## Columns

```
time_utc        ISO-8601 timestamp in UTC (the scripts convert to PST, UTC−8, no daylight saving)
parameter_code  USGS code: 00300 dissolved oxygen (mg/L), 00010 water temperature (°C),
                00060 discharge (ft³/s), 00095 specific conductance (µS/cm at 25 °C)
value           the reading; empty when USGS published a timestamp with no value
approval        "Approved" or "Provisional" (USGS review status at retrieval)
qualifiers      JSON list, usually empty. Seen in these files:
                  ["LESSTHAN"]      reading below the sensor reporting limit; value is the limit (0.1 mg/L for DO)
                  ["DISCONTINUED"]  placeholder row written after the series was discontinued; no value
                  ["DRY"]           sensor out of water (1,308 DO values at 11152850, one on 21 Nov 2024 and the
                                    rest 22 May–5 Jun 2025, reading 7.3–10.4 mg/L). EXCLUDED by metrics.load().
                  ["ZEROFLOW"]      standing water, no discharge (56 DO values at 11152880, 1 at 11152900). Retained.
                  ["ESTIMATED"]     discharge only (11153000). Retained.
```

## Qualifier policy

`src/metrics.py` drops any row whose qualifiers include `DRY` (the probe was not in water, so the
value is not a water measurement) and keeps everything else. Excluding DRY ends the usable
above-reservoir DO record on 22 May 2025 18:15 PST and reduces the 2025 matched-day comparison from
65 to 51 days. `ZEROFLOW` is kept because a standing pool can have a valid oxygen reading.

## Things to know before using the below-dam file

* The dissolved-oxygen record has **54,152 rows with a value**, 2024-03-15 22:45 UTC to
  2025-10-01 08:00 UTC, every one of them Approved at retrieval.
* It is followed by **6,658 rows with no value** and the `DISCONTINUED` qualifier, through
  2025-12-09. Row counts that include these (60,810) overstate the data; the papers use 54,152.
* **4,163** DO rows carry `LESSTHAN`. The scripts take them at 0.1 mg/L, which biases concentration
  summaries (medians, means, saturation) toward higher oxygen; it does not change shares below 1, 3, 5
  or 7 mg/L, because any censored value is below those thresholds.
* No discharge was measured at this gauge. Flow context comes from Dunneville (11153000) and
  Cedar Creek (11152900).

## Later data

The frozen files were requested through 1 January 2026. A live query of the same API on
16 October 2026 (parameter 00300, 1 May 2025 – 16 October 2026) returned no DO values at any of the six
Pacheco gauges after the last values in these files (11152850: 2025-06-05; 11152870: 2025-10-01;
11152880: 2025-05-16; 11152890: 2025-08-04; 11152900: 2025-06-13; 11153000: 2025-08-09, UTC).

## Derived tables (in `analysis/`)

* `daily_metrics.csv` — one row per site and calendar day with ≥ 86 DO readings: n, DO min/max/
  mean, clock hours of the min and max, daily range (`amp`), hours below 7 and 5 mg/L and when
  those spells start and end, temperature min/max/mean and hour of max, mean discharge.
  Written by `src/metrics.py`.
* `night_metrics.csv` — the same idea on a noon-to-noon window so a pre-dawn minimum is not split
  across two calendar days; labelled by the morning date. Written by `src/night_metrics.py`.
  Used in the explainer's discussion of the diel cycle, not in the Note's tables.
* `monthly_coverage.csv` — DO readings per gauge-month and the share of possible 15-minute slots.
* `AUDIT.md` — every quoted number, regenerated. Written by `src/audit.py`.
