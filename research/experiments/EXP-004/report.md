<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# EXP-004 report: second test on a real score distribution (UCI Adult)

| Field | Value |
|---|---|
| Experiment | EXP-004 |
| Date | 2026-11-25 |
| Version | 1.0 |
| Status | Complete (160 of 160 runs ok). Confirmatory, real data (UCI Adult, CC BY 4.0). H1-real disconfirmed. |
| Authorship | Mohamed Bechir Kefi (C3). AI assistant disclosed as a research and development assistant, not an author. |
| Protocol | `research/experiments/EXP-004/protocol.md`, FROZEN v1.2 (pre-data amendment of 2026-11-25, owner-approved), SHA-256 ff9b80ff4c2421b9057838e1775bcfb08da65ae9e26b30c6c4f3ecdc4bfe30ae |
| Config | SHA-256 6fe218fd09d7ea15f1689e048cdb44b935d110307889b14121008df165aed0c1 |
| Data | `data/raw/adult.zip`, SHA-256 7537312dd56c2b98035880805ce99e68183a30ee468aa5329d6df0fbb3cc21bb; data manifest SHA-256 37194645cd251abaab069a90a26908b3032bdd573097633fb9908bfe9540192d |
| Code revision | b455d59294ea98e2b050ef30f20bc74b7993969e (tree clean) |
| Results | `results/EXP-004/` (results.json SHA-256 d00eae903565c63d58bba98477928dbe60bbde4ee4b1c17e980e4f8656ea58c5) |

## 1. Executive summary

**Question.** Does the synthetic prediction hold on a real score and label? The prediction is that one common threshold selects qualified members of the lower-base-rate group less often.

**Method.** A four-feature logistic score was fitted on `adult.data`. Policies P0 to P3 were applied on `adult.test`, comparing the partition hours-per-week below 40 against a random permutation of the same labels, over 20 random splits.

**Outcome.** D = EOG(R-hours, P0) - EOG(R-hours-random, P0) = -7.45 pp (95% bootstrap [-8.75, -6.05]). The interval lies entirely below +2 pp, so H1-real is disconfirmed. Because D is negative, the frozen rule reports it as a contradiction of the synthetic mechanism on this real distribution. Qualified members of the lower-hours group were selected more often, not less. This holds even though that group's base rate is much lower (9.13% against 28.20%).

**Caveat.** The pool is fixed, so the interval covers split and tie-breaking variability only.

## 2. Rationale

This is a second test of the synthetic mechanism on a real score distribution, not a calibration of the synthetic study (protocol section 2).

## 3. Hypotheses and definitions

- Group B is hours-per-week below 40; Group A is 40 or more. R-hours-random applies the seed's row-index permutation to the hours labels.
- H0-real: D = 0. H1-real: D is at least +2 pp. Disconfirmation: the 95% percentile bootstrap interval lies entirely below +2 pp. A negative D is reported as a contradiction.
- Secondary analyses, all descriptive:
  - whether any policy meets SR, EO and PPV parity within 2 pp on R-hours;
  - paired utility of P1 to P3 against P0;
  - the base-rate gap of the partition.

## 4. Methodology

**Score.** Logistic regression on age, education-num, log1p capital-gain and log1p capital-loss, standardised and fitted once on `adult.data` (JRN-0005, frozen in the config). No group variable is a score input.

**Pool.** The 16,281 kept rows of `adult.test`. Per seed:
- one RNG (`SeedSequence([seed, 2])`) draws, in order, the pool permutation (8,140 rows to fit, 8,141 to evaluate), the tie uniforms, and the row-index permutation;
- these draws are shared by both cells and all policies.

**Policies and design.**
- P0 to P3 with kappa 0.30, 20 calibration bins and cost ratio 1.
- P3 capacity tolerance of 30 individuals, owner-ratified.
- Seeds 0 to 19; 160 runs.

**Statistics.** Percentile bootstrap over seeds (10,000 resamples, seed 20261124). No analytic cross-check applies.

**Protected attributes.** None is used in any analysis (amendment of 2026-11-25; master prompt claims boundary).

**Environment.** As EXP-001.

## 5. Implementation verification

- **Tests:** 116 passed before the run. The suite tests ingestion, the score, the populations and the routing on synthetic fixtures only.
- **P3:** no P3 run exceeded the capacity tolerance. No run failed, and no metric was undefined.
- **Control:** the random control behaves as designed. Its P0 EOG is -0.33 pp [-1.34, 0.70] and its base-rate gap is -0.07 pp [-0.54, 0.47].

## 6. Execution record

- **Command:** `scripts/run_confirmatory.sh EXP-004`.
- **Time:** 2026-11-25, 00:15:47Z to 00:15:49Z UTC; wall clock 1.42 s; exit 0.
- **Resources:** peak RSS 71.5 MiB. Mean runtime per run: P0 0.023 s (includes loading the pool), P1 0.005 s, P2 0.003 s, P3 0.004 s.
- **Runs:** 160 planned, 160 ok, 0 failed. Run IDs RUN-EXP-004-<cell>-<policy>-s<seed>; config hashes in `provenance.json`.

**Deviations and owner decisions:**
- **Pre-data amendment (owner, 2026-11-25, "approve all recommendations, RIGGED A", DEC-018).** Hours-per-week below 40 is the primary group, and sex is removed from every analysis. It replaces the round-3 design (sex primary, 320 runs), which was never run.
- **Base-rate table (DEC-020).** `tables/base_rate_gap.csv` was produced after the run by `scripts/exp004_base_rates.py`, written then. It computes the protocol's descriptive base-rate gap from `results.json` with the frozen interval method.
- **Prior knowledge.** The agent knew from the general literature, without computing it, that lower hours go with a lower share of high incomes on this dataset (C4).

## 7. Results

**Primary contrast** (P0, paired over 20 seeds; `results/EXP-004/tables/contrasts.csv`):

| Metric | Mean (pp) | SD (pp) | 95% bootstrap | 95% t-interval |
|---|---|---|---|---|
| EOG (primary D) | -7.45 | 3.11 | [-8.75, -6.05] | [-8.90, -6.00] |
| SR gap | 7.76 | 1.25 | [7.22, 8.28] | [7.17, 8.34] |
| PPV gap | 29.11 | 2.73 | [27.94, 30.28] | [27.83, 30.39] |
| FPR gap | 0.22 | 1.18 | [-0.28, 0.73] | [-0.34, 0.77] |

**Per cell and policy** (seed means in pp, 95% bootstrap; `results/EXP-004/tables/summary.csv`):

| Cell | Policy | SR gap | EOG | PPV gap | FPR gap |
|---|---|---|---|---|---|
| R-hours | P0 | 7.92 [7.68, 8.15] | -7.78 [-8.76, -6.80] | 28.45 [27.75, 29.24] | 0.57 [0.24, 0.87] |
| R-hours | P1 | 28.27 [26.16, 30.38] | 30.52 [25.63, 35.58] | 10.47 [7.19, 13.69] | 19.22 [17.37, 21.01] |
| R-hours | P2 | -0.21 [-0.83, 0.38] | -17.54 [-18.63, -16.45] | 33.10 [32.41, 33.86] | -7.33 [-7.97, -6.73] |
| R-hours | P3 | 13.85 [13.00, 14.65] | 0.95 [-1.03, 2.83] | 24.68 [24.07, 25.34] | 6.16 [5.44, 6.82] |
| R-hours-random | P0 | 0.17 [-0.28, 0.64] | -0.33 [-1.34, 0.70] | -0.66 [-1.44, 0.24] | 0.35 [-0.08, 0.77] |
| R-hours-random | P1 | -3.99 [-6.76, -1.24] | -4.71 [-7.45, -1.96] | 2.01 [-0.43, 4.40] | -3.73 [-6.53, -0.93] |
| R-hours-random | P2 | 0.21 [-0.15, 0.59] | -0.27 [-1.20, 0.69] | -0.69 [-1.39, 0.14] | 0.39 [0.10, 0.67] |
| R-hours-random | P3 | 0.49 [-0.42, 1.42] | 0.10 [-1.29, 1.57] | -0.90 [-1.87, 0.14] | 0.64 [-0.19, 1.49] |

**Incompatibility check on R-hours.** No policy meets all three criteria within 2 pp. The failures by policy are:
- P0: EO and PPV;
- P1: SR, EO and PPV;
- P2: EO and PPV;
- P3: SR and PPV.

**Utility per capita against P0 on R-hours** (`policy_vs_p0.csv`):
- P1 +0.0043 [0.0025, 0.0059];
- P2 -0.0063 [-0.0074, -0.0053];
- P3 +0.0038 [0.0028, 0.0049].

**Base rates on the evaluation half** (`base_rate_gap.csv`):
- R-hours: Group A 28.20% [28.03, 28.38]; Group B 9.13% [8.97, 9.28]; gap 19.07 pp [18.84, 19.34]; Group B share 24.16%.
- Control: gap -0.07 pp [-0.54, 0.47].

Strip plot: `figures/XFIG-EXP-004-01-eog.svg`.

## 8. Interpretation

**Measured.** The partition has the lower base rate the synthetic model assumes for Group B. Yet under one common threshold, its qualified members had a higher TPR, by 7.45 pp net of the control. The synthetic prediction (at least +2 pp) is disconfirmed, and the sign is reversed.

**Model-dependent reading (a hypothesis for M4, not a finding).** EXP-003 showed that the sign of the gap depends on where qualified individuals sit relative to the cutoff, not on the base rate alone. A lower base rate with a reversed gap fits that narrower interpretation. This file does not establish why.

**Other observations.**
- P3 closes the EOG at the cost of a 13.85 pp SR gap.
- P1's calibrated threshold produces a large EOG of 30.52 pp, with wide intervals.
- On the random control P1 shows non-zero gaps (SR -3.99 pp) while P0, P2 and P3 stay within 2 pp. P1's per-seed spread is a known limitation (AP-008).
- The utility differences are small.

Nothing here is a claim about workers, hours, pay, causes or real decisions.

## 9. Threats to validity

- **Fixed pool:** the intervals understate population uncertainty.
- **Simple score:** another score could change the gap.
- **The partition:** it correlates with other attributes.
- **Ties:** the 1994 extract has tied scores, so P3 meets capacity only within 30 individuals.
- **Single partition:** one partition and one dataset.
- **Prior knowledge:** see section 6.
- **No protected attributes:** none was used, so nothing about protected groups can be inferred.

## 10. Conclusion and next experiment

On this real distribution, the synthetic mechanism's prediction fails, with a sign reversal for the hours partition. This is a contradiction the manuscript must report. M4 should challenge both the synthetic interpretation and this result. One direction is to compare the score distributions of qualified individuals near the threshold, labelled exploratory, without protected attributes.

## 11. Reproduction

See `research/experiments/EXP-004/reproduction.md`.
