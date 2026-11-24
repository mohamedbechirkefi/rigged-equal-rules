<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# RIGGED project protocol

| Field | Value |
|---|---|
| Status | **DRAFT v0.1, not frozen.** Freezing is the owner's decision (G-FREEZE). |
| Date | 2026-11-24 |
| Protocol hash | none yet (recorded at freeze) |
| Scope | Synthetic populations only. All results are simulated. |

No run made under this draft is confirmatory. Runs before the freeze are exploratory and are labelled so in `research/experiment_journal.jsonl` and in any report.

## 1. Research question

Can equal rules yield unequal outcomes under different starting distributions?

Operational form: when one decision rule is applied identically to two synthetic groups that differ only in the distribution of a latent qualification (their "starting distribution") and, separately, in how noisily that qualification is measured, do equally qualified individuals in the two groups face different chances of selection? And which fairness criteria can alternative rules satisfy at the same time?

## 2. Formal model (synthetic data generator)

Two abstract synthetic groups g in {A, B}. They are not protected groups and stand for no real population.

For individual i in group g:

- Latent qualification: Q_i ~ Normal(mu_g, s_g^2). Primary model: s_A = s_B = 1.
- Explicit qualification label: Y_i = 1[Q_i > 0]. The base rate is pi_g = Phi(mu_g / s_g).
- Observed score: X_i = Q_i + e_i, with e_i ~ Normal(0, sigma_g^2) independent of Q_i (measurement noise).
- Group share: a fraction p_B of the population is in group B (primary p_B = 0.5).
- Capacity: a fixed overall fraction kappa of the population is selected (primary kappa = 0.30).

Parameterisation: mu_A = 0 (pi_A = 0.5), mu_B = -delta. sigma_A = 0.5, sigma_B = rho * 0.5. The starting-distribution gap is delta; the measurement-noise ratio is rho.

Common random numbers: within a seed, every cell and every policy uses the same standard-normal draws (z for Q, u for e, and the group-assignment uniforms), transformed by the cell parameters. Differences between cells and between policies within a seed are therefore paired.

Each seed draws two independent populations from separate RNG streams: a fitting population (used only to fit thresholds and calibration maps) and an evaluation population (used only to compute metrics). Nothing is tuned on the evaluation population.

## 3. Decision rules (policies)

| ID | Policy | Definition | Role |
|---|---|---|---|
| P0 | Common raw threshold | Select if X > t; one t for both groups, set on the fitting population so the overall selection rate equals kappa | **Baseline (primary comparator)**: the simplest "equal rule" |
| P1 | Common calibrated threshold | Fit a within-group calibration map r_g(x) ~ P(Y=1 given X=x, G=g) on the fitting population (20 quantile bins per group); select if r_g(X) > t, one t for both groups, overall rate kappa | Equal rule on the probability scale |
| P2 | Selection-rate parity | Group-specific thresholds so each group's selection rate equals kappa | Constrained selection (independence) |
| P3 | Equal opportunity | Group-specific thresholds chosen on the fitting population so TPR_A = TPR_B with overall rate kappa | Constrained selection (separation on Y=1) |

Ties at a threshold are broken by a seeded uniform so that realised capacity matches kappa to within one individual.

## 4. Hypotheses (project level)

Primary (EXP-001):

- **H0:** Under the common raw threshold P0, with equal measurement noise (rho = 1), the equal-opportunity gap at delta = 0.5 does not differ from the equal-distribution control (delta = 0).
- **H1 (directional):** At delta = 0.5, rho = 1, the equal-opportunity gap is positive: qualified members of Group B (the lower starting distribution) are selected less often than qualified members of Group A, by at least the smallest effect size of interest (2 percentage points), relative to the control.

Disconfirmation: H1 is contradicted if the 95% interval for the paired difference lies entirely below +2 pp (including zero or negative values).

Note on what this tests: under the stated Gaussian model, H1 follows analytically (qualified members of B are concentrated nearer the cutoff Q = 0). The simulation therefore quantifies the size of the effect, checks the implementation against numerical integration, and tests robustness when the model's assumptions are changed (EXP-003). The contribution is a transparent, reproducible quantification and an interactive explanation, not the discovery of the mechanism; see `research/literature_review.md`.

Secondary hypotheses are stated per experiment in `research/experiments/EXP-NNN/protocol.md`.

## 5. Metrics

All metrics are computed per group on the evaluation population of one run.

| Metric | Formula | Unit |
|---|---|---|
| Selection rate SR_g | selected_g / n_g | proportion |
| True positive rate TPR_g | TP_g / (TP_g + FN_g) | proportion |
| False negative rate FNR_g | 1 - TPR_g | proportion |
| False positive rate FPR_g | FP_g / (FP_g + TN_g) | proportion |
| Positive predictive value PPV_g | TP_g / (TP_g + FP_g) | proportion |
| Within-group calibration error ECE_g | sum over 10 equal-width bins b of (n_gb / n_g) * abs(mean(Y) - mean(score)), for the group-blind calibrated score fitted on the fitting population | proportion |
| Utility per capita U | (TP - c * FP) / n, cost ratio c = 1 | selections net of errors, per person |
| Accuracy | (TP + TN) / n | proportion |

**Primary metric: the equal-opportunity gap, EOG = TPR_A - TPR_B**, in percentage points (pp). Direction: positive means qualified members of Group B are selected less often.

Justification: the research question concerns "unequal outcomes" under an equal rule. A difference in selection rates alone is expected whenever base rates differ and is not by itself unequal treatment of equals. The EOG compares individuals who are equally qualified by construction (Y = 1), so it isolates the outcome inequality that the question is about. It is one criterion among several; the project does not present it as a universal fairness metric. The other gaps (SR, FPR, PPV, ECE) are secondary and are always reported.

Zero denominators: when a denominator is zero, the metric is undefined; it is stored as null with a flag `undefined_reason` and counted, never imputed.

## 6. Experimental unit, seeds and sample size

- Experimental unit: one seed, that is one pair of fitting and evaluation populations. Individuals within a seed are not independent units for the between-condition comparison (they share thresholds).
- Population size: n = 20,000 per population (about 10,000 per group at p_B = 0.5).
- Seeds: 20 per cell (at least 5 are required; 20 are cheap). Seeds 0 to 19, fixed in advance.
- Sample-size rationale: with about 5,000 qualified individuals in Group A and about 3,100 in Group B at delta = 0.5, the binomial standard error of a group TPR near 0.6 is about 0.007 to 0.009, so the per-seed EOG standard deviation is roughly 0.011 (planning estimate, to be checked by the smoke run and recorded before freezing). With 20 paired seeds, the standard error of the mean paired difference is about 0.0025, so a 95% interval half-width near 0.5 pp, well below the 2 pp smallest effect of interest. If the smoke run shows a per-seed SD above 0.03, the seed count is raised to 50 before the freeze.

## 7. Uncertainty and analysis

- Primary estimate: the mean over seeds of the paired difference D_s = EOG_s(treatment cell) - EOG_s(control cell).
- 95% interval: percentile bootstrap over seeds (10,000 resamples, bootstrap RNG seed 20261124). A t-interval over seeds is reported alongside as a check.
- Effect size: the mean paired difference in pp, plus the standardised mean paired difference (mean D / SD D).
- Raw distributions: per-seed values are exported and plotted (strip plots), not only means.
- Analytic reference: for the Gaussian model, the population TPR per group is computed by numerical integration; the simulated mean must agree within 3 bootstrap standard errors (implementation check, not a hypothesis test).
- No p-value thresholds are used as the decision rule; the decision rule is the interval versus the smallest effect of interest stated in section 4.

## 8. Exclusion and stopping rules

- No run is excluded for its result. A run is a failure only if it raises an error, fails schema validation, or yields an undefined primary metric. Failures are recorded with their reason and reported.
- Stopping: the matrix is fixed in advance; no optional stopping and no added seeds after viewing confirmatory results. If more than 10% of runs in a cell fail, the cell is halted, the failure is reported, and the protocol is amended only through a dated, justified amendment labelled exploratory.

## 9. Matrices

Smoke matrix (exploratory; validates the pipeline and the SD estimate):

- delta in {0, 0.5}; rho = 1; policies P0 to P3; seeds 0 to 2; n = 2,000.

Full matrix (confirmatory once frozen):

- EXP-001: delta in {0, 0.25, 0.5, 1.0} x rho in {1, 1.5, 2}; policy P0; 20 seeds. 12 cells, 240 runs.
- EXP-002: same 12 cells; policies P0 to P3; 20 seeds. 960 runs (the P0 runs are shared with EXP-001 under common random numbers and are computed once).
- EXP-003: sensitivity grid (section 10); policy P0 (and P3 as a check); 20 seeds.

Compute budget: under 30 minutes of wall-clock on the local laptop for the full matrix (planning estimate, to be measured by the smoke run). No paid compute.

## 10. Sensitivity analysis that could invalidate the main interpretation (EXP-003)

The main interpretation would be "a lower starting distribution (lower base rate) produces a lower TPR for qualified individuals under an equal rule". This interpretation is invalid if the gap is driven by the shape of the qualification distribution near the cutoff rather than by the base-rate difference. EXP-003 tests this by:

- holding base rates equal (pi_A = pi_B) while changing the latent dispersion s_B in {0.5, 1, 2} (with mu_B adjusted so that pi_B = 0.5), and
- holding the base-rate gap fixed (pi_B = Phi(-0.5)) while changing s_B so that the qualified mass of Group B lies farther from the cutoff,
- replacing the Gaussian latent distribution with a Student t (3 degrees of freedom) and a skewed (log-normal shifted) distribution with matched base rates,
- varying capacity kappa in {0.1, 0.3, 0.5} and group share p_B in {0.2, 0.5}.

If a non-zero EOG appears at equal base rates, or if the EOG reverses sign at the same base-rate gap, the base-rate interpretation is refuted and must be replaced by a distribution-shape interpretation. This outcome is reported whichever way it falls.

## 11. Confounders and competing explanations

- Measurement noise (rho) versus starting distribution (delta): separated by the factorial design.
- Threshold placement (kappa): varied in EXP-003.
- Calibration-fit error in P1 (finite bins): checked against the analytic posterior.
- Finite-sample threshold fitting in P2 and P3: the fitting and evaluation populations are separate, so overfitting shows up as residual gaps on the evaluation population.

## 12. Claims boundary

No real hiring, lending or justice decisions. No claims about real or protected groups. No fairness metric is presented as universal. Results hold only within the stated generator assumptions.

## 13. Amendments

None. Any amendment after the freeze will be listed here with date, reason and whether it is exploratory.
