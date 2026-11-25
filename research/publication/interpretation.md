<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# M4 interpretation: competing explanations, sensitivity and expected versus observed

| Field | Value |
|---|---|
| Date | 2026-11-25 |
| Milestone | M4 (master prompt 11.4 to 11.6) |
| Inputs | Committed confirmatory results at revision b455d59 (`results/EXP-001/` to `results/EXP-004/`); exploratory checks JRN-0014, JRN-0015 and JRN-0016 |
| New computation | Two cheap exploratory checks (JRN-0015, JRN-0016; `results/exploratory/m4-confounders/`, `scripts/m4_exploratory.py`, one process, 8.6 s). They are labelled exploratory and never change or replace a frozen verdict. |

## 1. Method of this review

For each confirmatory conclusion, the competing explanations named in the protocols (project protocol sections 10 and 11; EXP-001 section 4; EXP-002 section 3; EXP-003 section 2; EXP-004 sections 2 and 6) are listed, and each is marked as addressed by a committed result, addressed by an exploratory check, or not addressed. Committed results were used first. New computation was added only where a named explanation had no committed evidence and a check cost seconds.

## 2. Competing explanations, conclusion by conclusion

### 2.1 EXP-001: one common threshold gives a positive equal-opportunity gap (H1 supported, D = 6.59 [6.20, 6.97] pp)

| Competing explanation (source) | Evidence | Status |
|---|---|---|
| The gap comes from measurement noise, not the starting distribution (EXP-001 section 4; protocol section 11) | Factorial design: at rho = 1 (equal noise) the gap is 6.50 pp at delta = 0.5 against -0.09 pp at delta = 0; at delta = 0 the gap stays within [-0.60, 0.62] pp for every rho (`results/EXP-001/tables/summary.csv`). | Addressed (committed). Noise widens the gap (9.20 pp at delta 0.5, rho 2) but does not create it at delta = 0 under P0. |
| The gap is an artefact of threshold fitting (EXP-001 section 4) | Separate fitting and evaluation populations; 48 of 48 analytic comparisons within 3 bootstrap SE; primary cell population value 6.31 pp inside the interval (`analytic_check.csv`). | Addressed (committed). |
| The gap reflects distribution shape near the cutoff, not the base rate (EXP-001 section 4; protocol section 10) | EXP-003 grids A and B. | Addressed, and it holds: the base-rate wording is too broad (section 2.3). |
| Pre-knowledge: the result was analytically implied and exploratory values were seen before the freeze (freeze record C4) | Disclosed. | Not removable. The result is a quantification and an implementation check, not a test of an unknown outcome. |

### 2.2 EXP-002: no rule meets the three parity criteria at delta = 0.5; constrained rules cost utility (H1 and H2 supported)

| Competing explanation (source) | Evidence | Status |
|---|---|---|
| Failures are due to finite-sample fitting, not incompatibility (EXP-002 section 3) | At the delta = 0 control all four policies meet all three criteria; every control interval lies within [-0.88, 0.61] pp (`results/EXP-002/tables/summary.csv`). | Addressed (committed). |
| Calibration-fit error in P1 from 20 finite bins (protocol section 11: "checked against the analytic posterior") | Committed: a unit test compares the fitted bin rates with the analytic posterior (`tests/test_analytic.py`). It does not give a policy-level value. Exploratory JRN-0015: P1 recomputed with the exact Gaussian posterior by numerical integration (infinite n, no bins). | Addressed by an exploratory check, with a finding (below). |
| The verdict depends on the 2 pp tolerance (EXP-002 section 10) | Read from the committed intervals: same verdict at 1, 2 and 5 pp. | Addressed (committed). |

**JRN-0015 finding (exploratory).** With the exact posterior, P1's population EOG at the primary cell is 13.04 pp, against the binned simulated 14.89 [14.30, 15.45] pp. The exact value lies outside the simulated interval in 5 of the 12 cells, with differences from -3.86 to +7.67 pp (largest at d1.00-r1.00: 22.25 against 29.91 pp). Under the exact posterior, P1's PPV gap at the primary cell is 2.10 pp, against 1.00 pp with 20 bins. Consequences:

- The EXP-002 H1 verdict is unchanged: with the exact posterior, P1 still fails selection-rate parity (19.05 pp) and equal opportunity (13.04 pp).
- The statement "P1 brings PPV parity within 2 pp" depends on the 20-bin implementation and is qualified in the manuscript; with the exact posterior the PPV gap is just above 2 pp.
- The statement "P1 more than doubles P0's EOG" holds with the exact posterior too (13.04 against a P0 population value of 6.31 pp).
- P1's magnitudes are partly a property of the 20-bin map (AP-008, not applied). This is now a stated limitation with a measured size.

A Monte Carlo cross-check of the integration (4,000,000 draws per cell, seed 1234, exact posterior and a common 70th-percentile threshold) gave 13.00, 22.26 and 15.18 pp for d0.50-r1.00, d1.00-r1.00 and d0.00-r1.50, against 13.04, 22.25 and 15.20 pp by integration (JRN-0015).

### 2.3 EXP-003: shape near the cutoff, not base rate alone, drives the gap (H0 rejected; H2 sign reversal analytically determined; H3 and H4 sign kept)

| Competing explanation (source) | Evidence | Status |
|---|---|---|
| The four implementation-check failures reflect a code fault in non-default kappa or p_B paths, not the seed realisation (DEC-019) | Exploratory rerun on seeds 1000 to 1019 passed 60/60 (JRN-0014); grid-D signs are far from zero (smallest 2.09 [1.85, 2.32] pp). The owner decided on 2026-11-25 that this is a disclosed limitation on H4, with no rerun (DEC-021). | Partly addressed; disclosed, not resolved. |
| Threshold placement (kappa) drives the sign (protocol section 11) | Grid D: positive at kappa 0.1, 0.3 and 0.5 and p_B 0.2 and 0.5. Magnitude falls with kappa (2.09 to 2.82 pp at kappa 0.5). | Addressed (committed), with the DEC-019 caveat on two cells. |
| Grid C's non-Gaussian result depends on the one parameterisation per family | Not addressed; one parameterisation per family. | Open limitation. |
| The "refutation" is a redescription: TPR is by definition the share of qualified individuals above the threshold, so its dependence on where they sit is an identity | Raised in the second review pass (`review_pass_2.md`). | Accepted as a qualification: the falsifiable content is that a base-rate difference is neither necessary (grid A) nor sufficient for a fixed sign (grid B). |

### 2.4 EXP-004: on the real score, the prediction fails with a sign reversal (H1-real disconfirmed, D = -7.45 [-8.75, -6.05] pp)

| Competing explanation | Evidence | Status |
|---|---|---|
| The reversal is a split or tie-breaking artefact | Control behaves as designed (P0 EOG -0.33 [-1.34, 0.70] pp); the full-pool analogue (no split, one threshold at the pool's 70th score percentile) gives the same sign: 62.05% of qualified Group A against 70.31% of qualified Group B above it (JRN-0016). | Addressed. |
| The lower-base-rate group's qualified members are not near the cutoff in this score (EXP-003's narrowed reading) | JRN-0016: the median score of qualified members is -0.29 in Group B against -0.53 in Group A; the qualified members of Group B have a higher mean age (48.50 against 43.90 years), a score input. Unqualified members of Group B score lower (median -2.19 against -1.83). | Supported descriptively (exploratory). This is consistent with EXP-003, not a test of it. |
| The group-blind score relates differently to the label in the two groups (the synthetic model assumes one common latent scale and equal noise) | Committed: ECE gap -7.05 [-7.51, -6.56] pp on R-hours against -0.86 [-1.15, -0.56] pp on the control. JRN-0016: the logistic probability over-predicts Group B by 11.23 pp in the large and under-predicts Group A by 2.98 pp; in every score decile Group B's observed rate is lower (top decile 40.12% against 74.47%). | Present and large. The synthetic model also gives a lower rate for Group B at equal score (through the prior shift), so this alone does not explain the reversal, but the size of the difference shows the generator's measurement assumptions do not describe this score. |
| The sign depends on the scale on which the rule is "equal" | Committed: under P1 (within-group calibrated score, one threshold) the R-hours EOG is +30.52 [25.63, 35.58] pp, the sign the synthetic model predicts. | Addressed (committed): under one equal rule the gap is reversed, under another equal rule it has the predicted sign. |
| Fixed pool: intervals cover split and tie-breaking only | Stated in the protocol. | Not addressable within the design. |
| Prior knowledge of the dataset (C4) | Disclosed. | Not removable. |

**Net effect on the EXP-004 conclusion.** The frozen verdict stands: H1-real is disconfirmed. The review adds that the reversal is accompanied by qualified Group B members sitting higher on the score, which fits EXP-003's narrowed reading, and that the predicted sign appears under P1. It does not establish why the partition looks this way, and nothing is claimed about workers, hours or pay.

## 3. What the review changed in the conclusions

1. The project-level mechanism statement is narrowed everywhere to "where the qualified members of each group sit relative to the common cutoff", with the base-rate version reported as refuted in this model (EXP-003) and contradicted on the real score (EXP-004).
2. P1's PPV-parity result and P1's magnitudes are qualified as dependent on the 20-bin calibration map (JRN-0015).
3. EXP-004's contradiction is reported as a contradiction of the base-rate prediction, not of the narrowed mechanism, and as dependent on the scale of the equal rule (P0 against P1).
4. H4 is reported with the owner-accepted limitation of DEC-019.
5. No frozen verdict changed.

## 4. Expected versus observed

Verdicts are those of the frozen rules. "Known in advance" marks outcomes implied analytically or seen exploratorily before the freeze.

| Experiment | Hypothesis | Prediction (frozen) | Observation (committed) | Verdict under the frozen rule | Known in advance |
|---|---|---|---|---|---|
| EXP-001 | H1 | D at least +2 pp at delta 0.5, rho 1 | 6.59 [6.20, 6.97] pp | Supported | Yes (analytic 6.31 pp; SIZING 6.30 pp) |
| EXP-001 | H1b | Descriptive at delta 0 (analytic 0.000, 0.177, 0.081 pp) | -0.09, 0.15, 0.11 pp; intervals include 0 | Descriptive; no equivalence claimed | Yes (analytic) |
| EXP-001 | Implementation check | 48 of 48 within 3 SE | 48 of 48 | Passed | Not applicable |
| EXP-002 | H1 | No policy meets SR, EO and PPV parity within 2 pp at delta 0.5; all do at the control | No policy does (smallest worst violation 11.74 pp); all four do at the control | Supported | Expected from theory (abstract-level sources) |
| EXP-002 | H2 | Utility of P2 and P3 below P0 at delta 0.5 | P2 -0.01773, P3 -0.00215 per capita; P1 +0.00058 | Supported | No |
| EXP-003 | H0 / H1 | H0: EOG within +/-2 pp at equal base rates | 19.44 pp (s_B 0.5) and -22.50 pp (s_B 2) | H0 rejected, H1 supported | Partly (analytic values computable) |
| EXP-003 | H2 | Sign stable at a fixed base-rate gap | Sign reversal at s_B 2: -9.56 [-10.01, -9.12] pp | Sign reversal, as analytically determined (A1) | Yes (population -9.73 pp) |
| EXP-003 | H3 | Sign kept under t3 and log-normal | 2.29 and 1.43 pp, both positive | Supported (sign) | Partly (seen exploratorily, C4) |
| EXP-003 | H4 | Sign kept for kappa x p_B | Positive in all six cells (2.09 to 6.95 pp) | Supported (sign), with the DEC-019 limitation | Partly (one cell seen, C4) |
| EXP-003 | Implementation check | 60 of 60 within 3 SE | 56 of 60 | Failed on 4 comparisons; disclosed limitation (owner, DEC-021) | Not applicable |
| EXP-004 | H1-real | D at least +2 pp | -7.45 [-8.75, -6.05] pp | Disconfirmed; contradiction (sign reversal) | No (direction not known; C4 discloses general knowledge of the dataset) |
| EXP-004 | Secondary | Descriptive | No policy meets the three criteria; base-rate gap 19.07 pp | Descriptive | No |

The expected-versus-observed pattern is: every outcome implied by the Gaussian model was observed; the one prediction carried to a real score failed with the opposite sign; and the sensitivity experiment showed the base-rate wording of the mechanism to be wrong in the model itself.
