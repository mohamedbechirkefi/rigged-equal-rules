<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# When equal rules produce unequal outcomes, and when the obvious explanation fails

*Draft for Medium (M5). Not published; publication is the owner's decision. Author: Mohamed Bechir Kefi, independent researcher. Every number below is copied from the manuscript (`research/paper/manuscript.md`), which is an independent research manuscript / preprint draft, not peer-reviewed.*

## One threshold for everyone

A common way to call a decision rule fair is to apply it identically to everyone: one score, one cutoff. This small study asks whether such an equal rule can still produce unequal outcomes when two groups start from different distributions. The groups are abstract, Group A and Group B. They stand for no real or protected group, and nothing here describes a real hiring or selection decision.

## What was built

A seeded simulation gives each person a latent qualification, a label (qualified or not) and a noisy score. Group B's qualification can be shifted down (the starting-distribution gap, delta) and its score can be measured with more noise (the noise ratio, rho). Four rules select 30% of each population: one raw threshold (P0, the baseline), one threshold on a within-group calibrated score (P1), group thresholds with equal selection rates (P2) and group thresholds with equal true positive rates (P3). The primary metric is the equal-opportunity gap (EOG): the share of qualified Group A members selected minus the same share for Group B. Every protocol was frozen by the owner before the confirmatory runs, and every result is reported over 20 seeds with a 95% bootstrap interval.

*Figure suggestion (alt text): a dot-and-interval chart of the EOG for the four rules at delta 0.5 and rho 1, with a shaded band from -2 to +2 pp; only P3 sits inside the band. Source: the demo's explorer, drawn from `results/EXP-002/tables/summary.csv`.*

## What was measured

**The equal rule opens a gap (simulated).** When Group B starts half a standard deviation lower, the EOG under one common threshold rises by 6.59 pp [6.20, 6.97] against an equal-distribution control. This was expected: the Gaussian model implies it, and the analytic value is 6.31 pp. The run measures its size.

**No rule satisfies every criterion (simulated).** No rule meets selection-rate, equal-opportunity and predictive parity within 2 pp once distributions differ. Equalising selection rates (P2) moves the EOG to -19.99 pp; equalising true positive rates (P3) closes it (0.12 pp) but leaves a selection-rate gap of 11.74 pp. Both constrained rules cost utility.

**The base rate is not the explanation (simulated).** A natural reading is that a lower base rate lowers the chance of qualified members. A sensitivity experiment designed to refute that reading did so: at equal base rates, changing only the spread of Group B's qualification gives gaps of 19.44 and -22.50 pp, and at a fixed base-rate gap the sign reverses (-9.56 pp).

**On a real score, the prediction failed (real data).** On the UCI Adult test file, with a simple four-feature score and Group B defined as hours-per-week below 40, the base-rate prediction was disconfirmed with a sign reversal: -7.45 pp [-8.75, -6.05]. Qualified members of the lower-base-rate group were selected more often. A calibrated equal rule (P1) gave the predicted sign, +30.52 pp [25.63, 35.58], so even the direction of the gap depends on the scale on which the rule is equal.

## What this does and does not say

What survives is narrow: under one common rule, the gap follows where each group's qualified members sit relative to the cutoff. That is close to a definition, and its useful consequence is negative: base rates are not a safe guide to the sign of the gap.

The limits matter. The simulated results hold only inside the generator. EXP-004 covers one simple score and one non-protected partition of one 1994 extract; no protected attribute was used, and nothing can be said about workers, hours, pay or any real decision. One implementation check failed on 4 of 60 comparisons, a limitation disclosed on one hypothesis. The EOG is one criterion among several; no fairness metric is presented as universal. Related work was read at abstract level only.

## Reproduce it

Code, frozen protocols, raw results, the manuscript and a static demo with a sandbox: <https://github.com/mohamedbechirkefi/rigged-equal-rules>. Demo: <https://rigged-equal-rules.kefimohamedbechir.workers.dev>.

*Disclosure: an AI assistant (Claude, Anthropic) drafted the code, the experiments' reports, the manuscript and this article under the owner's direction; it is not an author.*
