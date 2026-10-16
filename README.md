# TailWater

Dissolved oxygen in the water released from a small dam, measured continuously.

TailWater is a small, fully reproducible analysis of public U.S. Geological Survey (USGS)
15-minute water-quality records on **North Fork Pacheco Creek and Pacheco Creek, Santa Clara
County, California**, for the two years (March 2024 – October 2025) in which USGS operated a
gauge 0.1 km below Pacheco Reservoir alongside an unregulated gauge above the reservoir and
gauges 3 km and 13 km downstream. It is the code and data behind a research note submitted to the
*California Fish and Wildlife Journal* and a longer explainer written for general readers.

The headline result: during the April–October release seasons of 2024 and 2025, dissolved oxygen
at the outlet was below the Central Coast Basin Plan cold-water objective (7 mg/L) in 97–99 % of
readings, below 3 mg/L for continuous episodes of 46 and 65 days, and at the sensor reporting
limit (0.1 mg/L) for most of June 2025, while the same creek above the reservoir stayed near
saturation. Oxygen was substantially higher 3 km downstream.

A project of [Blue Leaf Labs](https://blueleaflabs.org).

## Layout

```
TailWater/
  src/
    fetch_usgs.py        download the USGS records (resumable; see data/DATA.md)
    metrics.py           load(site) -> 15-min DataFrame in PST; writes analysis/daily_metrics.csv
    night_metrics.py     noon-to-noon nightly minima -> analysis/night_metrics.csv
    audit.py             regenerates every number quoted in the papers -> analysis/AUDIT.md
    figures/
      fig_timeseries.py  Note Figure 2  (paper/figs/note_fig2_timeseries.png)
      fig_map_profile.py Note Figure 1  (paper/figs/fig4_map_profile.png)
      fig_explainer.py   Note Figure 3 + explainer figures 1 and 3 (paper/figs/fig1_*, fig2_*, fig3_*)
  data/                  frozen USGS records as downloaded 15 Oct 2026 (see data/DATA.md)
  analysis/              derived tables, monthly coverage, and the audit
  sources/               documents cited (large PDFs not tracked in git; see sources/SOURCES.md)
  paper/                 explainer (.docx/.pdf) and submission/ (journal package)
```

## Reproduce everything

```
pip install -r requirements.txt
./run_all.sh
```

`run_all.sh` runs `metrics.py`, `night_metrics.py`, `audit.py` and the three figure scripts, in
that order, from the frozen `data/`. Every script sets its own working directory to the repository
root, so each can also be run on its own from anywhere. The whole pipeline takes about a minute.

`analysis/AUDIT.md` is the check that matters: it lists every monitoring-derived statistic in the Note
and the explainer, regenerated from the raw 15-minute records. If you change the data or the code
and a number in the papers no longer matches AUDIT.md, the papers are wrong.

To re-download the data instead of using the frozen copy, run `python3 src/fetch_usgs.py`. USGS
may revise records after the fact, so a fresh download is not guaranteed to reproduce the frozen
numbers exactly; the frozen files are the ones the papers describe.

## Method, in brief

* Times are converted to Pacific Standard Time with no daylight-saving shift.
* Daily statistics use calendar days with at least 86 of 96 possible 15-minute readings.
* Threshold shares (below 7, 5, 3, 1 mg/L) are computed from the raw 15-minute readings.
* Percent saturation uses the Benson–Krause (1984) equation at standard pressure.
* "Matched days" are April–October days on which the above-reservoir and below-dam gauges both
  qualify; differences are medians of daily differences with interquartile ranges.
* Low-oxygen episodes are spells with every reading below a threshold, allowing gaps of 1 h or
  less; a strict no-gap variant is also reported.
* Readings below the 0.1 mg/L reporting limit are taken as 0.1 mg/L, which biases results toward
  higher oxygen.

Full description: the Note in `paper/submission/` and Sections 3–4 of the explainer in `paper/`.

## Gauges

| USGS site | Name | Role |
|---|---|---|
| 11152850 | North Fork Pacheco Creek above Pacheco Reservoir | unregulated reference, ~4 km above the reservoir |
| 11152870 | North Fork Pacheco Creek below Pacheco Reservoir | 0.1 km below the dam, in the outlet pool |
| 11152890 | Pacheco Creek at Bell Station | ~3 km below the dam |
| 11153000 | Pacheco Creek near Dunneville | ~13 km below the dam; also discharge |
| 11152880 | South Fork Pacheco Creek | unregulated tributary |
| 11152900 | Cedar Creek | unregulated tributary; discharge |
| 11173200 | Arroyo Hondo near San José | regional unregulated comparison (explainer only) |

## Working notes

`analysis/PRIOR_ART.md` records the search for any earlier measurement or statement of oxygen in
the reservoir's releases (none was found beyond the EIR's hypothesis). `analysis/CONFOUNDERS.md`
is the list of simple alternative explanations that were tested before the finding was written up,
with the test and outcome for each.

## Rebuilding the papers

The Note and cover letter in `paper/submission/` are generated Word files. Their text lives in
`paper/submission/src/note_text.js`; `build_note.js` and `build_cover.js` render it with the
`docx` npm package (`npm install docx image-size`, then `node build_note.js out.docx`). Setting
`FIGS=<fig1>,<fig2>,<fig3>` on the command line embeds the figures after their captions to make
a reading copy; the journal file is built without it. The explainer is maintained as a document
and exported; its `.docx`/`.pdf` here are snapshots.

## Citing

Data: U.S. Geological Survey. 2026. USGS water data for the Nation. https://doi.org/10.5066/F7P55KJN

Code: TailWater v1.0, Blue Leaf Labs, 2026. https://github.com/blueleaflabs/TailWater (archive DOI to be added at release)

## License

Code: MIT. Text and figures in `paper/`: CC BY 4.0. The USGS data in `data/` are U.S. Government
works in the public domain.
