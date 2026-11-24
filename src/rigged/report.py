# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Report generator: tables (CSV, Markdown) and figures (SVG) built only from validated result files.

PDFs go through pandoc (Markdown to Typst, ``-V mainfont="Libertinus Serif"``) and the typst Python
package. Tool locations come from RIGGED_PANDOC and RIGGED_TYPST_PYTHON, defaulting to the owner's
local zero-cost toolchain.
"""

from __future__ import annotations

import csv
import html
import io
import math
import os
import subprocess
from collections import defaultdict
from pathlib import Path

from .analytic import p0_population_metrics
from .config import CellConfig
from .matrices import exp001, exp002, exp003
from .schema import load
from .stats import summarise

PANDOC = os.environ.get("RIGGED_PANDOC", "/Users/bechir/research/labs/.tools/pandoc")
TYPST_PYTHON = os.environ.get("RIGGED_TYPST_PYTHON", "/Users/bechir/research/labs/.tools/py/bin/python")

SUMMARY_METRICS = ("eog", "sr_gap", "fpr_gap", "ppv_gap", "ece_gap", "utility_per_capita", "accuracy",
                   "tpr_a", "tpr_b")


def metric_value(run: dict, name: str):
    if run["status"] != "ok":
        return None
    if name in run["gaps"]:
        return run["gaps"][name]
    if name in run["overall"]:
        return run["overall"][name]
    if name == "tpr_a":
        return run["groups"]["A"]["tpr"]
    if name == "tpr_b":
        return run["groups"]["B"]["tpr"]
    raise KeyError(name)


def _fmt(v, scale: float = 1.0, digits: int = 2) -> str:
    if v is None:
        return "NA"
    return f"{v * scale:.{digits}f}"


def index_runs(bundle: dict) -> dict:
    """(cell_id, policy) -> {seed: run}."""
    idx: dict = defaultdict(dict)
    for r in bundle["runs"]:
        idx[(r["cell_id"], r["policy"])][r["seed"]] = r
    return idx


def summary_rows(bundle: dict) -> list[dict]:
    rows = []
    for (cell, pol), by_seed in index_runs(bundle).items():
        runs = [by_seed[s] for s in sorted(by_seed)]
        row = {"cell_id": cell, "policy": pol, "runs": len(runs), "failed": sum(r["status"] != "ok" for r in runs),
               "undefined_values": sum(len(r.get("undefined", {})) for r in runs),
               "runtime_mean_s": sum(r["runtime_s"] for r in runs) / len(runs)}
        for m in SUMMARY_METRICS:
            s = summarise([metric_value(r, m) for r in runs])
            row[f"{m}_mean"] = s["mean"]
            row[f"{m}_sd"] = s["sd"]
            row[f"{m}_lo"] = s["boot_lo"]
            row[f"{m}_hi"] = s["boot_hi"]
            row[f"{m}_missing"] = s["n_missing"]
        rows.append(row)
    return rows


def contrast_rows(bundle: dict, contrasts) -> list[dict]:
    """Paired (within-seed) differences of each gap between a treatment and a control cell, per policy."""
    idx = index_runs(bundle)
    out = []
    policies = sorted({p for (_, p) in idx})
    for treat, ctrl in contrasts:
        for pol in policies:
            if (treat, pol) not in idx or (ctrl, pol) not in idx:
                continue
            a, b = idx[(treat, pol)], idx[(ctrl, pol)]
            seeds = sorted(set(a) & set(b))
            for m in ("eog", "sr_gap", "ppv_gap", "fpr_gap"):
                diffs = []
                for s in seeds:
                    va, vb = metric_value(a[s], m), metric_value(b[s], m)
                    diffs.append(None if va is None or vb is None else va - vb)
                st = summarise(diffs)
                out.append({"treatment": treat, "control": ctrl, "policy": pol, "metric": m, **st})
    return out


def policy_vs_p0_rows(bundle: dict) -> list[dict]:
    """Paired utility difference of each policy against P0 within cell and seed."""
    idx = index_runs(bundle)
    out = []
    for (cell, pol), runs in sorted(idx.items()):
        if pol == "P0" or (cell, "P0") not in idx:
            continue
        base = idx[(cell, "P0")]
        diffs = []
        for s in sorted(set(runs) & set(base)):
            va, vb = metric_value(runs[s], "utility_per_capita"), metric_value(base[s], "utility_per_capita")
            diffs.append(None if va is None or vb is None else va - vb)
        out.append({"cell_id": cell, "policy": pol, "metric": "utility_per_capita minus P0", **summarise(diffs)})
    return out


def analytic_rows(bundle: dict) -> list[dict]:
    """P0 implementation check: simulated seed mean versus the population value (3 bootstrap SE)."""
    out = []
    idx = index_runs(bundle)
    for (cell_id, pol), by_seed in sorted(idx.items()):
        if pol != "P0":
            continue
        runs = [by_seed[s] for s in sorted(by_seed)]
        if any(r["status"] != "ok" for r in runs):
            continue
        cfg = {k: v for k, v in runs[0]["config"]["cell"].items() if k not in ("base_rate_a", "base_rate_b")}
        cell = CellConfig(**cfg)
        if cell.is_real:  # no analytic model for real data (EXP-004)
            continue
        if not (0 < cell.kappa < 1 and 0 < cell.p_b < 1):
            continue
        pop = p0_population_metrics(cell)
        for m in ("eog", "sr_gap", "fpr_gap", "ppv_gap"):
            s = summarise([metric_value(r, m) for r in runs])
            if s["mean"] is None or s["boot_se"] is None:
                continue
            z = (s["mean"] - pop[m]) / s["boot_se"] if s["boot_se"] > 0 else math.inf
            out.append({"cell_id": cell_id, "metric": m, "population_value": pop[m], "sim_mean": s["mean"],
                        "boot_se": s["boot_se"], "z": z, "within_3se": abs(z) <= 3.0, "n_seeds": s["n_seeds"]})
    return out


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if v is None else (f"{v:.10g}" if isinstance(v, float) else v)) for k, v in r.items()})


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    buf = io.StringIO()
    buf.write("| " + " | ".join(headers) + " |\n")
    buf.write("|" + "|".join("---" for _ in headers) + "|\n")
    for r in rows:
        buf.write("| " + " | ".join(r) + " |\n")
    return buf.getvalue()


def strip_plot_svg(series: list[tuple[str, list[float]]], title: str, ylabel: str, desc: str,
                   ref: float | None = None) -> str:
    """Accessible SVG strip plot: one column per series, one dot per seed, a bar at the mean."""
    w, h, ml, mr, mt, mb = 760, 400, 110, 20, 40, 120
    vals = [v for _, vs in series for v in vs if v is not None]
    if ref is not None:
        vals.append(ref)
    if not vals:
        vals = [0.0, 1.0]
    lo, hi = min(vals), max(vals)
    if hi - lo < 1e-9:
        lo, hi = lo - 1, hi + 1
    pad = 0.08 * (hi - lo)
    lo, hi = lo - pad, hi + pad
    pw, ph = w - ml - mr, h - mt - mb

    def ypix(v: float) -> float:
        return mt + ph * (1 - (v - lo) / (hi - lo))

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
           f'aria-labelledby="t d">',
           f'<title id="t">{html.escape(title)}</title><desc id="d">{html.escape(desc)}</desc>',
           f'<rect width="{w}" height="{h}" fill="#ffffff"/>',
           f'<text x="{w / 2}" y="22" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#111">'
           f'{html.escape(title)}</text>']
    for i in range(6):
        v = lo + (hi - lo) * i / 5
        y = ypix(v)
        out.append(f'<line x1="{ml}" x2="{w - mr}" y1="{y:.1f}" y2="{y:.1f}" stroke="#e3e3e3"/>')
        out.append(f'<text x="{ml - 6}" y="{y + 4:.1f}" text-anchor="end" font-family="sans-serif" font-size="11" '
                   f'fill="#333">{v:.1f}</text>')
    if ref is not None:
        y = ypix(ref)
        out.append(f'<line x1="{ml}" x2="{w - mr}" y1="{y:.1f}" y2="{y:.1f}" stroke="#555" stroke-dasharray="4 3"/>')
    out.append(f'<text transform="translate(16 {mt + ph / 2}) rotate(-90)" text-anchor="middle" '
               f'font-family="sans-serif" font-size="12" fill="#111">{html.escape(ylabel)}</text>')
    k = max(len(series), 1)
    step = pw / k
    for j, (label, vs) in enumerate(series):
        cx = ml + step * (j + 0.5)
        good = [v for v in vs if v is not None]
        for i, v in enumerate(good):
            jitter = ((i * 37) % 11 - 5) * step * 0.03
            out.append(f'<circle cx="{cx + jitter:.1f}" cy="{ypix(v):.1f}" r="3" fill="#1f4e79" fill-opacity="0.7"/>')
        if good:
            m = sum(good) / len(good)
            out.append(f'<line x1="{cx - step * 0.3:.1f}" x2="{cx + step * 0.3:.1f}" y1="{ypix(m):.1f}" '
                       f'y2="{ypix(m):.1f}" stroke="#b03a2e" stroke-width="2.5"/>')
        out.append(f'<text transform="translate({cx:.1f} {h - mb + 12}) rotate(-35)" text-anchor="end" '
                   f'font-family="sans-serif" font-size="11" fill="#111">{html.escape(label)}</text>')
    out.append(f'<line x1="{ml}" x2="{ml}" y1="{mt}" y2="{mt + ph}" stroke="#111"/>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def planned_run_counts() -> dict:
    counts: dict = {}
    seen = set()
    for mk in (exp001, exp002, exp003):
        m = mk()
        c = defaultdict(int)
        for spec in m.runs():
            key = (spec.cell.cell_id, spec.policy, spec.seed, spec.cell)
            if key in seen:  # P0 runs shared between EXP-001 and EXP-002 are computed once
                continue
            seen.add(key)
            c[spec.policy] += 1
        counts[m.matrix_id] = dict(c)
    return counts


def build(result_dir: Path, contrasts=(("d0.50-r1.00", "d0.00-r1.00"),), pdf: bool = False,
          title: str | None = None, analytic: bool = True) -> dict:
    """Build tables, figures and a Markdown report from ``result_dir/results.json``."""
    bundle = load(result_dir / "results.json", "rigged.result_bundle")
    manifest = load(result_dir / "run_manifest.json", "rigged.run_manifest")
    label = bundle["label"].upper()
    tables, figs = result_dir / "tables", result_dir / "figures"
    srows = summary_rows(bundle)
    crows = contrast_rows(bundle, contrasts)
    prows = policy_vs_p0_rows(bundle)
    arows = analytic_rows(bundle) if analytic else []
    write_csv(srows, tables / "summary.csv")
    write_csv(crows, tables / "contrasts.csv")
    write_csv(prows, tables / "policy_vs_p0.csv")
    write_csv(arows, tables / "analytic_check.csv")

    idx = index_runs(bundle)
    series = [(f"{c} {p}", [None if metric_value(idx[(c, p)][s], "eog") is None
                            else 100 * metric_value(idx[(c, p)][s], "eog") for s in sorted(idx[(c, p)])])
              for (c, p) in idx]
    figs.mkdir(parents=True, exist_ok=True)
    fig_name = f"XFIG-{bundle['matrix_id']}-01-eog.svg"
    n_seeds = len(bundle["seeds"])
    real = any(r["config"]["cell"].get("data_source") for r in bundle["runs"])
    kind = "Real data (UCI Adult score and label; abstract partition)" if real else "Simulated data"
    desc = (f"{label} {'real-data' if real else 'simulated'} results. Strip plot of the per-seed equal-opportunity gap (TPR_A minus TPR_B, "
            f"percentage points) for each cell and policy; dots are seeds ({n_seeds} per column), the red bar is "
            f"the seed mean, the dashed line marks zero. n = {bundle['n']} per population.")
    (figs / fig_name).write_text(strip_plot_svg(series, f"{label}: equal-opportunity gap per seed",
                                                "EOG (percentage points)", desc, ref=0.0), encoding="utf-8")

    runtimes = defaultdict(list)
    for r in bundle["runs"]:
        runtimes[r["policy"]].append(r["runtime_s"])
    rt = {p: sum(v) / len(v) for p, v in runtimes.items()}

    lines = [f"<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->",
             f"# {title or bundle['description']}", "",
             f"**{label}. {kind}. Not a finding.** The protocol is not frozen "
             f"({bundle['protocol']['status_reason']}); nothing here is confirmatory evidence." if
             bundle["label"] == "exploratory" else f"**{label}. {kind}.**", "",
             "Generated by `python -m rigged.cli report` from `results.json` (schema "
             f"{bundle['schema']} {bundle['schema_version']}); do not edit by hand.", "",
             "## Execution record", "",
             md_table(["Field", "Value"], [
                 ["Matrix", bundle["matrix_id"]], ["Label", bundle["label"]],
                 ["Population size n (fitting and evaluation, each)", str(bundle["n"])],
                 ["Seeds", f"{bundle['seeds'][0]} to {bundle['seeds'][-1]} ({n_seeds})"],
                 ["Runs planned / ok / failed", f"{bundle['counts']['planned']} / {bundle['counts']['ok']} / "
                                                f"{bundle['counts']['failed']}"],
                 ["Command", f"`{manifest['command']}`"],
                 ["Git revision", f"{manifest['environment']['git_revision']} (dirty: "
                                  f"{manifest['environment']['git_dirty']})"],
                 ["Environment", f"Python {manifest['environment']['python']}, numpy "
                                 f"{manifest['environment']['numpy']}, {manifest['environment']['cpu']}, "
                                 f"{manifest['environment']['os']}"],
                 ["Wall clock (s)", f"{manifest['wall_clock_s']:.2f}"],
                 ["Peak RSS (MiB)", _fmt(manifest["peak_rss_bytes"], 1 / 2 ** 20, 1)],
                 ["Mean runtime per run (s), by policy", ", ".join(f"{p} {v:.3f}" for p, v in sorted(rt.items()))],
             ]),
             "## Per cell and policy (seed means, 95% percentile bootstrap over seeds)", "",
             "Gaps are group A minus group B, in percentage points; utility is per capita.", ""]
    lines.append(md_table(["Cell", "Policy", "Runs", "Failed", "EOG mean", "95% bootstrap", "EOG SD"],
                          [[r["cell_id"], r["policy"], str(r["runs"]), str(r["failed"]), _fmt(r["eog_mean"], 100),
                            f"[{_fmt(r['eog_lo'], 100)}, {_fmt(r['eog_hi'], 100)}]", _fmt(r["eog_sd"], 100)]
                           for r in srows]))
    lines += ["Secondary metrics (seed means).", ""]
    lines.append(md_table(["Cell", "Policy", "SR gap", "FPR gap", "PPV gap", "ECE gap", "Utility", "Undefined"],
                          [[r["cell_id"], r["policy"], _fmt(r["sr_gap_mean"], 100), _fmt(r["fpr_gap_mean"], 100),
                            _fmt(r["ppv_gap_mean"], 100), _fmt(r["ece_gap_mean"], 100),
                            _fmt(r["utility_per_capita_mean"], 1, 4), str(r["undefined_values"])] for r in srows]))
    if crows:
        lines += ["## Paired contrasts (treatment minus control, within seed)", ""]
        lines.append(md_table(["Treatment", "Control", "Policy", "Metric", "Mean (pp)", "SD (pp)", "95% bootstrap",
                               "95% t-interval", "Seeds"],
                              [[c["treatment"], c["control"], c["policy"], c["metric"], _fmt(c["mean"], 100),
                                _fmt(c["sd"], 100), f"[{_fmt(c['boot_lo'], 100)}, {_fmt(c['boot_hi'], 100)}]",
                                f"[{_fmt(c['t_lo'], 100)}, {_fmt(c['t_hi'], 100)}]", str(c["n_seeds"])]
                               for c in crows]))
    if prows:
        lines += ["## Utility per capita relative to P0 (paired within seed)", ""]
        lines.append(md_table(["Cell", "Policy", "Mean difference", "95% bootstrap", "Seeds"],
                              [[p["cell_id"], p["policy"], _fmt(p["mean"], 1, 4),
                                f"[{_fmt(p['boot_lo'], 1, 4)}, {_fmt(p['boot_hi'], 1, 4)}]", str(p["n_seeds"])]
                               for p in prows]))
    if arows:
        lines += ["## Implementation check: P0 against the population value (numerical integration)", "",
                  "Pass criterion (protocol section 7): simulated seed mean within 3 bootstrap standard errors.", ""]
        lines.append(md_table(["Cell", "Metric", "Population (pp)", "Simulated mean (pp)", "Bootstrap SE (pp)", "z",
                               "Within 3 SE"],
                              [[a["cell_id"], a["metric"], _fmt(a["population_value"], 100, 3),
                                _fmt(a["sim_mean"], 100, 3), _fmt(a["boot_se"], 100, 3), f"{a['z']:.2f}",
                                "yes" if a["within_3se"] else "NO"] for a in arows]))
    if bundle["n"] == 20_000:
        planned = planned_run_counts()
        lines += ["## Projected runtime of the full draft matrix (planning measurement)", "",
                  "Mean measured runtime per run of each policy at n = 20,000, multiplied by the number of unique "
                  "runs each registered matrix plans (P0 runs shared by EXP-001 and EXP-002 counted once). "
                  "Excludes report generation and the analytic cross-check.", ""]
        prow, total = [], 0.0
        for mid, counts in planned.items():
            secs = sum(rt.get(p, float("nan")) * c for p, c in counts.items())
            total += secs
            prow.append([mid, ", ".join(f"{p}: {c}" for p, c in sorted(counts.items())), f"{secs:.1f}"])
        prow.append(["Total", str(sum(sum(c.values()) for c in planned.values())), f"{total:.1f}"])
        lines.append(md_table(["Matrix", "Unique runs by policy", "Projected seconds"], prow))
        out_projection = {"planned_runs": planned, "mean_runtime_s": rt, "projected_total_s": total}
    else:
        out_projection = None
    failures = [r for r in bundle["runs"] if r["status"] != "ok"]
    lines += ["## Failures and undefined values", ""]
    if failures:
        lines.append(md_table(["Run", "Reason"], [[r["run_id"], r["failure_reason"]] for r in failures]))
    else:
        lines.append("No run failed.\n")
    undef = defaultdict(int)
    for r in bundle["runs"]:
        for k, v in r.get("undefined", {}).items():
            undef[(r["cell_id"], r["policy"], k, v)] += 1
    if undef:
        lines.append(md_table(["Cell", "Policy", "Metric", "Reason", "Runs"],
                              [[c, p, k, v, str(n)] for (c, p, k, v), n in sorted(undef.items())]))
    else:
        lines.append("No metric was undefined.\n")
    lines += ["## Figure", "", f"![{fig_name.removesuffix('.svg')}. {desc}](figures/{fig_name})", ""]
    report = result_dir / "report.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    out = {"report": str(report), "tables": [str(p) for p in sorted(tables.glob("*.csv"))],
           "figures": [str(figs / fig_name)], "pdf": None, "projection": out_projection}
    if pdf:
        out["pdf"] = str(build_pdf(report))
    return out


def build_pdf(markdown: Path) -> Path:
    """Markdown to Typst with pandoc, then compile with the typst Python package."""
    typ = markdown.with_suffix(".typ")
    pdf = markdown.with_suffix(".pdf")
    subprocess.run([PANDOC, markdown.name, "-s", "-t", "typst", "-V", "mainfont=Libertinus Serif",
                    "-V", "fontsize=10pt", "-V", "header-includes=#show figure: set block(breakable: true)",
                    "-o", typ.name],
                   cwd=markdown.parent, check=True)
    subprocess.run([TYPST_PYTHON, "-c", f"import typst; typst.compile({typ.name!r}, output={pdf.name!r})"],
                   cwd=markdown.parent, check=True)
    typ.unlink()
    return pdf
