<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# LinkedIn draft (M5; not published, owner-controlled)

Does one threshold for everyone treat everyone equally?

I built a small, pre-registered simulation study (RIGGED) with two abstract groups, four decision rules and frozen protocols, then tested its prediction on one real score.

One defensible finding: in simulation, one common threshold opens an equal-opportunity gap of 6.59 pp [6.20, 6.97] when one group starts half a standard deviation lower. But the obvious explanation, the base rate, did not hold up: on the UCI Adult test file (group: hours-per-week below 40) the predicted gap reversed, -7.45 pp [-8.75, -6.05].

Caveat: simulated results hold only within the model; the real-data test covers one simple score and one non-protected partition. The groups are abstract, no protected attribute was used, and nothing here describes a real hiring decision or offers a universal fairness metric. Independent preprint draft, not peer-reviewed.

Code, manuscript and an offline interactive demo: https://github.com/mohamedbechirkefi/rigged-equal-rules · https://rigged-equal-rules.kefimohamedbechir.workers.dev

AI assistance (Claude, Anthropic) is disclosed in the manuscript.
