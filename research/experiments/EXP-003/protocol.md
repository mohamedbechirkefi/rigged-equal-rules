<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# EXP-003 protocol: sensitivity analysis (base rate versus distribution shape)

| Field | Value |
|---|---|
| Status | FROZEN v1.0 (owner-approved 2026-11-24), not yet run |
| Date | 2026-11-24 |
| Protocol hash | SHA-256 of this file, in `research/freeze.json` and the registry |
| Parent protocol | `research/protocol.md` (FROZEN v1.0), section 10 |
| Depends on | EXP-001 pipeline; generator extended with latent dispersion and non-Gaussian shapes |

## 1. Precise question

Is the equal-opportunity gap under a common threshold explained by the base-rate difference between groups, or by the shape of each group's qualification distribution near the cutoff?

## 2. Why this could invalidate the main interpretation

If EXP-001's gap were truly a base-rate effect, equal base rates should give no gap and a fixed base-rate gap should give a gap of stable sign. If instead a gap appears at equal base rates, or reverses sign at a fixed base-rate gap when only the dispersion changes, then "a lower starting base rate causes a lower TPR" is wrong as stated, and the interpretation must be narrowed to "the distribution of qualified individuals near the cutoff".

## 3. Hypotheses

- H0 (base-rate sufficiency): with pi_A = pi_B = 0.5 (mu_A = mu_B = 0), varying s_B in {0.5, 1, 2} with s_A = 1 leaves EOG within +/- 2 pp.
- H1 (shape matters, non-directional): EOG lies outside +/- 2 pp for at least one s_B != 1 at equal base rates.
- H2 (sign stability): with pi_B fixed at Phi(-0.5) (mu_B = -0.5 * s_B) and s_B in {0.5, 1, 2}, the sign of EOG is the same in all three cells. A sign reversal refutes the base-rate interpretation for that configuration. **Analytically determined before the run (amendment A1):** under the Gaussian model the population P0 EOG of cell B-sB2 is -9.73 pp, opposite in sign to the primary cell, so H2's outcome (a sign reversal) is known. The run quantifies this known result and checks the implementation; it is reported as analytically determined, not as a test with an unknown outcome.
- Robustness H3: with matched base rates (pi_A = 0.5, pi_B = Phi(-0.5)), replacing the Gaussian latent distribution with Student t (3 degrees of freedom, scaled to unit variance) or a shifted log-normal (sigma = 0.5, standardised) keeps the EOG sign of EXP-001's primary cell. Non-directional on magnitude.
- Robustness H4: at delta = 0.5, rho = 1, the EOG sign is unchanged for kappa in {0.1, 0.3, 0.5} and p_B in {0.2, 0.5}.

Each outcome is reported whichever way it falls; this experiment is designed so that its result can contradict EXP-001's interpretation.

## 4. Design

- Experimental unit: one seed; n = 20,000 per population; seeds 0 to 19.
- Grid A (equal base rates): s_B in {0.5, 1, 2}, mu_B = 0, rho = 1. 3 cells.
- Grid B (fixed base-rate gap): s_B in {0.5, 1, 2}, mu_B = -0.5 * s_B, rho = 1. 3 cells.
- Grid C (shape): latent family in {Gaussian, Student t3, shifted log-normal}, matched base rates, rho = 1. 3 cells.
- Grid D (operating point): kappa in {0.1, 0.3, 0.5} x p_B in {0.2, 0.5}, delta = 0.5, rho = 1. 6 cells.
- Policy: P0 for all; P3 also run on grids A and B as a check that the constrained rule closes the gap regardless of shape.
- Total: 15 cells x 20 seeds x P0 = 300 runs, plus 6 cells x 20 seeds x P3 = 120 runs.

## 5. Metrics and uncertainty

As in `research/protocol.md` sections 5 and 7. For non-Gaussian families, the analytic cross-check uses numerical integration of the stated density.

## 6. Exclusion, stopping, failure modes

As in `research/protocol.md` section 8. Heavy-tailed draws can produce extreme scores; no clipping is applied, and extreme values are logged.

## 7. Reproducibility commands (to be implemented in M2)

```
uv run python -m rigged.cli run --experiment EXP-003
uv run python -m rigged.cli report --experiment EXP-003
```

## 8. Amendments before freeze (owner-approved 2026-11-24)

A1 (H2 analytically determined), A2 (20 seeds), A3 (budget), A5 (P3 capacity tolerance of 10 individuals, which applies to the P3 runs of grids A and B) and A6 of `research/protocol.md` section 13 apply here. Exploratory estimates for cells B-sB2, C-student_t3, C-lognormal and D-k0.1-pB0.2 were seen before the freeze (SIZING, JRN-0003; `results/exploratory/sizing/`).
