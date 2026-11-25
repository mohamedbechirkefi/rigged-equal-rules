<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# Literature review (M0 draft)

Status: initial, non-systematic search. No systematic-review protocol was followed. A source is listed as **verified** only if its landing page was actually opened in this session; the content checked is stated. "Verified" here means the bibliographic record and abstract were checked, not that the full text was read. Full-text reading is an M1 task.

Access date for all entries below: 2026-11-24.

## 1. Verified sources (landing page opened)

| Key | Reference | Opened | What was checked | Relevance |
|---|---|---|---|---|
| kleinberg2016 | Kleinberg, J., Mullainathan, S., Raghavan, M. "Inherent Trade-Offs in the Fair Determination of Risk Scores." arXiv:1609.05807, v1 2016-09-19, v2 2016-11-17. https://arxiv.org/abs/1609.05807 | arXiv abstract page | Title, authors, versions, abstract: outside highly constrained special cases, three fairness conditions cannot hold simultaneously | Incompatibility of criteria (EXP-002) |
| chouldechova2017 | Chouldechova, A. "Fair prediction with disparate impact: A study of bias in recidivism prediction instruments." arXiv:1703.00056, 2017-02-28. https://arxiv.org/abs/1703.00056 | arXiv abstract page | Abstract: criteria cannot all hold when base rates differ; disparate impact can follow from error-rate imbalance. The arXiv page lists no journal reference | Base-rate dependence of error-rate balance (EXP-001, EXP-002) |
| hardt2016 | Hardt, M., Price, E., Srebro, N. "Equality of Opportunity in Supervised Learning." arXiv:1610.02413, 2016-10-07. https://arxiv.org/abs/1610.02413 | arXiv abstract page | Abstract: an oblivious criterion and post-processing based on joint statistics of predictor, target and group. The abstract does not itself name "equalized odds"; definitions to be checked in the full text | Source of the equal-opportunity criterion used for P3 and the primary metric |
| corbettdavies2017 | Corbett-Davies, S., Pierson, E., Feller, A., Goel, S., Huq, A. "Algorithmic decision making and the cost of fairness." arXiv:1701.08230 (v4, 2017-06-10); KDD 2017. https://arxiv.org/abs/1701.08230 | arXiv abstract page | Abstract: optimal constrained rules use group-specific thresholds; the unconstrained optimum is a single threshold; the trade-off can be substantial. The related DOI shown on the page was not resolved in this session and is left unverified | Threshold policies P0, P2, P3 and utility cost |
| pleiss2017 | Pleiss, G., Raghavan, M., Wu, F., Kleinberg, J., Weinberger, K. Q. "On Fairness and Calibration." arXiv:1709.02012 (v2, 2017-11-03); NIPS 2017 per the arXiv comment. https://arxiv.org/abs/1709.02012 | arXiv abstract page | Abstract: calibration is compatible with at most one error-balance condition (equal false-negative rates) | Calibrated policy P1; incompatibility in EXP-002 |
| liu2018 | Liu, L. T., Dean, S., Rolf, E., Simchowitz, M., Hardt, M. "Delayed Impact of Fair Machine Learning." arXiv:1803.04383; ICML 2018, PMLR 80:3150-3158. https://arxiv.org/abs/1803.04383 | arXiv abstract page | Abstract: one-step feedback model; fairness criteria can fail to help or harm; measurement error can change the conclusion | Out of scope (dynamics); cited as a limitation and future work |
| barocas2023 | Barocas, S., Hardt, M., Narayanan, A. *Fairness and Machine Learning: Limitations and Opportunities.* MIT Press, 2023. https://fairmlbook.org/ | Book home page | Publisher, year, online licence CC BY-NC-ND 4.0, chapter 3 "Classification" covers formal non-discrimination criteria. The names independence, separation and sufficiency were not visible on the page opened and remain to be checked in the chapter | Textbook framing of criteria; terminology |
| ding2021 | Ding, F., Hardt, M., Miller, J., Schmidt, L. "Retiring Adult: New Datasets for Fair Machine Learning." NeurIPS 34, 2021. Cited as listed in the folktables README, https://github.com/socialfoundations/folktables | folktables README only | Citation as given by the README; the paper itself was not opened. **Paper unverified.** | Dataset audit only |
| becker1996 | Becker, B., Kohavi, R. "Adult" [Dataset]. UCI Machine Learning Repository, 1996. https://doi.org/10.24432/C5XW20 | UCI dataset page | Licence CC BY 4.0, 48,842 instances, donation date 1996-04-30 | Dataset audit only |

## 2. Unverified (named but not opened)

- The ProPublica "Machine Bias" article (2016): only the data repository https://github.com/propublica/compas-analysis was opened, not the article.
- Any equalized-odds definition text, and the KDD DOI of corbettdavies2017.
- Dwork et al., "Fairness through awareness" (individual fairness): not opened; would be cited only after verification.

## 3. Synthesis so far

The incompatibility of group fairness criteria under unequal base rates is established theory (kleinberg2016, chouldechova2017, pleiss2017). Threshold rules are the standard object of analysis (hardt2016, corbettdavies2017). The narrow contribution available to this project is therefore not a new theorem. It is:

1. a transparent, seeded, reproducible quantification of how much a single common threshold separates equally qualified individuals as the starting distribution and the measurement noise vary, with uncertainty over seeds and an analytic cross-check;
2. a sensitivity analysis that separates the base-rate explanation from a distribution-shape explanation (EXP-003);
3. an interactive explorer showing the trade-offs, with measured and visitor-generated results kept apart.

No novelty is claimed. Whether item 2 has been done in this exact form is unknown until the M1 full-text search; until then it is described as "a robustness check" and not as a contribution beyond prior work.

## 4. M1 to-do

- Read the full texts of hardt2016, kleinberg2016, chouldechova2017, pleiss2017, corbettdavies2017 and chapter 3 of barocas2023; record exact definitions and theorem statements used.
- Search for prior simulation studies of threshold rules under shifted latent distributions and differential measurement noise (search terms: "differential measurement error fairness threshold", "label bias base rate simulation").
- Build `research/paper/references.bib` only from verified entries.

## 5. M6 full-text check (2026-11-25)

On 2026-11-25 the full text of each cited paper was opened from a free, legal source (arXiv PDF or the PMLR PDF; no login, no paid access). Text was extracted locally and the passage behind each statement in manuscript section 2 was read and compared with the statement. **No paper was read in full**; each is labelled "full text opened, cited passage checked".

| Key | Full text opened | Passage checked | Result |
|---|---|---|---|
| kleinberg2016 | https://arxiv.org/pdf/1609.05807 (v2, 2016-11-17) | Abstract; section 1.1, conditions (A) to (C); section 1.2, Theorem 1.1 (p. 5) | Supported: the three conditions hold together only under perfect prediction or equal base rates. |
| chouldechova2017 | https://arxiv.org/pdf/1703.00056 (v1, revised February 2017) | Abstract; section 2.3, equation (2.6) (p. 7); section 3 (pp. 7 to 8) | Supported: with unequal prevalence, predictive parity excludes equal FPR and FNR; section 3 shows how disparate impact arises from error-rate imbalance. |
| pleiss2017 | https://arxiv.org/pdf/1709.02012 (v2, 2017-11-03) | Abstract; section 4, Theorem 1 (p. 6) | Supported with a qualification now stated in the manuscript: the result assumes unequal base rates and excludes perfect classifiers. |
| corbettdavies2017 | https://arxiv.org/pdf/1701.08230 (v4) | Abstract; section 3, "Optimal decision rules" (pp. 3 to 5); section 4, Table 1 (p. 6) | Supported with a qualification now stated: the group-specific threshold result covers statistical parity, conditional statistical parity and predictive equality; equal opportunity is not analysed. The cost estimate is on Broward County data (4% to 9% estimated increase in violent crime across the three constraints, their Table 1). |
| hardt2016 | https://arxiv.org/pdf/1610.02413 (v1) | Abstract; section 2, Definition 2.2 (p. 4); section 4, Definition 4.1 (pp. 5 to 6) | Supported: equal opportunity is equality of true positive rates across groups, so the study's EOG is zero exactly when it holds; the derived predictor depends only on the joint distribution of score, group and target. |
| liu2018 | https://proceedings.mlr.press/v80/liu18c/liu18c.pdf; landing page https://proceedings.mlr.press/v80/liu18c.html | Abstract; section 3, Theorems 3.3 and 3.4 (pp. 5 to 6); venue and pages 3150 to 3158 from the PMLR page | Supported. |
| barocas2023 | https://fairmlbook.org/classification.html | Chapter 3 "Classification": sections on statistical non-discrimination criteria (independence, separation, sufficiency) | Supported (framing only). |
| becker1996 | UCI dataset page (2026-11-24) | Licence and DOI | Unchanged: verified at M0. |
| ding2021 | not opened | none | Still unverified; not cited in the manuscript. |

The KDD DOI of corbettdavies2017 remains unverified, as before.

