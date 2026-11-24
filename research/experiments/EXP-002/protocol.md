<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# EXP-002 protocol: comparing equal and constrained rules; incompatible criteria

| Field | Value |
|---|---|
| Status | FROZEN v1.0 (owner-approved 2026-11-24), not yet run |
| Date | 2026-11-24 |
| Protocol hash | SHA-256 of this file, in `research/freeze.json` and the registry |
| Parent protocol | `research/protocol.md` (FROZEN v1.0) |
| Depends on | EXP-001 pipeline; policies P1, P2, P3 implemented and tested |

## 1. Precise question

At a fixed overall capacity, how do a common raw threshold (P0), a common calibrated threshold (P1), selection-rate parity (P2) and equal opportunity (P3) differ in group outcome gaps and utility, and can any of them satisfy selection-rate parity, equal opportunity and predictive parity at the same time when starting distributions differ?

## 2. Mechanism and verified rationale

When base rates differ, a classifier generally cannot equalise selection rates, error rates and positive predictive values at once (kleinberg2016, chouldechova2017, pleiss2017; abstracts verified 2026-11-24). Group-specific thresholds can enforce one constraint at a utility cost (corbettdavies2017, abstract verified).

## 3. Competing explanations

- Failure to meet a criterion is due to finite-sample fitting rather than incompatibility: checked by the delta = 0, rho = 1 control, where all criteria should hold within tolerance, and by comparison with analytic population values.

## 4. Hypotheses

- H0 (incompatibility, primary for this experiment): at delta = 0.5, rho = 1, at least one policy satisfies all three criteria within a tolerance of 2 pp (|SR gap|, |EOG|, |PPV gap| all at most 2 pp on the seed mean, with the 95% interval inside +/- 2 pp).
- H1: no policy satisfies all three at delta = 0.5, rho = 1, while all four policies satisfy all three at delta = 0, rho = 1.
- H2 (secondary, non-directional for P1, directional for P2 and P3): the utility per capita of P2 and P3 is lower than that of P0 at delta = 0.5 (paired difference over seeds). P1's utility relative to P0 is reported without a directional prediction.
- Contradiction of H1: some policy meets all three criteria at delta = 0.5, rho = 1, or the control fails to meet them (the latter signals an implementation or fitting problem, investigated before any interpretation).

## 5. Estimands

- For each policy and cell: mean over seeds of SR gap, EOG, FPR gap, PPV gap, ECE gap, utility per capita.
- Paired differences against P0 within seed.

## 6. Design

- Experimental unit: one seed.
- Cells: as EXP-001 (12 cells).
- Policies: P0, P1, P2, P3 (P0 runs shared with EXP-001 via common random numbers).
- Seeds: 0 to 19. Runs: 960, of which 240 shared.
- Fixed parameters as EXP-001.

## 7. Uncertainty

Percentile bootstrap over seeds for every gap and paired difference; per-seed distributions exported.

## 8. Exclusion and stopping

As in `research/protocol.md` section 8. Policy fitting failures (for example no threshold pair satisfying P3 within the grid) are recorded as failures with a reason.

## 9. Anticipated failure modes

- P3 threshold search may not reach exact equality on a finite population: the realised fitting-population gap is recorded; the criterion is judged on the evaluation population.
- P1 calibration bins may be sparse at large delta: bin counts are logged.

## 10. Sensitivity

Tolerance of 2 pp varied to 1 pp and 5 pp in the report (descriptive only).

## 11. Reproducibility commands (to be implemented in M2)

```
uv run python -m rigged.cli run --experiment EXP-002
uv run python -m rigged.cli report --experiment EXP-002
```

## 12. Amendments before freeze (owner-approved 2026-11-24)

A2 (20 seeds), A3 (budget), A5 (P3 capacity tolerance of 10 individuals; a P3 run outside it is a recorded failure) and A6 of `research/protocol.md` section 13 apply here.
