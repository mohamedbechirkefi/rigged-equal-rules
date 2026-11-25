<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# EXP-004 protocol: second test on a real score distribution (UCI Adult)

| Field | Value |
|---|---|
| Status | FROZEN v1.2 (owner-approved 2026-11-24; pre-data amendments of round 3, owner-approved 2026-11-24, section 10, and of 2026-11-25, owner-approved 2026-11-25, section 11), not yet run |
| Date | 2026-11-24 (amended 2026-11-25) |
| Protocol hash | SHA-256 of this file, in `research/freeze.json` and the registry |
| Parent protocol | `research/protocol.md`, section 13, "Amendments before freeze (owner-approved 2026-11-24, round 2)", "Amendments before data (owner-approved 2026-11-24, round 3)" and "Amendment before data (owner-approved 2026-11-25)" |
| Data | UCI Adult (Becker and Kohavi 1996, DOI 10.24432/C5XW20), CC BY 4.0; `data/raw/adult.zip` |

## 1. Precise question

Does the pattern predicted by the synthetic model (one common threshold selects qualified members of the lower-base-rate group less often) appear when the score and the label are real rather than simulated?

## 2. Role of the real data

A second test, not a calibration of the synthetic study. The only fitted quantity is the score model (section 4), fitted on the official training file `adult.data`, which this experiment never evaluates on. The experiment runs on the official test file `adult.test` (the pool).

## 3. Hypotheses

- H0-real: D = EOG(R-hours, P0) - EOG(R-hours-random, P0) = 0 (Group B = hours-per-week below 40; parent protocol section 13, amendment of 2026-11-25, A25-1).
- H1-real (directional): D is at least +2 pp.
- Disconfirmation: the 95% percentile bootstrap interval of the mean paired D lies entirely below +2 pp. A negative D is reported as a contradiction of the synthetic mechanism on this real distribution.
- Secondary (descriptive): whether any of P0 to P3 meets selection-rate, equal-opportunity and predictive parity within 2 pp on R-hours; paired utility of P1 to P3 against P0; the base-rate gap of the partition.

## 4. Score model (fixed before the fit, fitted once)

Logistic regression of Y = 1[income > 50K] on age, education-num, log(1 + capital-gain), log(1 + capital-loss), each standardised by its training-file mean and SD (population SD). Unpenalised maximum likelihood by Newton-Raphson from zero, stop when the largest absolute step is below 1e-10, at most 100 iterations. Training data: `adult.data` after the ingestion exclusions. No group variable and no test-file row is used. X = fitted log-odds. The fitted values are stored in `research/experiments/EXP-004/config.json` and frozen with it.

## 5. Design

- Pool: `adult.test` rows after the ingestion exclusions (protocol section 13).
- Cells: R-hours (primary; Group B = hours-per-week below 40, Group A = 40 or more) and R-hours-random (the hours labels permuted by the seed's row-index permutation; same group sizes). Sex is used in no cell and no analysis (section 11).
- Policies P0 to P3, kappa = 0.30, 20 calibration bins (P1), 10 ECE bins, cost ratio 1. P3 capacity tolerance 30 individuals (tied real score; parent protocol section 13, JRN-0006).
- Seeds 0 to 19. Per seed, `numpy.random.Generator(PCG64(SeedSequence([seed, 2])))` draws in order: a permutation of the pool (first floor(N/2) rows fit, the rest evaluate), N tie uniforms, a permutation of the row indices, applied to the hours labels of R-hours-random. Shared by both cells and all policies.
- Runs: 2 cells x 4 policies x 20 seeds = 160.

## 6. Uncertainty

As in `research/protocol.md` section 7 (percentile bootstrap over seeds, 10,000 resamples, seed 20261124; t-interval check). The pool is fixed, so the interval covers split and tie-breaking variability only, not sampling from a population: stated as a limitation in every report. No analytic cross-check.

## 7. Exclusion, stopping and failure

As in `research/protocol.md` section 8. Ingestion exclusions are counted, not chosen per result.

## 8. Claims boundary

Real records, abstract use. Group B is "hours-per-week below 40", a non-protected partition of this 1994 census extract that correlates with other attributes. No protected attribute (sex, race or any other) is used in any confirmatory or exploratory analysis, following the master prompt's claims boundary: "No real hiring decisions or protected-group claims; do not suggest a universal fairness metric." Results are about this partition of this file under this score only. No claim about workers, hours, pay, any cause, the people in the data or any real hiring or lending decision. No fairness metric is presented as universal.

## 9. Reproduction

```
python3 scripts/download_adult.py
scripts/rigged run --experiment EXP-004
scripts/rigged report --experiment EXP-004
```

## 10. Amendment before data (owner-approved 2026-11-24, round 3)

The owner decided ("Approve all", 2026-11-24, round 3; `owner-approvals-2026-11-24c.md`, section 1): the primary comparison uses **sex** as the group attribute; hours-per-week below 40 stays as a secondary check; nothing is computed on the test file until the confirmatory run; the P3 capacity tolerance of 30 is ratified. Applied in v1.1 of this protocol (sections 3, 5 and 8) and in the parent protocol, section 13, round 3 (R3-1 to R3-10), before any EXP-004 metric on `adult.test` was computed. Group B of R-sex was set by the rule written first (lower base rate on `adult.data`): `Female` 0.1095 against `Male` 0.3057 (JRN-0007, training file only). The v1.0 hashes are kept in `research/freeze.json` with the reason they were superseded.

Superseded on 2026-11-25 by section 11. The text above records what the owner decided in round 3; it no longer describes the design.

## 11. Amendment before data (owner-approved 2026-11-25)

The owner chose option A ("approve all recommendations, RIGGED A", 2026-11-25; `owner-approvals-2026-11-25.md`, item 1, which replaces item 1 of `owner-approvals-2026-11-24c.md`): "EXP-004's primary group attribute is hours-per-week below 40." Sex is "not used in any confirmatory or exploratory analysis. This respects the master prompt's claims boundary." "The P3 capacity tolerance of 30 is still ratified." Applied in v1.2 of this protocol (sections 3, 5 and 8) and in the parent protocol, section 13, amendment of 2026-11-25 (A25-1 to A25-9), written before any code, config or test changed and before any computation on `adult.test`. The cells R-sex and R-sex-random are withdrawn; the round-3 training-file base rates by sex (JRN-0007) are withdrawn from use. The v1.1 hashes are kept in `research/freeze.json` with the reason they were superseded.
