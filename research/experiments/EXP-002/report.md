<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# EXP-002 report: comparing equal and constrained rules; incompatible criteria

| Field | Value |
|---|---|
| Experiment | EXP-002 |
| Date | 2026-11-25 |
| Version | 1.0 |
| Status | Complete (960 of 960 runs ok). Confirmatory, simulated data. |
| Authorship | Mohamed Bechir Kefi, independent researcher (C3; author line approved by the owner on 2026-11-26). AI assistant disclosed as a research and development assistant, not an author. |
| Protocol | `research/experiments/EXP-002/protocol.md`, FROZEN v1.0, SHA-256 263ede02caaa43102ff0aee8b2e23653beb968d857632c9e87c6cf4175f2e875 |
| Config | SHA-256 150d6fffba5d2a8ac56cf1c2e187ae48048fe5167ea4050cf891e9eb380ed30e |
| Code revision | b455d59294ea98e2b050ef30f20bc74b7993969e (tree clean) |
| Results | `results/EXP-002/` (results.json SHA-256 c1af46ad572af0f083091d669d83e1720e64941ef57a960a8ee59c53dfc369b3) |

## 1. Executive summary

**Question.** At a fixed capacity, can any of four rules meet selection-rate parity, equal opportunity and predictive parity together when starting distributions differ? The rules are:

- P0: common raw threshold;
- P1: common calibrated threshold;
- P2: selection-rate parity;
- P3: equal opportunity.

**Outcome.** At delta = 0.5, rho = 1, no policy meets all three criteria within 2 pp; each fails at least one by more than 9 pp. At the delta = 0 control all four meet them. H1 is supported. P2 and P3 have lower utility than P0, so H2 is supported.

**Caveat.** The outcome is simulated, and the incompatibility is expected from theory (kleinberg2016, chouldechova2017).

## 2. Rationale and literature

When base rates differ, a classifier generally cannot equalise selection rates, error rates and PPV at once (kleinberg2016, chouldechova2017, pleiss2017). Group-specific thresholds enforce one constraint at a utility cost (corbettdavies2017). Abstracts were verified on 2026-11-24. This experiment measures the size of each violation and the utility cost in one controlled model.

## 3. Hypotheses

- H0: at delta = 0.5, rho = 1 at least one policy meets all three criteria within 2 pp. This means |SR gap|, |EOG| and |PPV gap| are each at most 2 pp on the seed mean, with the 95% interval inside +/- 2 pp.
- H1: no policy meets all three at delta = 0.5, rho = 1, while all four meet them at delta = 0, rho = 1.
- H2: utility per capita of P2 and P3 is lower than P0's at delta = 0.5 (paired over seeds). P1 is reported without a directional prediction.
- Contradiction: some policy meets all three at delta = 0.5, or the control fails.

## 4. Methodology

- **Cells:** the same 12 cells as EXP-001.
- **Policies:** P0 to P3, fitted on the fitting population and evaluated on the evaluation population.
  - P1 uses 20 quantile calibration bins.
  - P3 has a capacity tolerance of 10 individuals (A5).
- **Seeds and runs:** seeds 0 to 19; n = 20,000; 960 runs.
- **Intervals:** percentile bootstrap over seeds.
- **Environment:** as EXP-001.

## 5. Implementation verification

- **P0 analytic check:** 48 of 48 within 3 bootstrap SE (`results/EXP-002/tables/analytic_check.csv`).
- **P0 runs:** identical to EXP-001's on every summary field except runtime.
- **P3:** no capacity-tolerance failure. No undefined metric.
- **Test suite:** 116 passed before the run.

## 6. Execution record

- **Command:** `scripts/run_confirmatory.sh EXP-002`.
- **Time:** 2026-11-25, 00:15:13Z to 00:15:21Z UTC; wall clock 6.97 s; exit 0.
- **Resources:** peak RSS 90.2 MiB. Mean runtime per run: P0 0.006 s, P1 0.010 s, P2 0.006 s, P3 0.007 s.
- **Runs:** 960 planned, 960 ok, 0 failed.
- **Run IDs and config hashes:** in `results/EXP-002/provenance.json`.
- **Deviation (DEC-020):** the P0 runs were recomputed here rather than shared with EXP-001; the results are identical.
- **Owner decision:** not applicable.

## 7. Results

**Primary cell d0.50-r1.00** (seed means in pp, 95% bootstrap; `results/EXP-002/tables/summary.csv`):

| Policy | SR gap | EOG | PPV gap | FPR gap | All three within 2 pp |
|---|---|---|---|---|---|
| P0 | 15.37 [15.09, 15.64] | 6.50 [6.12, 6.89] | 4.56 [4.19, 4.97] | 1.74 [1.54, 1.94] | no (SR, EO, PPV) |
| P1 | 20.02 [19.65, 20.39] | 14.89 [14.30, 15.45] | 1.00 [0.55, 1.45] | 4.17 [3.93, 4.42] | no (SR, EO) |
| P2 | -0.14 [-0.60, 0.35] | -19.99 [-20.63, -19.35] | 15.94 [15.50, 16.40] | -6.30 [-6.58, -6.02] | no (EO, PPV) |
| P3 | 11.74 [11.33, 12.16] | 0.12 [-0.52, 0.74] | 7.34 [6.90, 7.76] | -0.16 [-0.37, 0.05] | no (SR, PPV) |

**Control d0.00-r1.00:**

| Policy | SR gap | EOG | PPV gap | All three within 2 pp |
|---|---|---|---|---|
| P0 | -0.10 [-0.46, 0.26] | -0.09 [-0.60, 0.38] | -0.25 [-0.44, -0.07] | yes |
| P1 | -0.13 [-0.59, 0.36] | -0.14 [-0.87, 0.61] | -0.24 [-0.50, 0.00] | yes |
| P2 | -0.14 [-0.60, 0.35] | -0.16 [-0.88, 0.59] | -0.24 [-0.51, 0.01] | yes |
| P3 | -0.16 [-0.61, 0.31] | -0.18 [-0.85, 0.49] | -0.21 [-0.44, 0.01] | yes |

**Utility per capita relative to P0** (paired, 95% bootstrap; `results/EXP-002/tables/policy_vs_p0.csv`):

| Cell | P1 | P2 | P3 |
|---|---|---|---|
| d0.50-r1.00 | +0.00058 [0.00010, 0.00108] | -0.01773 [-0.01859, -0.01688] | -0.00215 [-0.00249, -0.00181] |
| d0.00-r1.00 | -0.00002 [-0.00016, 0.00012] | -0.00001 [-0.00014, 0.00013] | -0.00005 [-0.00019, 0.00009] |

P0's mean utility per capita is 0.2455 at d0.50-r1.00 and 0.2763 at d0.00-r1.00.

**Other values.**

- The ECE gap is 0.14 [-0.13, 0.41] pp at d0.50-r1.00 for every policy. It is a property of the group-blind score (AP-007).
- Every cell and policy is in `summary.csv`; the strip plot is `figures/XFIG-EXP-002-01-eog.svg`.

![Per-seed equal-opportunity gap (EOG, percentage points) by cell and policy, EXP-002, 20 seeds per column, simulated. The red bar is the seed mean; the dashed line marks zero. With 48 columns the axis labels are small; every value is in `summary.csv`.](figures/XFIG-EXP-002-01-eog.svg)

**Tolerance sensitivity** (protocol section 10; read from the intervals above, with no new computation):

- At 5 pp, no policy meets all three at d0.50-r1.00. The smallest worst violation is P3's SR gap of 11.74 pp.
- At 1 pp, all four still meet all three at the control. Every control interval lies within [-0.88, 0.61].
- The verdict is the same at 1, 2 and 5 pp.

## 8. Interpretation

**H1 is supported.** Each rule fixes at most one criterion, and the others widen:

- P2 equalises selection rates but moves the EOG to -19.99 pp.
- P3 closes the EOG (0.12 pp) but leaves an SR gap of 11.74 pp and a PPV gap of 7.34 pp.
- P1 brings PPV parity within 2 pp (1.00 pp) but more than doubles P0's EOG (14.89 against 6.50 pp).

At the control every policy meets every criterion. This rules out finite-sample fitting as the cause of the failures at delta = 0.5.

**H2 is supported.** P2 costs 0.0177 and P3 0.0021 utility per capita against P0. P1 gains 0.0006, a small amount whose interval excludes 0.

All of this is consistent with the impossibility results cited; it is a measurement, not a new theorem.

## 9. Threats to validity

- **Simulation:** results hold for the simulated Gaussian model with cost ratio 1 only.
- **P1:** its per-seed spread is larger than P0's (AP-008, not applied).
- **Tolerance:** the 2 pp tolerance is a choice; sensitivity at 1 and 5 pp does not change the verdict.
- **Fairness metrics:** no criterion is presented as universal.

## 10. Conclusion and next experiment

In this model, once starting distributions differ, no rule tested satisfies the three parity criteria together, and constrained rules cost utility. EXP-003 tests whether the gap reflects base rates or distribution shape.

## 11. Reproduction

See `research/experiments/EXP-002/reproduction.md`.

## 12. M4 addendum (2026-11-25, exploratory; the verdicts above are unchanged)

- **P1 calibration-fit error (protocol section 11), JRN-0015.** With the exact Gaussian posterior in place of the 20-bin map, P1's population EOG at d0.50-r1.00 is 13.04 pp, outside the binned interval [14.30, 15.45]. Its PPV gap is 2.10 pp instead of 1.00 pp. The exact value is outside the binned interval in 5 of 12 cells. H1 is unchanged, because P1 still fails SR and EO parity. The statement "P1 brings PPV parity within 2 pp" in section 8 holds for the 20-bin implementation only. Source: `results/exploratory/m4-confounders/p1_exact_posterior.csv`; manuscript section 5.2 and supplementary S4.
- **Evidence audit.** All 960 runs and all summary and contrast values were re-derived from `results.json` without discrepancy (`research/publication/evidence_audit.md`).
