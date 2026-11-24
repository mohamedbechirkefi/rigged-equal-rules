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
