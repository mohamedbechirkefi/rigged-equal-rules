<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# EXP-003 report: sensitivity analysis (base rate versus distribution shape)

| Field | Value |
|---|---|
| Experiment | EXP-003 |
| Date | 2026-11-25 |
| Version | 1.0 |
| Status | Complete (420 of 420 runs ok). Confirmatory, simulated data. Implementation check failed on 4 of 60 comparisons (deviation DEC-019; the owner decided on 2026-11-25 that it is a disclosed limitation on H4, with no rerun, DEC-021). |
| Authorship | Mohamed Bechir Kefi (C3). AI assistant disclosed as a research and development assistant, not an author. |
| Protocol | `research/experiments/EXP-003/protocol.md`, FROZEN v1.0, SHA-256 7d6335cf96cb0b856eeffc6f2bfc264425df11c008f9984147d313609a116214 |
| Config | SHA-256 b22c17b436cf9fc0fa4ad2e083f0de2dbac804557001410045e027c71ff2c24a |
| Code revision | b455d59294ea98e2b050ef30f20bc74b7993969e (tree clean) |
| Results | `results/EXP-003/` (results.json SHA-256 ad64b5ebbf349eced4f93ea51c57f7694c4412ab7dcbab3c213dd3175167f3e0) |

## 1. Executive summary

**Question.** Is EXP-001's gap a base-rate effect or an effect of the shape of the qualification distribution near the cutoff?

**Outcome.**
- At equal base rates, changing only Group B's dispersion gives EOGs of 19.44 pp (s_B 0.5) and -22.50 pp (s_B 2). H0 is rejected: shape matters.
- At a fixed base-rate gap, the EOG reverses sign at s_B = 2 (-9.56 pp), as analytically determined before the run (A1).
- The sign of the primary cell is kept under Student t3 and log-normal shapes (H3) and across six operating points (H4).

The base-rate interpretation, "a lower base rate lowers TPR", is refuted as stated. It must be narrowed to "the distribution of qualified individuals near the cutoff".

**Caveat.** The frozen implementation check passed only 56 of 60 comparisons. Four failures are in two grid-D cells, so H4 carries a caveat (DEC-019). The owner decided on 2026-11-25 that this is a disclosed limitation on H4; nothing is rerun (DEC-021).

## 2. Why this experiment exists

If the gap were a base-rate effect, equal base rates would give no gap, and a fixed base-rate gap would give a gap of stable sign. A gap at equal base rates, or a sign reversal at a fixed base-rate gap, refutes the base-rate interpretation (protocol section 2). The experiment was designed so that its result could contradict EXP-001's reading.

## 3. Hypotheses

- H0 (base-rate sufficiency): with pi_A = pi_B = 0.5 and s_B in {0.5, 1, 2}, EOG stays within +/- 2 pp.
- H1 (non-directional): EOG lies outside +/- 2 pp for at least one s_B != 1 at equal base rates.
- H2 (sign stability) at pi_B = Phi(-0.5), with s_B in {0.5, 1, 2}. This was analytically determined before the run: the population EOG of B-sB2 is -9.73 pp, a sign reversal.
- H3: the sign of the primary cell is kept under Student t3 and shifted log-normal latent families with matched base rates.
- H4: the sign is unchanged for kappa in {0.1, 0.3, 0.5} and p_B in {0.2, 0.5} at delta = 0.5, rho = 1.

## 4. Methodology

- **Grids:**
  - A: equal base rates, s_B varied; 3 cells.
  - B: fixed base-rate gap, s_B varied; 3 cells.
  - C: latent family; 3 cells.
  - D: kappa x p_B; 6 cells.
- **Runs:** P0 on all 15 cells (300 runs); P3 on grids A and B (120 runs). Seeds 0 to 19; n = 20,000.
- **Statistics:** percentile bootstrap over seeds.
- **Analytic check:** population values by numerical integration, including the non-Gaussian densities.
- **Environment:** as EXP-001.

## 5. Implementation verification

**Frozen check** (protocol section 7: simulated mean within 3 bootstrap SE of the population value): **56 of 60 pass.** The four failures (`results/EXP-003/tables/analytic_check.csv`):

| Cell | Metric | Population (pp) | Simulated (pp) | Bootstrap SE (pp) | z |
|---|---|---|---|---|---|
| D-k0.1-pB0.5 | EOG | 7.49 | 6.95 | 0.17 | -3.08 |
| D-k0.1-pB0.5 | SR gap | 7.57 | 7.27 | 0.07 | -4.07 |
| D-k0.5-pB0.2 | FPR gap | 4.66 | 5.29 | 0.13 | 5.05 |
| D-k0.5-pB0.2 | PPV gap | 9.34 | 8.63 | 0.21 | -3.38 |

**Exploratory diagnosis (JRN-0014).** It ran after the failure, changed nothing, and does not alter the confirmatory outcome:
- The same frozen matrix on exploratory seeds 1000 to 1019 passed 60 of 60. The largest |z| in the two flagged cells was 1.72.
- All cells share the same 20 seeds under common random numbers, so the 60 comparisons are correlated.
- The pattern suggests a realisation of the confirmatory seed set rather than a code fault. This is not proven.

**Other checks.** All other EOG comparisons pass, including grid C (t3 population 2.43 pp, simulated 2.29 pp; log-normal 1.23 pp, simulated 1.43 pp). No run failed, and no metric was undefined.

## 6. Execution record

- **Command:** `scripts/run_confirmatory.sh EXP-003`.
- **Time:** 2026-11-25, 00:15:34Z to 00:15:37Z UTC; wall clock 2.56 s; exit 0.
- **Resources:** peak RSS 79.6 MiB. Mean runtime per run: P0 0.006 s, P3 0.007 s.
- **Runs:** 420 planned, 420 ok, 0 failed. Config hashes are in `provenance.json`.
- **Deviation DEC-019:** the implementation check failure above. Nothing was changed or rerun as confirmatory. Owner decision (2026-11-25, "Approve all recommendations, push then next", item 2): a disclosed limitation on H4, no rerun (DEC-021).
- **Prior knowledge:** cells B-sB2, C-student_t3, C-lognormal and D-k0.1-pB0.2 were seen exploratorily before the freeze (C4).

## 7. Results

P0 EOG (seed means in pp, 95% bootstrap; `results/EXP-003/tables/summary.csv`):

| Grid | Cell | EOG | Population value |
|---|---|---|---|
| A (pi equal) | s_B 0.5 | 19.44 [18.98, 19.89] | 19.45 |
| A | s_B 1 | -0.09 [-0.60, 0.38] | 0 |
| A | s_B 2 | -22.50 [-22.93, -22.06] | -22.28 |
| B (pi_B = Phi(-0.5)) | s_B 0.5 | 22.10 [21.68, 22.56] | 22.13 |
| B | s_B 1 | 6.50 [6.12, 6.89] | 6.31 |
| B | s_B 2 | -9.56 [-10.01, -9.12] | -9.73 |
| C | Gaussian | 6.50 [6.12, 6.89] | 6.31 |
| C | Student t3 | 2.29 [1.87, 2.69] | 2.43 |
| C | shifted log-normal | 1.43 [1.07, 1.81] | 1.23 |
| D | kappa 0.1, p_B 0.2 | 6.40 [5.86, 6.87] | 6.84 |
| D | kappa 0.1, p_B 0.5 | 6.95 [6.63, 7.31] | 7.49 (check failed) |
| D | kappa 0.3, p_B 0.2 | 6.90 [6.37, 7.44] | 7.22 |
| D | kappa 0.3, p_B 0.5 | 6.50 [6.12, 6.89] | 6.31 |
| D | kappa 0.5, p_B 0.2 | 2.82 [2.40, 3.27] | 2.96 |
| D | kappa 0.5, p_B 0.5 | 2.09 [1.85, 2.32] | 2.02 |

P3 EOG on grids A and B, by cell:
- A-sB0.5: 0.14 [-0.49, 0.76]
- A-sB1: -0.18 [-0.85, 0.49]
- A-sB2: -0.25 [-0.87, 0.36]
- B-sB0.5: 0.08 [-0.53, 0.71]
- B-sB1: 0.12 [-0.52, 0.74]
- B-sB2: 0.31 [-0.20, 0.85]

Strip plot: `figures/XFIG-EXP-003-01-eog.svg`.

## 8. Interpretation and verdicts

- **H0 rejected, H1 supported.** At equal base rates, the EOG is far outside +/- 2 pp in both directions. A base-rate difference is not necessary for an equal-opportunity gap in this model.
- **H2: sign reversal, analytically determined.** At the same base-rate gap, the EOG is +22.10, +6.50 and -9.56 pp as s_B rises. This refutes the base-rate interpretation for the B-sB2 configuration. The outcome was known in advance (A1); the run quantifies it and confirms the implementation in grid B (all checks pass).
- **H3 supported (sign).** Under t3 and log-normal shapes the EOG stays positive but is smaller (2.29 and 1.43 pp against 6.50 pp). The magnitude depends on the shape.
- **H4 supported (sign), with a caveat.** All six grid-D cells are positive, from 2.09 to 6.95 pp. Two of those cells failed the implementation check, so the magnitudes there are not confirmed at the frozen standard. The signs are far from zero in every cell.
- **P3** closes the gap in every grid A and B cell. This is consistent with its construction.
- **Combined reading.** The gap under one threshold is driven by where the qualified members of each group sit relative to the cutoff. A base-rate difference is neither necessary (grid A) nor sufficient for a fixed sign (grid B). EXP-001's mechanism statement should be narrowed accordingly.

## 9. Threats to validity

- Results are simulated, for two groups and one score.
- The check failure is not explained; the owner accepted it as a disclosed limitation on H4 (DEC-019, DEC-021).
- H2 was known before the run.
- Grid C uses one parameterisation per family.
- The 60 check comparisons are correlated through common random numbers.

## 10. Conclusion and next experiment

The distribution-shape interpretation replaces the base-rate interpretation within this model. The next step is EXP-004, the real-data test. The owner decided that DEC-019 stands as a disclosed limitation on H4 (DEC-021).

## 11. Reproduction

See `research/experiments/EXP-003/reproduction.md`.
