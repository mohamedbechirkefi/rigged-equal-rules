# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""M4 evidence audit (master prompt 11.5): re-derive reported numbers from the raw run records and
trace every decimal number in the manuscript and reports to a committed result file.

Part A, raw-output checks per experiment (results/EXP-NNN/results.json):
  run count and status; per-run identities (group n sum to the evaluation n, tp + fn = positives,
  fp + tn = negatives, selected = tp + fp, rates recomputed from counts, gaps = A minus B);
  summary.csv and contrasts.csv re-derived from the per-run values with an independent
  implementation of the frozen interval method (mean; percentile bootstrap over seeds, 10,000
  resamples, PCG64 seed 20261124; t-interval); SHA256SUMS verified.
Part B, number trace: every number with a decimal point in the listed documents is looked up
  among the values of the committed tables (raw values, and values times 100 for proportions
  shown in pp or %), at the precision shown. Unmatched numbers are listed for manual review
  (many are parameters, hashes, versions or durations from provenance files).

Usage: PYTHONPATH=src .venv/bin/python scripts/m4_evidence_audit.py
Writes research/publication/evidence_audit_output.json and number_trace.csv.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EXPS = ("EXP-001", "EXP-002", "EXP-003", "EXP-004")
GAPS = ("eog", "sr_gap", "fpr_gap", "ppv_gap", "ece_gap")
DOCS = [
    "research/paper/manuscript.md",
    "research/paper/supplementary.md",
    "research/experiments/EXP-001/report.md",
    "research/experiments/EXP-002/report.md",
    "research/experiments/EXP-003/report.md",
    "research/experiments/EXP-004/report.md",
    "research/claims_register.csv",
]


def t975(df: int) -> float:
    from rigged.numerics import t_ppf  # the frozen helper; checked against scipy-free tables in tests
    return t_ppf(0.975, df)


def interval(v: list[float]) -> dict:
    a = np.asarray(v, dtype=np.float64)
    k = a.shape[0]
    rng = np.random.Generator(np.random.PCG64(20261124))
    means = a[rng.integers(0, k, size=(10_000, k))].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    sd = a.std(ddof=1)
    h = t975(k - 1) * sd / math.sqrt(k)
    return {"mean": a.mean(), "sd": sd, "boot_lo": lo, "boot_hi": hi, "t_lo": a.mean() - h, "t_hi": a.mean() + h}


def run_metric(r: dict, m: str):
    if m in GAPS:
        return r["gaps"].get(m)
    if m in ("utility_per_capita", "accuracy"):
        return r["overall"][m]
    if m in ("tpr_a", "tpr_b"):
        return r["groups"][m[-1].upper()]["tpr"]
    return None


def part_a() -> dict:
    out = {}
    for e in EXPS:
        d = ROOT / "results" / e
        b = json.loads((d / "results.json").read_text(encoding="utf-8"))
        runs = b["runs"]
        issues = []
        status = defaultdict(int)
        for r in runs:
            status[r["status"]] += 1
            if r["status"] != "ok":
                continue
            o, ga, gb = r["overall"], r["groups"]["A"], r["groups"]["B"]
            if ga["n"] + gb["n"] != o["n"]:
                issues.append(f"{r['run_id']}: group n do not sum to the evaluation n")
            for gname, g in (("A", ga), ("B", gb)):
                if g["tp"] + g["fn"] != g["positives"] or g["fp"] + g["tn"] != g["negatives"]:
                    issues.append(f"{r['run_id']} {gname}: confusion counts")
                if g["tp"] + g["fp"] != g["selected"] or g["positives"] + g["negatives"] != g["n"]:
                    issues.append(f"{r['run_id']} {gname}: selected or n")
                for k, num, den in (("tpr", g["tp"], g["positives"]), ("fpr", g["fp"], g["negatives"]),
                                    ("ppv", g["tp"], g["selected"]), ("sr", g["selected"], g["n"])):
                    if den and abs(g[k] - num / den) > 1e-12:
                        issues.append(f"{r['run_id']} {gname}: {k} differs from its counts")
            for k in ("eog", "sr_gap", "fpr_gap", "ppv_gap"):
                base = {"eog": "tpr", "sr_gap": "sr", "fpr_gap": "fpr", "ppv_gap": "ppv"}[k]
                if abs(r["gaps"][k] - (ga[base] - gb[base])) > 1e-12:
                    issues.append(f"{r['run_id']}: {k} is not A minus B")
            u = (o["tp"] - r["config"]["cell"]["cost_ratio"] * o["fp"]) / o["n"]
            if abs(u - o["utility_per_capita"]) > 1e-12:
                issues.append(f"{r['run_id']}: utility differs from (TP - c FP) / n")
        # re-derive summary.csv
        by = defaultdict(list)
        for r in runs:
            by[(r["cell_id"], r["policy"])].append(r)
        max_dev = 0.0
        n_checked = 0
        with (d / "tables" / "summary.csv").open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                rs = sorted(by[(row["cell_id"], row["policy"])], key=lambda r: r["seed"])
                if int(row["runs"]) != len(rs) or len(rs) != 20:
                    issues.append(f"summary {row['cell_id']} {row['policy']}: run count {row['runs']}")
                for m in GAPS + ("utility_per_capita", "accuracy", "tpr_a", "tpr_b"):
                    s = interval([run_metric(r, m) for r in rs])
                    for k in ("mean", "sd", "boot_lo", "boot_hi"):
                        dev = abs(float(row[f"{m}_{'lo' if k == 'boot_lo' else 'hi' if k == 'boot_hi' else k}"]) - s[k])
                        max_dev = max(max_dev, dev)
                        n_checked += 1
        # re-derive contrasts.csv
        cdev = 0.0
        nc = 0
        with (d / "tables" / "contrasts.csv").open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                tr = {r["seed"]: r for r in by[(row["treatment"], row["policy"])]}
                ct = {r["seed"]: r for r in by[(row["control"], row["policy"])]}
                diffs = [run_metric(tr[s], row["metric"]) - run_metric(ct[s], row["metric"]) for s in sorted(tr)]
                st = interval(diffs)
                for k in ("mean", "sd", "boot_lo", "boot_hi", "t_lo", "t_hi"):
                    cdev = max(cdev, abs(float(row[k]) - st[k]))
                    nc += 1
                if int(row["n_seeds"]) != 20:
                    issues.append(f"contrast {row['treatment']} {row['metric']}: n_seeds {row['n_seeds']}")
        # SHA256SUMS
        bad = []
        for line in (d / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            h, name = line.split(maxsplit=1)
            name = name.lstrip("*")
            p = d / name
            if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != h:
                bad.append(name)
        out[e] = {"runs": len(runs), "status": dict(status), "identity_issues": issues[:50],
                  "n_identity_issues": len(issues), "summary_values_checked": n_checked,
                  "summary_max_abs_deviation": max_dev, "contrast_values_checked": nc,
                  "contrast_max_abs_deviation": cdev, "sha256sums_mismatch": bad}
    return out


NUM = re.compile(r"(?<![\w.])-?\d+\.\d+(?![\w.])")


def source_values() -> dict[str, set[str]]:
    """Map from rendered string (at 1 to 5 decimals) to source files that render to it."""
    idx: dict[str, set[str]] = defaultdict(set)
    files = sorted((ROOT / "results").glob("EXP-00?/tables/*.csv")) + \
        sorted((ROOT / "results" / "exploratory" / "m4-confounders").glob("*.csv")) + \
        sorted((ROOT / "results" / "exploratory" / "exp-003-x" / "tables").glob("*.csv"))
    for f in files:
        rel = str(f.relative_to(ROOT))
        with f.open(encoding="utf-8") as fh:
            for row in csv.reader(fh):
                for cell in row:
                    try:
                        v = float(cell)
                    except ValueError:
                        continue
                    if math.isnan(v):
                        continue
                    for scale in (1.0, 100.0):
                        for dp in range(0, 6):
                            for vv in (v * scale, abs(v * scale)):
                                idx[f"{vv:.{dp}f}"].add(rel)
    return idx


def part_b() -> list[dict]:
    idx = source_values()
    rows = []
    for doc in DOCS:
        p = ROOT / doc
        if not p.exists():
            continue
        for ln, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if "sha256" in line.lower() or "SHA-256" in line:
                line = re.sub(r"[0-9a-f]{40,64}", "", line)
            for m in NUM.finditer(line):
                s = m.group(0)
                hit = idx.get(s) or idx.get(s.lstrip("-"))
                rows.append({"document": doc, "line": ln, "number": s, "matched": bool(hit),
                             "sources": ";".join(sorted(hit)[:3]) if hit else ""})
    return rows


def main() -> int:
    sys.path.insert(0, str(ROOT / "src"))
    a = part_a()
    b = part_b()
    pub = ROOT / "research" / "publication"
    (pub / "evidence_audit_output.json").write_text(json.dumps(
        {"part_a": a, "part_b_summary": {doc: {"numbers": sum(1 for r in b if r["document"] == doc),
                                               "unmatched": sum(1 for r in b if r["document"] == doc and not r["matched"])}
                                         for doc in DOCS}}, indent=1, default=float) + "\n", encoding="utf-8")
    with (pub / "number_trace.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["document", "line", "number", "matched", "sources"], lineterminator="\n")
        w.writeheader()
        w.writerows(b)
    for e, v in a.items():
        print(e, v["runs"], v["status"], "identity issues", v["n_identity_issues"],
              "summary max dev", f"{v['summary_max_abs_deviation']:.2e}", f"({v['summary_values_checked']})",
              "contrast max dev", f"{v['contrast_max_abs_deviation']:.2e}", f"({v['contrast_values_checked']})",
              "sha mismatches", v["sha256sums_mismatch"])
    for doc in DOCS:
        n = [r for r in b if r["document"] == doc]
        print(doc, "numbers", len(n), "unmatched", sum(1 for r in n if not r["matched"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
