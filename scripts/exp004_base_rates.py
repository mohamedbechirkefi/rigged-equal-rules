# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""EXP-004 secondary (protocol section 3, descriptive): base-rate gap of each cell's partition.

Reads results/EXP-004/results.json and writes results/EXP-004/tables/base_rate_gap.csv: per cell,
the evaluation-half base rate P(Y = 1) of Group A and Group B and the gap A minus B, summarised over
seeds with the frozen interval method (rigged.stats.summarise: percentile bootstrap, 10,000 resamples,
seed 20261124). The partition does not depend on the policy, so the P0 runs are used.

Usage: PYTHONPATH=src .venv/bin/python scripts/exp004_base_rates.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from rigged.stats import summarise

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    bundle = json.loads((ROOT / "results" / "EXP-004" / "results.json").read_text(encoding="utf-8"))
    rows = []
    for cell in sorted({r["cell_id"] for r in bundle["runs"]}):
        runs = sorted((r for r in bundle["runs"] if r["cell_id"] == cell and r["policy"] == "P0" and r["status"] == "ok"),
                      key=lambda r: r["seed"])
        series = {
            "base_rate_a": [r["groups"]["A"]["positives"] / r["groups"]["A"]["n"] for r in runs],
            "base_rate_b": [r["groups"]["B"]["positives"] / r["groups"]["B"]["n"] for r in runs],
            "group_b_share": [r["groups"]["B"]["n"] / r["overall"]["n"] for r in runs],
        }
        series["base_rate_gap"] = [a - b for a, b in zip(series["base_rate_a"], series["base_rate_b"])]
        for metric, values in series.items():
            rows.append({"cell_id": cell, "policy_runs_used": "P0", "metric": metric, **summarise(values)})
    out = ROOT / "results" / "EXP-004" / "tables" / "base_rate_gap.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if v is None else (f"{v:.10g}" if isinstance(v, float) else v)) for k, v in r.items()})
    print(f"wrote {out.relative_to(ROOT)} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
