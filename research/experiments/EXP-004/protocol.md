<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# EXP-004 protocol: second test on a real score distribution (UCI Adult)

| Field | Value |
|---|---|
| Status | FROZEN v1.0 (owner-approved 2026-11-24), not yet run |
| Date | 2026-11-24 |
| Protocol hash | SHA-256 of this file, in `research/freeze.json` and the registry |
| Parent protocol | `research/protocol.md`, section 13, "Amendments before freeze (owner-approved 2026-11-24, round 2)" |
| Data | UCI Adult (Becker and Kohavi 1996, DOI 10.24432/C5XW20), CC BY 4.0; `data/raw/adult.zip` |

## 1. Precise question

Does the pattern predicted by the synthetic model (one common threshold selects qualified members of the lower-base-rate group less often) appear when the score and the label are real rather than simulated?

## 2. Role of the real data

A second test, not a calibration of the synthetic study. The only fitted quantity is the score model (section 4), fitted on the official training file `adult.data`, which this experiment never evaluates on. The experiment runs on the official test file `adult.test` (the pool).

## 3. Hypotheses

- H0-real: D = EOG(R-hours, P0) - EOG(R-random, P0) = 0.
- H1-real (directional): D is at least +2 pp.
- Disconfirmation: the 95% percentile bootstrap interval of the mean paired D lies entirely below +2 pp. A negative D is reported as a contradiction of the synthetic mechanism on this real distribution.
- Secondary (descriptive): whether any of P0 to P3 meets selection-rate, equal-opportunity and predictive parity within 2 pp on R-hours; paired utility of P1 to P3 against P0; the base-rate gap of the partition.

## 4. Score model (fixed before the fit, fitted once)

Logistic regression of Y = 1[income > 50K] on age, education-num, log(1 + capital-gain), log(1 + capital-loss), each standardised by its training-file mean and SD (population SD). Unpenalised maximum likelihood by Newton-Raphson from zero, stop when the largest absolute step is below 1e-10, at most 100 iterations. Training data: `adult.data` after the ingestion exclusions. No group variable and no test-file row is used. X = fitted log-odds. The fitted values are stored in `research/experiments/EXP-004/config.json` and frozen with it.

## 5. Design

- Pool: `adult.test` rows after the ingestion exclusions (protocol section 13).
- Cells: R-hours (Group B = hours-per-week below 40) and R-random (the same labels permuted at random within the seed; same group sizes).
- Policies P0 to P3, kappa = 0.30, 20 calibration bins (P1), 10 ECE bins, cost ratio 1. P3 capacity tolerance 30 individuals (tied real score; parent protocol section 13, JRN-0006).
- Seeds 0 to 19. Per seed, `numpy.random.Generator(PCG64(SeedSequence([seed, 2])))` draws in order: a permutation of the pool (first floor(N/2) rows fit, the rest evaluate), N tie uniforms, a permutation of the group labels (R-random). Shared by both cells and all policies.
- Runs: 2 cells x 4 policies x 20 seeds = 160.

## 6. Uncertainty

As in `research/protocol.md` section 7 (percentile bootstrap over seeds, 10,000 resamples, seed 20261124; t-interval check). The pool is fixed, so the interval covers split and tie-breaking variability only, not sampling from a population: stated as a limitation in every report. No analytic cross-check.

## 7. Exclusion, stopping and failure

As in `research/protocol.md` section 8. Ingestion exclusions are counted, not chosen per result.

## 8. Claims boundary

Real records, abstract use. Group B is "hours-per-week below 40", a non-protected partition that correlates with other attributes; results are about this partition of this file under this score only. No claim about the people in the data, about income, or about any real hiring or lending decision.

## 9. Reproduction

```
python3 scripts/download_adult.py
scripts/rigged run --experiment EXP-004
scripts/rigged report --experiment EXP-004
```
