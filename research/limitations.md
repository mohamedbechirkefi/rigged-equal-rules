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

- EXP-004 uses real records (UCI Adult, 1994 census extract) only as a source of a real score and label. Its primary partition is the recorded sex field (Group B Female; a protected attribute, the owner's decision of 2026-11-24, round 3), and its secondary partition (hours-per-week below 40) is non-protected but correlates with other attributes. Results describe these partitions of this file under this score, not women or men in general, people, pay, causes or decisions. The sex field is a recorded binary category of the extract.
- EXP-004's pool is fixed: seed-to-seed variation reflects the random split and tie-breaking only, so its intervals understate uncertainty about any wider population.
- The EXP-004 score model is deliberately simple (four features, logistic); a different score could give a different gap.
- The real score is tied, so P3 meets capacity only within 30 individuals in EXP-004 (DEC-013, ratified by the owner in round 3).
- P1 uses 20 quantile bins; its per-seed spread is larger than P0's (AP-008, not applied).
- The ECE gap does not depend on the policy and is reported once per cell (AP-007).
- EXP-003 H2 was analytically determined before the run (A1); several primary and EXP-003 values were seen exploratorily before the freeze (`research/freeze.json`, C4).
