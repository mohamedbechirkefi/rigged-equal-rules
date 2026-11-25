# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Build research/publication/artifact_manifest.json (master prompt 11.5).

One entry per quantitative artifact of the manuscript, supplementary file and experiment reports
(tables, figures, exploratory tables): experiment ID, run IDs (pattern and count), metric definition,
result path, generator script, config and protocol hashes, code revision and file SHA-256. Line-level
tracing of every decimal number is in research/publication/number_trace.csv (scripts/m4_evidence_audit.py).

Usage: python3 scripts/build_artifact_manifest.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEN = "src/rigged/report.py (python -m rigged.cli report), run by scripts/run_confirmatory.sh"
EOG = "EOG = TPR_A - TPR_B on the evaluation population (protocol section 5), pp"
GAPS = "Group A minus group B of SR, TPR (EOG), FPR, PPV and ECE (protocol section 5); seed means and 95% percentile bootstrap over seeds (section 7)"


def sha(p: str) -> str:
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def prov(e: str) -> dict:
    return json.loads((ROOT / f"results/{e}/provenance.json").read_text(encoding="utf-8"))


def entry(aid, kind, e, run_ids, metric, path, gen, used_in, policies="", note=""):
    p = prov(e) if (ROOT / f"results/{e}/provenance.json").is_file() and "exploratory" not in path else None
    d = {"artifact_id": aid, "kind": kind, "experiment_id": e, "run_ids": run_ids, "metric_definition": metric,
         "result_path": path, "generator_script": gen, "used_in": used_in,
         "config_hash": f"sha256:{p['config_sha256']}" if p else None,
         "protocol_hash": f"sha256:{p['experiment_protocol_sha256']}" if p else None,
         "project_protocol_hash": f"sha256:{p['project_protocol_sha256']}" if p else None,
         "code_revision": p["git_revision"] if p else None,
         "sha256": sha(path) if (ROOT / path).is_file() else None}
    if note:
        d["note"] = note
    return d


def main() -> int:
    ex = json.loads((ROOT / "results/exploratory/m4-confounders/manifest.json").read_text(encoding="utf-8"))
    E = []
    E.append(entry("TAB-001", "table", "EXP-001", "RUN-EXP-001-{d0.50-r1.00,d0.00-r1.00}-P0-s{0..19} (40 runs)",
                   "Paired difference over seeds of each gap, treatment minus control; " + GAPS,
                   "results/EXP-001/tables/contrasts.csv", GEN, ["manuscript Table 1, abstract, section 5.1", "EXP-001 report section 7", "CLM-001"]))
    E.append(entry("TAB-002", "table", "EXP-001", "RUN-EXP-001-<cell>-P0-s{0..19} (240 runs)", EOG + "; seed means, 95% bootstrap",
                   "results/EXP-001/tables/summary.csv", GEN, ["manuscript Table 2", "EXP-001 report section 7", "CLM-002"]))
    E.append(entry("TAB-002a", "table", "EXP-001", "240 runs", "Simulated P0 seed mean against population value (numerical integration); z = difference / bootstrap SE",
                   "results/EXP-001/tables/analytic_check.csv", GEN, ["manuscript sections 5.1 and 3", "CLM-003"]))
    E.append(entry("FIG-001", "figure", "EXP-001", "240 runs", "Per-seed P0 EOG by cell (strip plot)",
                   "results/EXP-001/figures/XFIG-EXP-001-01-eog.svg", GEN, ["manuscript Figure 1"],
                   note="Identical copy at research/experiments/EXP-001/figures/ (SHA-256 checked)"))
    E.append(entry("TAB-003", "table", "EXP-002", "RUN-EXP-002-<cell>-<P0..P3>-s{0..19} (960 runs)", GAPS,
                   "results/EXP-002/tables/summary.csv", GEN, ["manuscript Table 3, supplementary S2", "EXP-002 report", "CLM-004", "CLM-016"]))
    E.append(entry("TAB-003a", "table", "EXP-002", "960 runs", "Utility per capita (TP - c FP)/n, c = 1, policy minus P0, paired over seeds",
                   "results/EXP-002/tables/policy_vs_p0.csv", GEN, ["manuscript section 5.2, supplementary S3", "CLM-005"]))
    E.append(entry("FIG-002", "figure", "EXP-002", "960 runs", "Per-seed EOG by cell and policy (strip plot)",
                   "results/EXP-002/figures/XFIG-EXP-002-01-eog.svg", GEN, ["manuscript Figure 2"]))
    E.append(entry("TAB-004", "table", "EXP-003", "RUN-EXP-003-<cell>-<P0|P3>-s{0..19} (420 runs)", EOG + "; seed means, 95% bootstrap",
                   "results/EXP-003/tables/summary.csv", GEN, ["manuscript Table 4", "EXP-003 report", "CLM-006 to CLM-010"]))
    E.append(entry("TAB-004a", "table", "EXP-003", "300 P0 runs", "Implementation check: simulated P0 seed mean within 3 bootstrap SE of the population value",
                   "results/EXP-003/tables/analytic_check.csv", GEN, ["manuscript Table 4 and section 5.3", "CLM-011"]))
    E.append(entry("FIG-003", "figure", "EXP-003", "420 runs", "Per-seed P0 EOG by cell (strip plot)",
                   "results/EXP-003/figures/XFIG-EXP-003-01-eog.svg", GEN, ["manuscript Figure 3"]))
    E.append(entry("TAB-005", "table", "EXP-004", "RUN-EXP-004-{R-hours,R-hours-random}-P0-s{0..19} (40 runs)",
                   "D = EOG(R-hours, P0) - EOG(R-hours-random, P0), paired by seed; " + GAPS,
                   "results/EXP-004/tables/contrasts.csv", GEN, ["abstract, manuscript section 5.4", "CLM-012"]))
    E.append(entry("TAB-005a", "table", "EXP-004", "RUN-EXP-004-<cell>-<P0..P3>-s{0..19} (160 runs)", GAPS,
                   "results/EXP-004/tables/summary.csv", GEN, ["manuscript Table 5, supplementary S5", "CLM-013", "CLM-017"]))
    E.append(entry("TAB-005b", "table", "EXP-004", "160 runs", "Utility per capita, policy minus P0, paired over seeds",
                   "results/EXP-004/tables/policy_vs_p0.csv", GEN, ["manuscript section 5.4", "CLM-014"]))
    E.append(entry("TAB-005c", "table", "EXP-004", "RUN-EXP-004-<cell>-P0-s{0..19} (40 runs)",
                   "Evaluation-half base rate P(Y = 1) per group and gap A minus B; Group B share", "results/EXP-004/tables/base_rate_gap.csv",
                   "scripts/exp004_base_rates.py (written after the run, DEC-020)", ["manuscript section 5.4", "CLM-015"]))
    E.append(entry("FIG-004", "figure", "EXP-004", "160 runs", "Per-seed P0 EOG, R-hours and R-hours-random (strip plot)",
                   "results/EXP-004/figures/XFIG-EXP-004-01-eog.svg", GEN, ["manuscript Figure 4"]))
    E.append(entry("TAB-006", "table", "EXP-001 to EXP-004", "all 1,780 runs", "Expected versus observed (verdicts under the frozen rules)",
                   "research/publication/interpretation.md", "hand-written from TAB-001 to TAB-005", ["manuscript Table 6"],
                   note="Every number in it appears in TAB-001 to TAB-005c (number_trace.csv)"))
    for aid, path, jrn, metric, used in (
        ("XTAB-001", "results/exploratory/m4-confounders/p1_exact_posterior.csv", "JRN-0015",
         "P1 population gaps with the exact Gaussian posterior (numerical integration) against binned simulated P1", ["manuscript section 5.2, supplementary S4", "CLM-018"]),
        ("XTAB-002", "results/exploratory/m4-confounders/exp004_score_by_group.csv", "JRN-0016",
         "Full-pool score quantiles, shares above the pool p70, calibration in the large, by hours partition", ["manuscript section 5.4, supplementary S7", "CLM-019"]),
        ("XTAB-003", "results/exploratory/m4-confounders/exp004_calibration_by_decile.csv", "JRN-0016",
         "Observed rate and mean logistic probability by pool-wide score decile and group", ["supplementary S7", "CLM-019"]),
        ("XTAB-004", "results/exploratory/m4-confounders/exp004_features_by_label.csv", "JRN-0016",
         "Score inputs by group and label", ["supplementary S7", "interpretation.md"])):
        d = entry(aid, "table (EXPLORATORY)", "EXP-002" if jrn == "JRN-0015" else "EXP-004", f"none (no runs; {jrn})", metric, path,
                  "scripts/m4_exploratory.py", used)
        d["code_revision"] = ex["code_revision_at_run"]
        d["code_revision_note"] = "script uncommitted at run time; committed unchanged in the M4 commit"
        d["config_hash"] = None
        d["inputs_sha256"] = ex["inputs"]
        E.append(d)
    d = entry("XTAB-005", "table (EXPLORATORY)", "EXP-003", "RUN-EXP-003-<cell>-<P0|P3>-s{1000..1019} (420 exploratory runs; JRN-0014)",
              "Implementation check on exploratory seeds", "results/exploratory/exp-003-x/tables/analytic_check.csv", GEN,
              ["manuscript section 5.3", "CLM-011"])
    d["config_hash"] = d["protocol_hash"] = d["project_protocol_hash"] = None
    d["code_revision"] = "b455d59294ea98e2b050ef30f20bc74b7993969e"
    E.append(d)
    out = {"schema_version": "1.0.0", "updated": "2026-11-25", "status": "M4: complete for the manuscript, supplementary and experiment reports",
           "line_level_trace": "research/publication/number_trace.csv (every decimal number in the manuscript, supplementary, reports and claims register, matched to a committed table)",
           "entry_fields": ["artifact_id", "kind", "experiment_id", "run_ids", "metric_definition", "result_path", "generator_script",
                            "used_in", "config_hash", "protocol_hash", "project_protocol_hash", "code_revision", "sha256"],
           "entries": E}
    (ROOT / "research/publication/artifact_manifest.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(f"{len(E)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
