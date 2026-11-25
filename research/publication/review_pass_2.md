<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# Second review pass: arguing against the preferred hypothesis

| Field | Value |
|---|---|
| Date | 2026-11-25 |
| Object | `research/paper/manuscript.md` (M4 first synthesis), the four experiment reports, the claims register |
| Reviewer | AI assistant, as internal quality control (master prompt 11.5). This is not external peer review. |
| Preferred hypothesis under challenge | "Equal rules yield unequal outcomes under different starting distributions", in the narrowed form "under one common rule, the equal-opportunity gap follows where each group's qualified members sit relative to the cutoff" |

The pass argues against the preferred reading. For each challenge it records whether the challenge holds, and what changed. Changes were made to the manuscript after this pass; section 3 lists them.

## 1. Challenges

### R1. The narrowed mechanism is close to a definition

**Challenge.** TPR is by definition the share of qualified individuals above the threshold. Saying that the gap "follows where qualified members sit relative to the cutoff" restates the metric and cannot be wrong. Presenting it as the supported mechanism overstates what EXP-003 adds.

**Assessment: holds.** The falsifiable content of EXP-003 is negative. A base-rate difference is neither necessary for a gap (grid A: 19.44 and -22.50 pp at equal base rates) nor sufficient for its sign (grid B: -9.56 pp at s_B 2). The positive statement is descriptive.

**Change.** The abstract, discussion and conclusion now present the location statement as near-definitional and state its testable content as the negative result about base rates.

### R2. "Refutes the base-rate interpretation" may overreach

**Challenge.** Grids A and B change the dispersion of Group B. That changes the starting distribution in another way, so the experiment shows that "starting distribution" is broader than "base rate". It does not show that base rates are irrelevant. In the primary design (equal dispersion) a lower base rate does produce a positive gap.

**Assessment: holds in part.** The refuted statement is the protocol's version: "a lower base rate lowers TPR", as a general rule. Within the equal-dispersion Gaussian family, the base-rate gap and the gap in location are the same thing, and the positive gap holds (EXP-001).

**Change.** The manuscript states that the refutation concerns the base rate as a sufficient description, and that within equal-dispersion Gaussian groups the base-rate wording and the location wording coincide.

### R3. EXP-004 does not test the synthetic mechanism, only its base-rate proxy

**Challenge.** The real data have no latent qualification and no "starting distribution" in the generator's sense. The only property of the partition that was predicted from is its lower base rate. A reversal therefore shows that the base rate is a poor proxy. It does not show that the synthetic mechanism fails, and calling it a "contradiction of the synthetic mechanism" (EXP-004 report) is broader than the evidence.

**Assessment: holds.** The frozen rule labels a negative D a contradiction, and that label stands. But what is contradicted is the prediction made from the base rate. The exploratory description (JRN-0016) is consistent with the narrowed location reading: qualified Group B members score higher.

**Change.** The manuscript and the claims register (CLM-012) now say "contradiction of the base-rate prediction". The verdict is unchanged.

### R4. The EXP-004 account is post hoc story-telling

**Challenge.** JRN-0016 was designed after seeing the reversal, on the same test pool. Any description that "accounts for" the reversal was bound to be found, because the full-pool shares above a cutoff are almost the quantity being explained.

**Assessment: holds.** JRN-0016 explains nothing causally. It shows that the reversal is not a split artefact and where the qualified members lie on the score.

**Change.** The manuscript labels JRN-0016 as post hoc and exploratory. It states that the score-calibration difference is shared in direction with the synthetic model and does not explain the reversal by itself. It adds, as future work, a pre-registered location measure for any new real score.

### R5. The "equal rule" is not unique, and the sign depends on which one

**Challenge.** On the same data, P0 gives -7.78 pp and P1 gives +30.52 pp on R-hours. If the sign depends on whether the common threshold is on the raw score or on a within-group calibrated score, then "equal rules yield unequal outcomes" is true, but its direction is not a property of the groups.

**Assessment: holds.** This is a real limitation of any statement about direction. It is also supported in the model: P1 more than doubles P0's EOG (CLM-016).

**Change.** The discussion keeps the paragraph on the scale of "equal" and adds that direction claims are rule-specific. The abstract now mentions P1's sign on the real score.

### R6. A contradictory secondary result was not reported as one

**Challenge.** EXP-002 H2 (constrained policies cost utility) is supported in the model. On the real score, P3 *gains* utility over P0 (+0.0038 [0.0028, 0.0049]), and P0's own utility per capita is negative (-0.0025). The manuscript reported these numbers but not that they run against H2's direction.

**Assessment: holds.** H2 was not a hypothesis of EXP-004, so no verdict changes. But this result runs against the synthetic pattern. It is consistent with P0 not being the unconstrained optimum on a score that is not calibrated within groups.

**Change.** Section 5.4 and the discussion now report it as a result that runs against EXP-002 H2's direction outside the model.

### R7. Consistency across cells is not replication

**Challenge.** "Positive in all six grid-D cells" and "48 of 48 checks pass" sound like many independent confirmations. All cells share the same 20 seeds under common random numbers, so they are not.

**Assessment: holds.** This is already in the limitations, but not where the results are stated.

**Change.** Section 5.3 now says this next to H4.

### R8. Uncertainty from 20 seeds

**Challenge.** Percentile bootstrap intervals over 20 seeds can under-cover.

**Assessment: does not change any verdict.** The t-intervals agree to within 0.15 pp on every primary contrast (Table 1; EXP-004 [-8.90, -6.00] against [-8.75, -6.05]). Every directional verdict has a margin of more than 4 pp to the 2 pp boundary: EXP-001's lower bound is 6.20 pp, and EXP-004's upper bound is -6.05 pp.

**Change.** None beyond the existing statement.

### R9. Leakage and prior knowledge

**Challenge.** The hours cutoff of 40 and the score features were chosen by an agent with general knowledge of Adult. The training-file base rates by sex were computed (JRN-0007). JRN-0016 used the test pool.

**Assessment: partly holds, already disclosed.** The score was fitted on the training file only. No test-file metric was computed before the freeze or the amendments. JRN-0007 is withdrawn from every analysis. The C4 disclosure covers prior knowledge. JRN-0016 is exploratory and changes no verdict. The direction of the EXP-004 outcome was not known before the run.

**Change.** None beyond the existing disclosures.

### R10. Missing exploratory and failed runs

**Challenge.** Does the manuscript list every run that was made, including exploratory ones?

**Assessment: holds in part.** No confirmatory run failed. The manuscript mentioned C4 and JRN-0014 to JRN-0016 but did not list the earlier exploratory matrices: SMOKE, SIZING and DEGEN (M2), the M3 smoke and sizing runs, and EXP-003-X.

**Change.** Section 4.7 now lists them with their journal entries.

### R11. Stale figures and numbers

**Challenge.** Are any numbers or figures stale?

**Assessment: holds in part.**
- The evidence audit found one wrong number in the EXP-001 report: SIZING 6.31 pp instead of 6.30 pp. It was corrected.
- The audit found stale status text in the EXP-003 report (DEC-019 "open for the owner") and in the experiment registry ("report pending"). Both were corrected.
- The figures in `research/experiments/` are byte-identical to `results/` and were generated from the committed `results.json`.

**Change.** Recorded in `evidence_audit.md`.

### R12. P1's results are an artefact of 20 bins

**Challenge.** The protocol names calibration-fit error as a confounder. P1's magnitudes might be binning artefacts.

**Assessment: holds in part (JRN-0015).** The exact-posterior P1 differs from the binned P1 by up to 7.67 pp in the EOG. The binned P1's PPV gap of 1.00 pp becomes 2.10 pp. EXP-002 H1 is unchanged.

**Change.** The manuscript qualifies P1's PPV-parity result and its magnitudes (section 5.2, limitations; CLM-004, CLM-016, CLM-018).

## 2. Challenges that did not hold

- **"EXP-001's support is an artefact of threshold fitting."** The analytic check passed 48 of 48, and the population value of 6.31 pp lies inside the interval.
- **"EXP-002's incompatibility is a finite-sample failure."** Every policy meets every criterion at the control.
- **"EXP-004's reversal is a split or tie artefact."** The control is within 2 pp, and the full-pool description gives the same sign.

## 3. Changes made to the manuscript after this pass

1. Abstract: the location statement is presented as near-definitional, with the negative base-rate result as its testable content. P1's predicted sign on the real score is added. (R1, R5)
2. Section 5.3: a sentence on common random numbers beside H4. (R7)
3. Section 5.4: P3's utility gain over P0 on the real score is reported as running against EXP-002 H2's direction. JRN-0016 is labelled post hoc. (R4, R6)
4. Section 4.7: every exploratory matrix is listed. (R10)
5. Section 6: the scope of the refutation (R2), the base-rate proxy reading of EXP-004 (R3), the rule-specific direction (R5) and the utility contradiction (R6).
6. Section 9: the conclusion no longer says "whenever"; future work adds a pre-registered location measure. (R1, R4)
7. Claims register: CLM-012 wording; limitations of CLM-004 and CLM-016. (R3, R12)
