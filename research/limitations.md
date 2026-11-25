<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# Limitations (living document, M0 draft)

No results exist yet. These are the limitations known by design.

1. **Simulation only.** Every result comes from a synthetic generator. It holds only within the generator's assumptions (Gaussian latent qualification, additive Gaussian measurement noise, a hard qualification cutoff). It is not evidence about any real decision system, population or protected group.
2. **The qualification label is assumed correct.** Y is defined by the generator, so it is measured without error. Real labels are often proxies that can themselves be biased; this study does not model label bias beyond the sensitivity checks of EXP-003.
3. **Static, one-shot decisions.** No feedback over time (see liu2018 in the literature review). Long-run effects of any rule are outside scope.
4. **Analytic predictability.** The primary hypothesis follows from the model. The simulation quantifies it and tests robustness; it does not discover a mechanism.
5. **Two groups, one score.** Real settings have many intersecting groups and many features.
6. **No universal metric.** The equal-opportunity gap is the primary metric for this question only. Other criteria encode other value judgements; the study shows they conflict and does not rank them.
7. **No human participants.** Nothing is inferred about human behaviour or preferences.
8. **Local toolchain.** `manuscript.tex` is not compiled locally (no TeX); PDFs come from Typst.

## Added at the freeze (2026-11-24)

- EXP-004 uses real records (UCI Adult, 1994 census extract) only as a source of a real score and label. Its only partition (hours-per-week below 40; owner's decision of 2026-11-25, option A) is non-protected but correlates with other attributes. No protected attribute is used in any analysis (master prompt claims boundary). Results describe this partition of this file under this score, not workers, hours, pay, causes or decisions. The round-3 design with sex as the primary group was superseded before any computation on the test file.
- EXP-004's pool is fixed: seed-to-seed variation reflects the random split and tie-breaking only, so its intervals understate uncertainty about any wider population.
- The EXP-004 score model is deliberately simple (four features, logistic); a different score could give a different gap.
- The real score is tied, so P3 meets capacity only within 30 individuals in EXP-004 (DEC-013, ratified by the owner in round 3 and again on 2026-11-25).
- P1 uses 20 quantile bins; its per-seed spread is larger than P0's (AP-008, not applied).
- The ECE gap does not depend on the policy and is reported once per cell (AP-007).
- EXP-003 H2 was analytically determined before the run (A1); several primary and EXP-003 values were seen exploratorily before the freeze (`research/freeze.json`, C4).

## Added in M3 (2026-11-25)

- EXP-003's implementation check (simulated P0 seed means against the numerical-integration population values, within 3 bootstrap SE) failed on 4 of 60 comparisons on the confirmatory seeds, in grid-D cells D-k0.1-pB0.5 (EOG, SR gap) and D-k0.5-pB0.2 (FPR gap, PPV gap). An exploratory rerun on seeds 1000 to 1019 passed 60 of 60 (JRN-0014). The 60 comparisons share one set of 20 seeds, so they are correlated. Unresolved; the owner decides (DEC-019). EXP-003 H4 rests on grid D and carries this caveat.
- EXP-004's primary contrast is negative (-7.45 pp): on this real distribution, the synthetic mechanism's prediction did not hold for the hours partition. The study does not explain why; any explanation is a hypothesis for M4, not a finding.
- The runner records per-run durations and matrix start and end times, not per-run timestamps (schema 1.0.0); `results/EXP-NNN/provenance.json` states this.
