<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# Limitations (living document; M0 design limitations, updated at the freeze, M3 and M4)

The M0 list below gives the limitations known by design; later sections add what the runs and the M4 review found.

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

- EXP-003's implementation check (simulated P0 seed means against the numerical-integration population values, within 3 bootstrap SE) failed on 4 of 60 comparisons on the confirmatory seeds, in grid-D cells D-k0.1-pB0.5 (EOG, SR gap) and D-k0.5-pB0.2 (FPR gap, PPV gap). An exploratory rerun on seeds 1000 to 1019 passed 60 of 60 (JRN-0014). The 60 comparisons share one set of 20 seeds, so they are correlated. Unexplained. The owner decided on 2026-11-25 that it is a disclosed limitation on H4, with no rerun (DEC-019, DEC-021). EXP-003 H4 rests on grid D and carries this limitation.
- EXP-004's primary contrast is negative (-7.45 pp): on this real distribution, the synthetic mechanism's prediction did not hold for the hours partition. The study does not explain why; any explanation is a hypothesis for M4, not a finding.
- The runner records per-run durations and matrix start and end times, not per-run timestamps (schema 1.0.0); `results/EXP-NNN/provenance.json` states this.

## Added in M4 (2026-11-25)

- **P1 depends on its 20-bin calibration map (JRN-0015, exploratory).** With the exact Gaussian posterior, P1's population EOG differs from the binned simulation by -3.86 to +7.67 pp across the 12 EXP-001/EXP-002 cells. The exact value is outside the binned interval in 5 of them. At the primary cell, the PPV gap is 2.10 pp exact against 1.00 pp binned. P1's magnitudes and its PPV-parity result are therefore implementation-specific. The EXP-002 verdicts do not change.
- **The narrowed mechanism is near-definitional.** "The gap follows where qualified members sit relative to the cutoff" restates what TPR measures. Its testable content is negative: the base rate neither creates nor signs the gap (second review pass, R1).
- **EXP-004 tests only the base-rate prediction.** The real data have no latent qualification. The reversal contradicts the prediction made from the base rate; it does not test a latent mechanism (R3).
- **Direction is rule-specific.** On R-hours, P0 gives -7.78 pp and P1 gives +30.52 pp (R5).
- **EXP-004's exploratory account is post hoc (JRN-0016).** It shows the reversal is not a split artefact and where qualified members lie on the score. It establishes no cause (R4).
- **Cells are not independent replications.** All cells share the same 20 seeds (R7).
- **Freeze-record hash.** `research/freeze.json` was appended after the runs (M3 deviation records). Its hash at run time, recorded in each `provenance.json`, differs from the current file. No frozen hash changed (evidence audit, section 2).
- **Literature at abstract level.** No cited source was read in full. Related-work statements are limited to abstracts.

