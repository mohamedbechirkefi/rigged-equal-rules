<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# EXP-001 protocol: one common threshold under unequal starting distributions

| Field | Value |
|---|---|
| Status | DRAFT v0.1, planned (protocol draft, awaiting owner freeze) |
| Date | 2026-11-24 |
| Protocol hash | none (recorded at freeze) |
| Parent protocol | `research/protocol.md` (DRAFT v0.1) |
| Depends on | M2 core engine (generator, policy P0, metrics) and the smoke run |

## 1. Precise question

Under one common raw-score threshold (P0), do qualified members of a group with a lower starting distribution of latent qualification have a lower chance of selection than qualified members of the other group, and how does the gap change with the starting-distribution gap delta and the measurement-noise ratio rho?

## 2. Mechanism

Y = 1[Q > 0]. If Group B's latent mean is lower, its qualified members are concentrated just above the cutoff Q = 0. Their observed scores X = Q + e are therefore lower on average than those of qualified members of A, so fewer of them clear a shared threshold t > 0. Higher noise in B (rho > 1) adds a second, separate channel: it spreads X for qualified and unqualified members alike.

## 3. Rationale from verified sources

Error-rate balance cannot generally coexist with other criteria when base rates differ (chouldechova2017, kleinberg2016; abstracts verified 2026-11-24). Single thresholds are the unconstrained optimum in corbettdavies2017 (abstract verified). The equal-opportunity criterion is from hardt2016 (abstract verified; definitions to be confirmed in the full text in M1).

## 4. Competing explanations

- The gap comes from measurement noise, not the starting distribution: separated by the factorial (rho = 1 cells).
- The gap is an artefact of threshold fitting: the threshold is fitted on a separate fitting population; analytic integration gives the population value.
- The gap reflects distribution shape near the cutoff rather than base rate: tested in EXP-003.

## 5. Hypotheses

- H0: EOG(delta = 0.5, rho = 1) - EOG(delta = 0, rho = 1) = 0.
- H1 (directional): this paired difference is at least +2 pp.
- Secondary H1b: at delta = 0, EOG increases with rho (noisier measurement of B lowers TPR_B when t is above the mean of qualified scores). Direction to be confirmed analytically before freeze; if the analytic sign is ambiguous, H1b becomes non-directional.
- Contradiction: the 95% bootstrap interval of the primary paired difference lies entirely below +2 pp.

## 6. Estimand

The population mean, over the generator, of the paired difference in EOG between the treatment cell and the control cell, at kappa = 0.30 and p_B = 0.5.

## 7. Design

- Experimental unit: one seed (fitting population plus evaluation population, n = 20,000 each).
- Independent variables: delta in {0, 0.25, 0.5, 1.0}; rho in {1, 1.5, 2}.
- Fixed: mu_A = 0, s_A = s_B = 1, sigma_A = 0.5, kappa = 0.30, p_B = 0.5, cost ratio c = 1.
- Treatment cell (primary): delta = 0.5, rho = 1. Control cell: delta = 0, rho = 1.
- Baseline policy: P0 only.
- Dependent variables: EOG (primary); SR, FPR, FNR, PPV, ECE gaps, utility, accuracy (secondary).
- Seeds: 0 to 19, common random numbers across cells.

## 8. Sample-size rationale and compute budget

See `research/protocol.md` section 6. 12 cells x 20 seeds = 240 runs. Budget: under 5 minutes wall-clock (planning estimate).

## 9. Metric formulas and units

As in `research/protocol.md` section 5. EOG in percentage points.

## 10. Uncertainty

Percentile bootstrap over the 20 seeds (10,000 resamples, seed 20261124) on the mean paired difference; t-interval as a check; per-seed values plotted. Analytic population EOG computed by numerical integration for every cell; simulated means must agree within 3 bootstrap standard errors.

## 11. Exclusion and stopping rules

As in `research/protocol.md` section 8.

## 12. Anticipated failure modes

- Threshold ties at large n: handled by seeded tie-breaking.
- Group with zero qualified individuals: impossible at these parameters (pi_B >= 0.159, n_B about 10,000), but the metric path returns null with a reason if it happens.
- Analytic and simulated values disagree: treated as an implementation bug; the experiment does not proceed until resolved.

## 13. Sensitivity tests

Delegated to EXP-003 (distribution shape, capacity, group share).

## 14. Reproducibility commands (to be implemented in M2)

```
uv run python -m rigged.cli smoke
uv run python -m rigged.cli run --experiment EXP-001
uv run python -m rigged.cli report --experiment EXP-001
```
