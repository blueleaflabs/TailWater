#!/usr/bin/env bash
# Rebuild every derived table, the audit, and every figure from the frozen data/.
set -euo pipefail
cd "$(dirname "$0")"
python3 src/metrics.py
python3 src/night_metrics.py
python3 src/audit.py > /dev/null
python3 src/figures/fig_timeseries.py
python3 src/figures/fig_map_profile.py
python3 src/figures/fig_explainer.py
echo "done — compare analysis/AUDIT.md against the numbers in paper/"
