<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# RIGGED project protocol

| Field | Value |
|---|---|
| Status | **FROZEN v1.1 (owner-approved 2026-11-24, G-FREEZE; pre-data amendment of round 3, owner-approved 2026-11-24, section 13).** Freeze record: `research/freeze.json`. |
| Date | 2026-11-24 |
| Protocol hash | SHA-256 of this file, in `research/freeze.json` (a file cannot contain its own hash) |
| Scope | Synthetic populations (EXP-001 to EXP-003, simulated) and one second test on a real score distribution (EXP-004, UCI Adult, CC BY 4.0). |

Runs made before the freeze (all exploratory) are labelled so in `research/experiment_journal.jsonl` and in any report. The amendments applied before the freeze are listed in section 13. Any later change is a dated deviation.

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

Ties at a threshold are broken by a seeded uniform so that realised capacity matches kappa to within one individual for P0, P1 and P2 on the fitting population. P3 (bisection on a common TPR) may miss the target count on a finite population; its tolerance is 10 individuals on the fitting population (amendment A5). The realised count and target are recorded per run as `fit_selected` and `fit_target`; a P3 run outside the tolerance is a failure with the reason recorded (section 8).

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
- Seeds: 20 per cell, fixed (amendment A2). Confirmatory seeds 0 to 19, fixed in advance. Exploratory and test runs use seeds of 1000 and above, never 0 to 19 (amendment A6).
- Sample-size rationale: with about 5,000 qualified individuals in Group A and about 3,100 in Group B at delta = 0.5, the binomial standard error of a group TPR near 0.6 is about 0.007 to 0.009, so the per-seed EOG standard deviation is roughly 0.011 (planning estimate, to be checked by the smoke run and recorded before freezing). With 20 paired seeds, the standard error of the mean paired difference is about 0.0025, so a 95% interval half-width near 0.5 pp, well below the 2 pp smallest effect of interest. Measured before the freeze (exploratory SIZING run JRN-0003, seeds 1000 to 1019, n = 20,000): per-seed SD of the P0 EOG 1.05 pp (control) and 1.25 pp (primary cell); SD of the primary paired difference 0.61 pp; bootstrap half-width 0.26 pp. The draft's conditional rule (raise to 50 seeds if the SD exceeds 0.03) is removed: the seed count is 20 (amendment A2).

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

- delta in {0, 0.5}; rho = 1; policies P0 to P3; seeds 1000 to 1002 (amendment A6; the draft used seeds 0 to 2); n = 2,000.

Full matrix (confirmatory once frozen):

- EXP-001: delta in {0, 0.25, 0.5, 1.0} x rho in {1, 1.5, 2}; policy P0; 20 seeds. 12 cells, 240 runs.
- EXP-002: same 12 cells; policies P0 to P3; 20 seeds. 960 runs (the P0 runs are shared with EXP-001 under common random numbers and are computed once).
- EXP-003: sensitivity grid (section 10); policy P0 (and P3 as a check); 20 seeds.
- EXP-004 (real data, section 13, rounds 2 and 3): cells R-sex and R-sex-random (primary), R-hours and R-hours-random (secondary) on the UCI Adult test file; policies P0 to P3; 20 seeds. 320 runs (160 before the round-3 amendment).

Compute budget: under 5 minutes of wall clock on the local laptop for the full matrix of EXP-001 to EXP-004, including reports (amendment A3; measured projection 10 to 35 s for EXP-001 to EXP-003, JRN-0003). No paid compute.

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

No real hiring, lending or justice decisions. EXP-001 to EXP-003 make no claims about real or protected groups. EXP-004 uses real census-derived records (UCI Adult) only as a source of a real score distribution and label; its primary partition is the recorded sex field (a protected attribute; owner's decision, section 13, round 3) and its secondary partition is hours-per-week below 40. Results describe these partitions of this 1994 extract under this score and these policies only; no claim is made about women or men in general, about the people in the data, about any cause, or about any real decision. No fairness metric is presented as universal. Results hold only within the stated generator assumptions.

## 13. Amendments

### Amendments before freeze (owner-approved 2026-11-24)

The owner approved these amendments ("yes for all others", 2026-11-24; approval list in the coordinator's file `owner-approvals-2026-11-24b.md`, section 7, RIGGED). Each was proposed in `research/protocol_amendment_proposals.md` (AP-001 to AP-006). They were fixed before any confirmatory run.

- **A1 (AP-006): EXP-003's sign test is reported as analytically determined.** Under the Gaussian model, the population P0 EOG of cell B-sB2 (fixed base-rate gap, s_B = 2) is -9.73 pp (numerical integration, `rigged.analytic`), opposite in sign to the primary cell. EXP-003 H2 (sign stability across s_B) is therefore decided analytically before any run. Its confirmatory run quantifies the known result and checks the implementation; it is not reported as a test with an unknown outcome. The hypotheses were finalised with the analytic values and the exploratory SIZING run available.
- **A2 (AP-002): 20 seeds.** Every confirmatory cell uses seeds 0 to 19. The conditional raise to 50 seeds is removed (section 6).
- **A3 (AP-001): a lower compute budget.** Under 5 minutes of wall clock for the full matrix including reports (section 9; EXP-001 under 1 minute).
- **A4 (AP-003): H1b is not monotone, and this is stated.** At delta = 0 the analytic P0 EOG is 0.000 pp (rho = 1), 0.177 pp (rho = 1.5) and 0.081 pp (rho = 2): not monotone in rho and far below 2 pp. EXP-001 H1b is no longer directional; the three values are reported descriptively with intervals, and no equivalence is claimed from a non-significant difference.
- **A5 (AP-005): a capacity tolerance for P3** of 10 individuals on the fitting population (section 3). The exploratory maximum was 5 individuals over 160 P3 runs at n = 20,000 (JRN-0003).
- **A6 (AP-004): exploratory seeds at 1000 and above.** Exploratory and test runs never use the confirmatory seeds 0 to 19; the smoke matrix moves to seeds 1000 to 1002 (sections 6 and 9).

Not applied (not in the approved list): AP-007 (ECE gap identical across policies) stays a reporting note: the ECE gap is reported once per cell as a property of the group-blind score, not compared between policies. AP-008 (P1 binning sensitivity) is not added; P1 keeps 20 quantile bins, and its larger per-seed spread is a stated limitation.

### Amendments before freeze (owner-approved 2026-11-24, round 2): real data

The owner approved real data for RIGGED ("Approve all", 2026-11-24; `owner-approvals-2026-11-24b.md`, section 1: "UCI Adult, CC BY 4.0. Second test on a real score distribution"). This section was written before any model was fitted and before any real-data metric was computed.

**What changes and what does not.** The synthetic study (EXP-001 to EXP-003) stays the controlled part of the project and is unchanged by the real data: no parameter of the synthetic generator is calibrated on Adult, because its parameters (delta, rho, sigma_A, kappa, p_B) are design factors, not estimates of a real quantity. DEC-003 (synthetic data only) is superseded for one new experiment, EXP-004.

**Dataset.** UCI Adult (Becker and Kohavi 1996, DOI 10.24432/C5XW20), CC BY 4.0, archive `adult.zip` (620,237 bytes, SHA-256 in `data/manifest.json`), downloaded by `scripts/download_adult.py`. It holds no direct personal identifier. The archive is under 20 MB and CC BY, so it is committed with attribution.

**Ingestion.** `rigged.adult.parse_adult` (pure function) reads `adult.data` and `adult.test`: comment lines (starting with `|`) and blank lines are skipped; a row is excluded if it does not have 15 fields, if any of age, education-num, capital-gain, capital-loss or hours-per-week is missing (`?`) or not numeric, or if the income label is not `<=50K` or `>50K` (a trailing `.` in the test file is removed). Missing values (`?`) in unused columns do not exclude a row; they are counted per column. Counts are recorded in `data/manifest.json`.

**What is fitted (calibration), with which method, on which split.** The only fitted quantity is the real score: a logistic regression of Y = 1[income > 50K] on four features, age, education-num, log(1 + capital-gain), log(1 + capital-loss), each standardised by its mean and SD on the training file. Method: unpenalised maximum likelihood by Newton-Raphson (iteratively reweighted least squares) from all-zero coefficients, stopping when the largest absolute coefficient step is below 1e-10 or after 100 iterations (non-convergence is a fit failure). Split: the official training file `adult.data` only. The fit uses no group variable and no part of `adult.test`, so it cannot use the primary contrast in any way. The score X is the fitted linear predictor (log-odds). Hours-per-week (the group variable below), sex, race, native-country, marital-status, relationship, workclass, occupation and fnlwgt are not score inputs. The fitted coefficients and standardisation constants are written into `research/experiments/EXP-004/config.json`, recorded as an exploratory journal entry, and frozen with the configs.

**What the second test is (EXP-004).** On the official test file `adult.test` (the pool), the four policies P0 to P3 are applied to the real score X with the real label Y, at kappa = 0.30, 20 calibration bins for P1 and cost ratio 1, exactly as in the synthetic study.

- Group partition (cell R-hours): Group B = hours-per-week below 40, Group A = 40 or more. This observed, non-protected partition stands in for two groups with different starting distributions. It is not a protected group, and no claim is made about workers, hours or any real decision.
- Control (cell R-random): the same individuals, with the group labels randomly permuted within each seed (same group sizes, equal starting distributions by construction). It plays the role of the delta = 0 control.
- Seeds 0 to 19. In each seed, one RNG (`SeedSequence([seed, 2])`) draws, in this order, a random permutation of the pool (first half fitting population, second half evaluation population), the tie-breaking uniforms, and the permutation of group labels for R-random. Both cells and all policies share these draws (common random numbers). Thresholds are fitted on the fitting half; metrics are computed on the evaluation half.
- Primary contrast (H1-real): D = EOG(R-hours, P0) - EOG(R-random, P0), paired by seed. Prediction from the synthetic mechanism: D is at least +2 pp (qualified members of the lower-base-rate group are selected less often under one common threshold). Disconfirmation: the 95% percentile bootstrap interval (over seeds, 10,000 resamples, RNG seed 20261124) lies entirely below +2 pp.
- Secondary: the EXP-002 incompatibility check on R-hours (does any policy meet SR, EO and PPV parity within 2 pp), paired utility differences against P0, and the base-rate gap of the partition, all descriptive.
- Uncertainty caveat: the pool is fixed, so seed-to-seed variation reflects the random split and tie-breaking, not sampling from a population. This is a stated limitation.
- The analytic cross-check does not apply (no closed-form model).
- P3 capacity tolerance in EXP-004: 30 individuals (fitting population of 8,140). The real score is tied (4,257 distinct values among 32,561 training rows), so P3's bisection cannot always hit the target count. An exploratory check on the training file only, with random partitions (seeds 1000 to 1019, no group variable, no test row), found deviations up to 19 individuals with the 10-individual tolerance of A5 exceeded in 4 of 20 fits (journal JRN-0006). The tolerance of 30 was set from that check with headroom, by the agent, and is flagged for the owner's ratification; A5's 10 individuals still applies to EXP-001 to EXP-003.
- No EXP-004 metric (including the base-rate gap of the partition on the test file) was computed before the freeze.


### Amendments before data (owner-approved 2026-11-24, round 3): EXP-004 grouping

The owner decided the EXP-004 grouping in the third round ("Approve all", 2026-11-24; coordinator's file `owner-approvals-2026-11-24c.md`, section 1, RIGGED): "The primary comparison in EXP-004 (UCI Adult) uses **sex** as the group attribute. This is the standard comparison for this dataset. Hours-per-week below 40 stays as a secondary check. Nothing has been computed on the test file. Keep it that way until the confirmatory run. The P3 capacity tolerance of 30, needed because real scores contain ties, is ratified." This is a dated pre-data amendment to the frozen v1.0 protocol: it was written before any EXP-004 metric on `adult.test` was computed, and none has been computed since. It supersedes the round-2 partition items above where they conflict; the round-2 text is kept as the record of what was frozen first.

- **R3-1. Primary group attribute: sex.** Cell R-sex: the group attribute is the `sex` column of the Adult files (values `Male` and `Female`). Rule for which value is Group B, stated before it is applied: Group B is the sex value with the lower base rate P(Y = 1) on the official training file `adult.data` (after the ingestion exclusions), so that Group B is the lower-base-rate group as in the synthetic model; the base rates are computed on `adult.data` only and recorded in an exploratory journal entry. No row of `adult.test` is used to choose it. `sex` is not a score input (the score model of round 2 is unchanged).
- **R3-2. Ingestion of the sex column.** `sex` becomes a used column, but the exclusion rules of round 2 are unchanged. A kept row whose `sex` field is neither `Male` nor `Female` stops ingestion with a schema error; that is a run failure under section 8, and the owner decides what follows. No category is imputed or merged.
- **R3-3. Control for the primary contrast.** Cell R-sex-random: the same individuals with the sex labels randomly permuted within each seed (same group sizes, equal starting distributions by construction).
- **R3-4. Secondary check: hours-per-week below 40.** Cells R-hours (Group B = hours-per-week below 40, as in round 2) and R-hours-random (the hours labels permuted within each seed; formerly called R-random). Secondary contrast: D-hours = EOG(R-hours, P0) - EOG(R-hours-random, P0), reported with the same interval method, descriptively; it does not decide H1-real.
- **R3-5. Draws.** Unchanged in kind and order: per seed, one RNG (`SeedSequence([seed, 2])`) draws a permutation of the pool, the tie uniforms and one permutation of the row indices; the random cells apply that same index permutation to their own labels (sex or hours). All four cells and all policies share these draws.
- **R3-6. Primary contrast (H1-real).** D = EOG(R-sex, P0) - EOG(R-sex-random, P0), paired by seed; prediction and disconfirmation as in round 2 (+2 pp; 95% percentile bootstrap over seeds, 10,000 resamples, RNG seed 20261124).
- **R3-7. Secondary analyses** (descriptive): the EXP-002 incompatibility check, paired utility differences against P0 and the base-rate gap, on R-sex and on R-hours.
- **R3-8. Runs.** 4 cells x 4 policies x 20 seeds = 320 runs.
- **R3-9. P3 capacity tolerance of 30 individuals in EXP-004 is ratified by the owner** (round 2, DEC-013); it applies to all four cells.
- **R3-10. Claims boundary for EXP-004.** Sex is a protected attribute in most jurisdictions, so the round-2 statement that the EXP-004 partition is non-protected no longer holds for the primary cell. Results describe this partition of this 1994 census extract under this score and these policies only. No claim is made about women or men in general, about pay, about any cause, or about any real hiring, lending or justice decision; the extract's sex field is a recorded binary category, not a statement about any person's identity. No fairness metric is presented as universal.

Result of applying the R3-1 rule (after the rule above was written; journal JRN-0007, exploratory, training file only): on `adult.data` (32,561 kept rows), P(Y = 1) is 1,179 / 10,771 = 0.1095 for `Female` and 6,662 / 21,790 = 0.3057 for `Male`. Group B = `Female`, Group A = `Male`. No row of `adult.test` was read for this, and no EXP-004 metric was computed.
