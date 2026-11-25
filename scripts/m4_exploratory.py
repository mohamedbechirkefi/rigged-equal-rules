# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""M4 confounder checks. EXPLORATORY: these numbers never change or replace a frozen verdict.

Part 1 (JRN-0015, protocol section 11, "calibration-fit error in P1 (finite bins)"): population
(infinite-n) values of P1 with the exact Gaussian posterior P(Y = 1 | X = x, G = g) in place of the
20-bin calibration map, for the 12 EXP-001/EXP-002 cells. One common threshold c on the posterior,
c chosen so that the overall selection rate equals kappa. Compared with the confirmatory P1 seed means
(results/EXP-002/tables/summary.csv). No simulation; numerical integration only.

Part 2 (JRN-0016, competing explanations of the EXP-004 sign reversal): descriptive statistics of the
frozen score on the full EXP-004 pool (the 16,281 kept rows of adult.test), by the hours partition
only (Group B = hours-per-week below 40). No protected attribute is read or used. No model is fitted.
Outputs: score quantiles among qualified (Y = 1) and unqualified individuals, the share of each above
the pool-wide 70th score percentile (a full-pool analogue of P0 at kappa 0.30), signed calibration of
the group-blind logistic probability by group and by pool-wide score decile, and the score-input
features among qualified individuals.

Usage: PYTHONPATH=src .venv/bin/python scripts/m4_exploratory.py
Writes results/exploratory/m4-confounders/ (CSV tables and manifest.json).
"""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

import numpy as np

from rigged.adult import ARCHIVE, SCORE_MODEL, group_b_hours, load_archive, parse_adult, score
from rigged.analytic import _exceed, p0_population_metrics
from rigged.matrices import EXP12_DELTAS, EXP12_RHOS, gaussian_cell

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "exploratory" / "m4-confounders"


def _write(name: str, rows: list[dict]) -> None:
    with (OUT / name).open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.10g}" if isinstance(v, float) else v) for k, v in r.items()})


# ---------------------------------------------------------------- part 1
def _p1_thresholds(cell, z: float) -> dict[str, float]:
    """x-threshold per group at which the Gaussian posterior equals Phi(z)."""
    out = {}
    for g in ("A", "B"):
        mu, s, sigma = (cell.mu_a, cell.s_a, cell.sigma_a) if g == "A" else (cell.mu_b, cell.s_b, cell.sigma_b)
        k = s * s / (s * s + sigma * sigma)
        sd = np.sqrt(s * s * sigma * sigma / (s * s + sigma * sigma))
        # posterior = Phi((mu + k (x - mu)) / sd) = Phi(z)  <=>  x = mu + (sd z - mu) / k
        out[g] = mu + (sd * z - mu) / k
    return out


def p1_population(cell) -> dict:
    def rate(z):
        t = _p1_thresholds(cell, z)
        tot = 0.0
        for g, share in (("A", 1 - cell.p_b), ("B", cell.p_b)):
            mu, s, sigma = (cell.mu_a, cell.s_a, cell.sigma_a) if g == "A" else (cell.mu_b, cell.s_b, cell.sigma_b)
            pos, neg = _exceed(cell.family, mu, s, sigma, t[g])
            tot += share * (pos + neg)
        return tot

    lo, hi = -40.0, 40.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if rate(mid) > cell.kappa:
            lo = mid
        else:
            hi = mid
    z = 0.5 * (lo + hi)
    t = _p1_thresholds(cell, z)
    m = {}
    for g in ("A", "B"):
        mu, s, sigma = (cell.mu_a, cell.s_a, cell.sigma_a) if g == "A" else (cell.mu_b, cell.s_b, cell.sigma_b)
        pos, neg = _exceed(cell.family, mu, s, sigma, t[g])
        br = cell.base_rate_a if g == "A" else cell.base_rate_b
        m[g] = {"sr": pos + neg, "tpr": pos / br, "fpr": neg / (1 - br), "ppv": pos / (pos + neg)}
    return {"posterior_z": z, "t_a": t["A"], "t_b": t["B"],
            "eog": m["A"]["tpr"] - m["B"]["tpr"], "sr_gap": m["A"]["sr"] - m["B"]["sr"],
            "fpr_gap": m["A"]["fpr"] - m["B"]["fpr"], "ppv_gap": m["A"]["ppv"] - m["B"]["ppv"]}


def part1() -> list[dict]:
    sim = {}
    with (ROOT / "results" / "EXP-002" / "tables" / "summary.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            sim[(r["cell_id"], r["policy"])] = r
    rows = []
    for d in EXP12_DELTAS:
        for rho in EXP12_RHOS:
            cell = gaussian_cell(d, rho)
            pop = p1_population(cell)
            p0 = p0_population_metrics(cell)
            s = sim[(cell.cell_id, "P1")]
            rows.append({
                "cell_id": cell.cell_id,
                "p1_exact_posterior_eog_pp": 100 * pop["eog"],
                "p1_exact_posterior_sr_gap_pp": 100 * pop["sr_gap"],
                "p1_exact_posterior_ppv_gap_pp": 100 * pop["ppv_gap"],
                "p1_exact_posterior_fpr_gap_pp": 100 * pop["fpr_gap"],
                "p1_binned_sim_eog_pp": 100 * float(s["eog_mean"]),
                "p1_binned_sim_eog_lo_pp": 100 * float(s["eog_lo"]),
                "p1_binned_sim_eog_hi_pp": 100 * float(s["eog_hi"]),
                "p1_binned_sim_ppv_gap_pp": 100 * float(s["ppv_gap_mean"]),
                "p0_population_eog_pp": 100 * p0["eog"],
            })
    return rows


# ---------------------------------------------------------------- part 2
def part2() -> tuple[list[dict], list[dict], list[dict], float]:
    model = json.loads(SCORE_MODEL.read_text(encoding="utf-8"))
    table, _ = parse_adult(load_archive(ARCHIVE)["adult.test"])
    x = score(table, model)
    y = table.y
    gb = group_b_hours(table)
    prob = 1.0 / (1.0 + np.exp(-x))
    cut = float(np.quantile(x, 0.70))  # full-pool analogue of the P0 threshold at kappa 0.30
    by_group = []
    for name, mask in (("A (40 or more hours)", ~gb), ("B (below 40 hours)", gb)):
        q, u = mask & y, mask & ~y
        row = {"group": name, "n": int(mask.sum()), "positives": int(q.sum()),
               "base_rate": float(y[mask].mean()),
               "mean_logistic_probability": float(prob[mask].mean()),
               "calibration_in_the_large_pp": 100 * float(prob[mask].mean() - y[mask].mean()),
               "share_qualified_above_p70": float((x[q] > cut).mean()),
               "share_unqualified_above_p70": float((x[u] > cut).mean()),
               "share_selected_above_p70": float((x[mask] > cut).mean())}
        for p in (10, 25, 50, 75, 90):
            row[f"score_q{p}_qualified"] = float(np.quantile(x[q], p / 100))
        for p in (25, 50, 75):
            row[f"score_q{p}_unqualified"] = float(np.quantile(x[u], p / 100))
        by_group.append(row)
    edges = np.quantile(x, np.arange(1, 10) / 10)
    dec = np.searchsorted(edges, x, side="right")
    cal = []
    for b in range(10):
        for name, mask in (("A", ~gb), ("B", gb)):
            m = mask & (dec == b)
            n = int(m.sum())
            cal.append({"score_decile": b + 1, "group": name, "n": n,
                        "observed_rate": float(y[m].mean()) if n else float("nan"),
                        "mean_logistic_probability": float(prob[m].mean()) if n else float("nan")})
    feats = []
    for name, mask in (("A (40 or more hours)", ~gb), ("B (below 40 hours)", gb)):
        for lab, sel in (("qualified", mask & y), ("unqualified", mask & ~y)):
            feats.append({"group": name, "label": lab, "n": int(sel.sum()),
                          "mean_age": float(table.age[sel].mean()),
                          "mean_education_num": float(table.education_num[sel].mean()),
                          "share_capital_gain_positive": float((table.capital_gain[sel] > 0).mean()),
                          "share_capital_loss_positive": float((table.capital_loss[sel] > 0).mean())})
    return by_group, cal, feats, cut


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    _write("p1_exact_posterior.csv", part1())
    by_group, cal, feats, cut = part2()
    _write("exp004_score_by_group.csv", by_group)
    _write("exp004_calibration_by_decile.csv", cal)
    _write("exp004_features_by_label.csv", feats)
    rev = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = bool(subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"], capture_output=True,
                                text=True).stdout.strip())
    files = sorted(p.name for p in OUT.glob("*.csv"))
    manifest = {
        "label": "exploratory (M4 confounder checks); never changes or replaces a frozen verdict",
        "journal": ["JRN-0015 (part 1)", "JRN-0016 (part 2)"],
        "command": "PYTHONPATH=src .venv/bin/python scripts/m4_exploratory.py",
        "code_revision_at_run": rev, "git_dirty_at_run": dirty,
        "python": sys.version.split()[0], "numpy": np.__version__, "platform": platform.platform(),
        "inputs": {"results/EXP-002/tables/summary.csv": hashlib.sha256(
            (ROOT / "results/EXP-002/tables/summary.csv").read_bytes()).hexdigest(),
            "data/raw/adult.zip": hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
            "research/experiments/EXP-004/score_model.json": hashlib.sha256(SCORE_MODEL.read_bytes()).hexdigest()},
        "exp004_pool_score_p70": cut,
        "protected_attributes_used": "none (hours-per-week partition only)",
        "outputs": {f: hashlib.sha256((OUT / f).read_bytes()).hexdigest() for f in files},
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {len(files)} tables to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
