# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Export the published results for the static demo (M5): demo/public/data/results.json.

Reads committed files only: the result tables of EXP-001 to EXP-004 (generated at the confirmatory
revision from results/EXP-NNN/results.json), the committed exploratory tables, the experiment
registry, the claims register and the artifact manifest. Nothing is recomputed from raw runs and no
number is typed by hand: every displayed string is formatted here from a table value, with the
precision the manuscript uses, and tests/test_demo_export.py checks that each string appears
verbatim in research/paper/manuscript.md (or, for documented exceptions, in
research/paper/supplementary.md, or is a group-level rate the manuscript does not print).

Schema: lab-demo-results 1.0.0 (labs/_shared/demo-template/src/results.ts), extended with the
top-level keys "explorer" (EXP-002 synthetic grid), "real_score" (EXP-004) and
"display_exceptions". No timestamps; the output is deterministic.

Usage: python3 scripts/export_demo_data.py [--check]
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "demo" / "public" / "data" / "results.json"

SCHEMA = "lab-demo-results"
SCHEMA_VERSION = "1.0.0"
CI_LEVEL = 0.95
GAP_METRICS = (("sr_gap", "SR gap"), ("eog", "EOG"), ("ppv_gap", "PPV gap"), ("fpr_gap", "FPR gap"))
POLICIES = ("P0", "P1", "P2", "P3")
POLICY_NAMES = {
    "P0": "P0, one raw threshold (baseline)",
    "P1": "P1, one threshold on a within-group calibrated score",
    "P2": "P2, group thresholds with equal selection rates",
    "P3": "P3, group thresholds with equal true positive rates",
}

SOURCES = (
    "research/experiment_registry.csv",
    "research/claims_register.csv",
    "research/publication/artifact_manifest.json",
    "results/EXP-001/tables/contrasts.csv",
    "results/EXP-001/tables/summary.csv",
    "results/EXP-001/tables/analytic_check.csv",
    "results/EXP-002/tables/summary.csv",
    "results/EXP-002/tables/policy_vs_p0.csv",
    "results/EXP-003/tables/summary.csv",
    "results/EXP-003/tables/analytic_check.csv",
    "results/EXP-004/tables/contrasts.csv",
    "results/EXP-004/tables/summary.csv",
    "results/EXP-004/tables/policy_vs_p0.csv",
    "results/EXP-004/tables/base_rate_gap.csv",
    "results/exploratory/exp-003-x/tables/analytic_check.csv",
    "results/exploratory/m4-confounders/p1_exact_posterior.csv",
    "results/exploratory/m4-confounders/exp004_score_by_group.csv",
)


def read_rows(rel: str) -> list[dict]:
    with (ROOT / rel).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def one(rows: list[dict], **match: str) -> dict:
    hit = [r for r in rows if all(r.get(k) == v for k, v in match.items())]
    if len(hit) != 1:
        raise SystemExit(f"expected one row for {match}, found {len(hit)}")
    return hit[0]


def f2(x: float, d: int = 2, sign: bool = False) -> str:
    s = f"{x:+.{d}f}" if sign else f"{x:.{d}f}"
    return s


def estimate(label: str, mean: float, lo: float | None, hi: float | None, unit: str, scale: float,
             d: int, suffix: str = "", sign: bool = False, kind: str = "measured") -> dict:
    """One estimate in the template schema. Values are stored in display units (pp, % or per capita)."""
    m = mean * scale
    e = {"label": label, "estimate": m, "ci_low": None, "ci_high": None, "ci_level": None, "unit": unit,
         "display": f2(m, d, sign) + suffix, "interval_display": None, "kind": kind}
    if lo is not None and hi is not None:
        e.update(ci_low=lo * scale, ci_high=hi * scale, ci_level=CI_LEVEL,
                 interval_display=f"[{f2(lo * scale, d)}, {f2(hi * scale, d)}]")
    return e


def summary_est(rows: list[dict], cell: str, policy: str, metric: str, label: str, suffix: str = "",
                sign: bool = False) -> dict:
    r = one(rows, cell_id=cell, policy=policy)
    return estimate(label, float(r[f"{metric}_mean"]), float(r[f"{metric}_lo"]), float(r[f"{metric}_hi"]),
                    "pp", 100.0, 2, suffix, sign)


def contrast_est(rows: list[dict], metric: str, label: str, suffix: str = "", **match: str) -> dict:
    r = one(rows, metric=metric, **match)
    return estimate(label, float(r["mean"]), float(r["boot_lo"]), float(r["boot_hi"]), "pp", 100.0, 2, suffix)


def claim_ids(claims: list[dict], exp_id: str) -> list[str]:
    out = []
    for c in claims:
        e = c["experiment_id"].strip()
        if e == exp_id:
            out.append(c["claim_id"])
        elif " to " in e:
            a, b = (int(x.split("-")[1]) for x in e.split(" to "))
            if exp_id.startswith("EXP-") and a <= int(exp_id.split("-")[1]) <= b:
                out.append(c["claim_id"])
    return out


def registry_title(reg: list[dict], exp_id: str) -> str:
    return one(reg, experiment_id=exp_id)["title"]


def cell_value(r: dict, metric: str) -> dict:
    mean, lo, hi = (100.0 * float(r[f"{metric}_{k}"]) for k in ("mean", "lo", "hi"))
    return {"estimate": mean, "ci_low": lo, "ci_high": hi,
            "display": f"{mean:.2f} [{lo:.2f}, {hi:.2f}]", "source": "supplementary"}


def group_rate(r: dict, metric: str) -> dict:
    mean, lo, hi = (100.0 * float(r[f"{metric}_{k}"]) for k in ("mean", "lo", "hi"))
    return {"estimate": mean, "ci_low": lo, "ci_high": hi,
            "display": f"{mean:.2f}% [{lo:.2f}, {hi:.2f}]", "exception": "group-rate"}


def utility_value(r: dict, d: int) -> dict:
    mean, lo, hi = float(r["mean"]), float(r["boot_lo"]), float(r["boot_hi"])
    return {"estimate": mean, "ci_low": lo, "ci_high": hi,
            "display": f"{mean:+.{d}f} [{lo:.{d}f}, {hi:.{d}f}]", "source": "supplementary"}


def policy_block(summary: list[dict], util: list[dict], cell: str, util_digits: int) -> list[dict]:
    out = []
    for p in POLICIES:
        r = one(summary, cell_id=cell, policy=p)
        blk = {"policy": p, "name": POLICY_NAMES[p],
               "gaps": {m: cell_value(r, m) for m, _ in GAP_METRICS},
               "tpr_a": group_rate(r, "tpr_a"), "tpr_b": group_rate(r, "tpr_b"),
               "within_2pp_all_three": all(abs(100.0 * float(r[f"{m}_mean"])) <= 2.0
                                           for m in ("sr_gap", "eog", "ppv_gap")),
               "utility_vs_p0": None}
        if p != "P0":
            blk["utility_vs_p0"] = utility_value(one(util, cell_id=cell, policy=p), util_digits)
        out.append(blk)
    return out


def build() -> dict:
    reg = read_rows("research/experiment_registry.csv")
    claims = read_rows("research/claims_register.csv")
    manifest = json.loads((ROOT / "research/publication/artifact_manifest.json").read_text(encoding="utf-8"))
    revs = {e.get("code_revision") for e in manifest["entries"]
            if str(e.get("experiment_id", "")).startswith("EXP-") and e.get("code_revision")}
    confirmatory_revs = {r for r in revs if r.startswith("b455d59")}
    if len(confirmatory_revs) != 1:
        raise SystemExit(f"expected one confirmatory code revision in the manifest, found {sorted(revs)}")
    code_revision = confirmatory_revs.pop()

    s1 = read_rows("results/EXP-001/tables/summary.csv")
    c1 = read_rows("results/EXP-001/tables/contrasts.csv")
    a1 = read_rows("results/EXP-001/tables/analytic_check.csv")
    s2 = read_rows("results/EXP-002/tables/summary.csv")
    u2 = read_rows("results/EXP-002/tables/policy_vs_p0.csv")
    s3 = read_rows("results/EXP-003/tables/summary.csv")
    a3 = read_rows("results/EXP-003/tables/analytic_check.csv")
    c4 = read_rows("results/EXP-004/tables/contrasts.csv")
    s4 = read_rows("results/EXP-004/tables/summary.csv")
    u4 = read_rows("results/EXP-004/tables/policy_vs_p0.csv")
    b4 = read_rows("results/EXP-004/tables/base_rate_gap.csv")
    x3 = read_rows("results/exploratory/exp-003-x/tables/analytic_check.csv")
    p1x = read_rows("results/exploratory/m4-confounders/p1_exact_posterior.csv")
    sg = read_rows("results/exploratory/m4-confounders/exp004_score_by_group.csv")

    prim = {"treatment": "d0.50-r1.00", "control": "d0.00-r1.00", "policy": "P0"}
    pop_prim = (float(one(a1, cell_id="d0.50-r1.00", metric="eog")["population_value"])
                - float(one(a1, cell_id="d0.00-r1.00", metric="eog")["population_value"]))
    check1 = [r for r in a1 if r["cell_id"]]
    pass1 = sum(r["within_3se"] == "True" for r in check1)
    pass3 = sum(r["within_3se"] == "True" for r in a3)
    passx = sum(r["within_3se"] == "True" for r in x3)
    d_rows = [r for r in s3 if r["cell_id"].startswith("D-") and r["policy"] == "P0"]
    d_min = min(d_rows, key=lambda r: float(r["eog_mean"]))

    exp1 = {
        "id": "EXP-001", "title": registry_title(reg, "EXP-001"),
        "status": "confirmatory, complete (240 of 240 runs ok); simulated",
        "verdict": "H1 supported: the interval lies entirely above +2 pp",
        "estimates": [
            contrast_est(c1, "eog", "EOG, primary contrast (d0.50-r1.00 minus d0.00-r1.00, P0)", " pp", **prim),
            contrast_est(c1, "sr_gap", "SR gap, same contrast", **prim),
            contrast_est(c1, "ppv_gap", "PPV gap, same contrast", **prim),
            contrast_est(c1, "fpr_gap", "FPR gap, same contrast", **prim),
            estimate("EOG contrast, population value by numerical integration",
                     pop_prim, None, None, "pp", 100.0, 2, " pp",
                     kind="analytic"),
        ],
        "claim_ids": claim_ids(claims, "EXP-001"),
        "report_path": one(reg, experiment_id="EXP-001")["report_path"],
        "notes": [f"Implementation check: {pass1} of {len(check1)} comparisons within 3 bootstrap SE.",
                  "The primary result is implied by the Gaussian model; the run quantifies it."],
    }
    exp2 = {
        "id": "EXP-002", "title": registry_title(reg, "EXP-002"),
        "status": "confirmatory, complete (960 of 960 runs ok); simulated",
        "verdict": "H1 supported (no policy meets all three parity criteria within 2 pp at d0.50-r1.00; "
                   "all do at the control); H2 supported (P2 and P3 cost utility)",
        "estimates": [
            summary_est(s2, "d0.50-r1.00", "P3", "sr_gap", "Smallest worst violation: P3 SR gap"),
            summary_est(s2, "d0.50-r1.00", "P2", "eog", "P2 EOG"),
            summary_est(s2, "d0.50-r1.00", "P1", "eog", "P1 EOG"),
            summary_est(s2, "d0.50-r1.00", "P1", "ppv_gap", "P1 PPV gap"),
            summary_est(s2, "d0.50-r1.00", "P3", "eog", "P3 EOG"),
        ] + [
            estimate(f"Utility per capita, {p} minus P0", float(r["mean"]), float(r["boot_lo"]),
                     float(r["boot_hi"]), "per capita", 1.0, 5, sign=(p == "P1"))
            for p in ("P2", "P3", "P1") for r in [one(u2, cell_id="d0.50-r1.00", policy=p)]
        ],
        "claim_ids": claim_ids(claims, "EXP-002"),
        "report_path": one(reg, experiment_id="EXP-002")["report_path"],
        "notes": ["Verdict unchanged at tolerances of 1 and 5 pp.",
                  "P1's magnitudes partly reflect its 20-bin calibration map (JRN-0015, exploratory)."],
    }
    exp3 = {
        "id": "EXP-003", "title": registry_title(reg, "EXP-003"),
        "status": "confirmatory, complete (420 of 420 runs ok); simulated; deviation DEC-019",
        "verdict": "H0 rejected; H2 sign reversal (analytically determined, a quantification, not a test); "
                   "H3 supported (sign); H4 supported (sign) with a disclosed limitation (DEC-019)",
        "estimates": [
            summary_est(s3, "A-sB0.5", "P0", "eog", "EOG, equal base rates, s_B 0.5"),
            summary_est(s3, "A-sB2", "P0", "eog", "EOG, equal base rates, s_B 2"),
            summary_est(s3, "B-sB2", "P0", "eog", "EOG, fixed base-rate gap, s_B 2"),
            summary_est(s3, "C-student_t3", "P0", "eog", "EOG, Student t3 latent"),
            summary_est(s3, "C-lognormal", "P0", "eog", "EOG, shifted log-normal latent"),
            summary_est(s3, d_min["cell_id"], "P0", "eog", f"Smallest grid-D EOG ({d_min['cell_id']})"),
        ],
        "claim_ids": claim_ids(claims, "EXP-003"),
        "report_path": one(reg, experiment_id="EXP-003")["report_path"],
        "notes": [f"Implementation check passed {pass3} of {len(a3)} comparisons; the failures are in cells "
                  "D-k0.1-pB0.5 and D-k0.5-pB0.2. The owner accepted them as a disclosed limitation on H4, "
                  "with no rerun (DEC-019, DEC-021). The magnitudes in those two cells are not confirmed at "
                  "the frozen standard.",
                  "All cells share the same 20 seeds, so cells are not independent replications."],
    }
    br = {m: one(b4, cell_id="R-hours", metric=m) for m in ("base_rate_a", "base_rate_b", "base_rate_gap")}
    exp4 = {
        "id": "EXP-004", "title": registry_title(reg, "EXP-004"),
        "status": "confirmatory, complete (160 of 160 runs ok); real data (UCI Adult)",
        "verdict": "H1-real disconfirmed: D is negative, a contradiction of the base-rate prediction",
        "estimates": [
            contrast_est(c4, "eog", "D: EOG of R-hours minus R-hours-random, P0", " pp",
                         treatment="R-hours", control="R-hours-random", policy="P0"),
            estimate("Base rate, 40 or more hours (Group A)", float(br["base_rate_a"]["mean"]),
                     float(br["base_rate_a"]["boot_lo"]), float(br["base_rate_a"]["boot_hi"]), "%", 100.0, 2, "%"),
            estimate("Base rate, below 40 hours (Group B)", float(br["base_rate_b"]["mean"]),
                     float(br["base_rate_b"]["boot_lo"]), float(br["base_rate_b"]["boot_hi"]), "%", 100.0, 2, "%"),
            summary_est(s4, "R-hours-random", "P0", "eog", "Random control, P0 EOG", " pp"),
            summary_est(s4, "R-hours", "P1", "eog", "P1 EOG on R-hours (calibrated equal rule)", " pp", sign=True),
        ],
        "claim_ids": claim_ids(claims, "EXP-004"),
        "report_path": one(reg, experiment_id="EXP-004")["report_path"],
        "notes": ["Group B is hours-per-week below 40. No protected attribute is a group, input, stratifier "
                  "or covariate.",
                  "Intervals cover the random split and tie-breaking only, not sampling from a population."],
    }
    jx = {r["cell_id"]: r for r in p1x}
    sgb = {r["group"][0]: r for r in sg}
    exp_x14 = {
        "id": "JRN-0014", "title": "EXP-003 rerun on seeds 1000 to 1019 (diagnosis of DEC-019)",
        "status": "exploratory, not confirmatory",
        "verdict": "none: exploratory, no frozen rule applies; it changes no verdict",
        "estimates": [], "claim_ids": [], "report_path": "results/exploratory/exp-003-x/report.md",
        "notes": [f"Implementation check {passx} of {len(x3)} on the exploratory seeds."],
    }
    exp_x15 = {
        "id": "JRN-0015", "title": "P1 with the exact Gaussian posterior (calibration-fit confounder)",
        "status": "exploratory, not confirmatory; population values by numerical integration",
        "verdict": "none: exploratory; the EXP-002 H1 verdict is unchanged",
        "estimates": [
            estimate("P1 population EOG at d0.50-r1.00, exact posterior",
                     float(jx["d0.50-r1.00"]["p1_exact_posterior_eog_pp"]), None, None, "pp", 1.0, 2, " pp",
                     kind="analytic"),
            estimate("P1 population PPV gap at d0.50-r1.00, exact posterior",
                     float(jx["d0.50-r1.00"]["p1_exact_posterior_ppv_gap_pp"]), None, None, "pp", 1.0, 2, " pp",
                     kind="analytic"),
        ],
        "claim_ids": ["CLM-018"], "report_path": "research/paper/supplementary.md",
        "notes": ["Deterministic integration: there is no sampling interval. The binned simulation gives "
                  "14.89 [14.30, 15.45] pp for the same cell."],
    }
    exp_x16 = {
        "id": "JRN-0016", "title": "EXP-004 score on the full test pool by the hours partition (post hoc)",
        "status": "exploratory, post hoc, not a test",
        "verdict": "none: descriptive; establishes no cause",
        "estimates": [
            estimate("Qualified members above the pool's 70th percentile, Group B",
                     float(sgb["B"]["share_qualified_above_p70"]), None, None, "%", 100.0, 2, "%",
                     kind="descriptive"),
            estimate("Qualified members above the pool's 70th percentile, Group A",
                     float(sgb["A"]["share_qualified_above_p70"]), None, None, "%", 100.0, 2, "%",
                     kind="descriptive"),
            estimate("Calibration in the large, Group B (probability minus rate)",
                     float(sgb["B"]["calibration_in_the_large_pp"]), None, None, "pp", 1.0, 2, " pp",
                     kind="descriptive"),
        ],
        "claim_ids": ["CLM-019"], "report_path": "research/paper/supplementary.md",
        "notes": ["Full-pool description with no resampling: there is no interval."],
    }

    cells = []
    for r in [x for x in s2 if x["policy"] == "P0"]:
        cid = r["cell_id"]
        delta, rho = float(cid[1:5]), float(cid.split("-r")[1])
        cells.append({"cell_id": cid, "delta": delta, "rho": rho,
                      "policies": policy_block(s2, u2, cid, 5)})
    explorer = {
        "experiment_id": "EXP-002", "label": "measured, simulated", "unit": "pp", "tolerance_pp": 2.0,
        "source": "results/EXP-002/tables/summary.csv; results/EXP-002/tables/policy_vs_p0.csv",
        "metrics": [{"key": k, "label": lab} for k, lab in GAP_METRICS],
        "deltas": sorted({c["delta"] for c in cells}), "rhos": sorted({c["rho"] for c in cells}),
        "cells": cells,
    }
    real_score = {
        "experiment_id": "EXP-004", "label": "measured, real data (UCI Adult test file)", "unit": "pp",
        "tolerance_pp": 2.0,
        "source": "results/EXP-004/tables/summary.csv; results/EXP-004/tables/policy_vs_p0.csv",
        "cells": [{"cell_id": c, "description": d, "policies": policy_block(s4, u4, c, 4)}
                  for c, d in (("R-hours", "Group B is hours-per-week below 40"),
                               ("R-hours-random", "Control: the same group labels permuted within each seed"))],
    }
    return {
        "schema": SCHEMA, "schema_version": SCHEMA_VERSION, "project": "RIGGED",
        "question": "Can equal rules yield unequal outcomes under different starting distributions?",
        "status_label": "Independent research manuscript / preprint draft, not peer-reviewed. EXP-001 to "
                        "EXP-003 are simulated; EXP-004 uses real data. Groups A and B are abstract groups, "
                        "never protected groups.",
        "code_revision": code_revision,
        "sources": [{"path": p, "sha256": sha256(p)} for p in SOURCES],
        "experiments": [exp1, exp2, exp3, exp4, exp_x14, exp_x15, exp_x16],
        "assumptions": [
            {"name": "Latent qualification", "value": "Q ~ N(mu_g, s_g^2); label Y = 1[Q > 0]",
             "source": "manuscript section 3, generator SYN-001"},
            {"name": "Observed score", "value": "X = Q + e, e ~ N(0, sigma_g^2) independent of Q; sigma_A = 0.5, "
             "sigma_B = 0.5 rho", "source": "manuscript section 3"},
            {"name": "Starting-distribution gap", "value": "mu_A = 0, mu_B = -delta; delta in {0, 0.25, 0.5, 1}",
             "source": "manuscript section 4.4"},
            {"name": "Capacity and group share", "value": "kappa = 0.30 selected; p_B = 0.5 in group B",
             "source": "manuscript section 3"},
            {"name": "Population size and seeds", "value": "n = 20,000 fitting and 20,000 evaluation per seed; "
             "seeds 0 to 19", "source": "manuscript section 4.2"},
            {"name": "Utility", "value": "U = (TP - c FP) / n with cost ratio c = 1",
             "source": "manuscript section 3"},
            {"name": "Smallest effect size of interest", "value": "2 pp; no p-value threshold",
             "source": "manuscript section 4.5"},
            {"name": "Interval", "value": "95% percentile bootstrap over seeds, 10,000 resamples",
             "source": "manuscript section 4.5"},
            {"name": "P1 calibration map", "value": "20 quantile bins per group",
             "source": "manuscript section 4.3"},
        ],
        "limitations": [
            "Simulation: EXP-001 to EXP-003 hold only within the generator (hard cutoff on a latent "
            "qualification, additive Gaussian noise, two groups, one score).",
            "Analytic predictability: EXP-001, EXP-002 and EXP-003 H2 were implied before the runs; their "
            "confirmatory status adds reproducibility, not discovery.",
            "Implementation check (DEC-019): EXP-003 passed 56 of 60 comparisons; the owner accepted the failures "
            "as a disclosed limitation on H4.",
            "Correlated cells: all cells share the same 20 seeds by design.",
            "P1 binning: P1's magnitudes and its PPV-parity result depend on the 20-bin calibration map (JRN-0015).",
            "EXP-004: one simple four-feature logistic score and one non-protected partition of one 1994 extract; "
            "a different score could change the gap; intervals cover the split and tie-breaking only.",
            "No protected attributes were used. Nothing can be inferred about protected groups, and the study "
            "makes no claim about workers, hours, pay, causes or any real hiring or selection decision.",
            "No universal metric: the EOG is the primary metric for this question only.",
            "Static decisions: no feedback over time.",
            "Literature at abstract level; the search was not systematic.",
        ],
        "explorer": explorer,
        "real_score": real_score,
        "display_exceptions": {
            "supplementary": "Per-cell values of the explorer are printed in research/paper/supplementary.md "
                             "(tables S2, S3 and S5), which the manuscript incorporates by reference, not in "
                             "the manuscript body. They are checked verbatim against that file.",
            "group-rate": "Group-level true positive rates (TPR_A, TPR_B) are not printed in the manuscript. "
                          "They are seed means from the same summary tables, shown to two decimals in percent; "
                          "their difference is the EOG printed in the manuscript and supplementary file.",
        },
    }


def render(data: dict) -> str:
    return json.dumps(data, indent=1, sort_keys=False, ensure_ascii=True, allow_nan=False) + "\n"


def main(argv: list[str]) -> int:
    text = render(build())
    if "--check" in argv:
        same = OUT.exists() and OUT.read_text(encoding="utf-8") == text
        print("results.json matches the export" if same else "results.json differs from the export")
        return 0 if same else 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(text)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
