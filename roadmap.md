<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# Roadmap

Target: five focused development days (planning estimate). Effort is in focused days. Statuses: not started, in progress, done (all acceptance criteria checked), blocked.

| ID | Milestone | Depends on | Priority | Effort | Status | Blockers |
|---|---|---|---|---|---|---|
| M0 | Bootstrap and feasibility | none | P0 | 0.5 | done (2026-11-24), pending the owner's read of the gate | none |
| M1 | Research and preregistration | M0 | P0 | 0.75 | gate passed: protocols frozen (owner-approved 2026-11-24, `research/freeze.json`); full-text reading still open | none for M3 |
| M2 | Core implementation | M1 drafts (freeze not needed to implement) | P0 | 1.25 | done (2026-11-24): all acceptance criteria checked; exploratory runs only | none |
| M3 | Experiments | M1 freeze, M2 | P0 | 0.5 | not started (EXP-001 to EXP-004 frozen, not yet run) | the coordinator schedules M3 |
| M4 | Interpretation and evidence audit | M3 | P0 | 0.75 | not started | none |
| M5 | Interactive experience | M3 results (M4 for final labels) | P1 | 0.75 | not started | none |
| M6 | Release candidate | M4, M5 | P0 | 0.5 | not started | owner approval for any publication (G-PUBLIC) |

## M0: Bootstrap and feasibility

Acceptance criteria:

- [x] Control files of master prompt section 2 exist (`CLAUDE.md`, `roadmap.md`, `progress.md`, research files, data manifest, folders, README, LICENSE package, CITATION.cff, CONTRIBUTING.md, lockfile).
- [x] Section 11.1 tree initialised: registry, manuscript skeleton, publication checklists.
- [x] Feasibility audit with hardware and tools confirmed by commands (`research/feasibility.md`).
- [x] Zero-cost publication toolchain confirmed by an exploratory smoke check (pandoc to Typst to PDF; pandoc to LaTeX) (11.6 M0/M1).
- [x] Sources and dataset licences audited; unclear rights flagged.
- [x] Scope, cost (zero) and exclusions stated.
- Gate: the owner can understand the question, cost and exclusions (owner to confirm).

## M1: Research and preregistration

Acceptance criteria:

- [x] Draft project protocol with H0/H1, baseline, primary metric, secondary metrics, unit, seeds, sample-size rationale, uncertainty, exclusion and stopping rules, smoke and full matrices, sensitivity analysis.
- [x] EXP-001 to EXP-003 registered and given draft protocols (11.2).
- [ ] Full texts of the core sources read; definitions and theorem statements recorded; `references.bib` limited to verified entries.
- [ ] Analytic expressions for population TPR per group derived and written into the protocol (needed for the cross-check and for H1b's direction). Implemented numerically in `src/rigged/analytic.py` and used for AP-003; not yet written into the protocol text (owner's draft).
- [x] Smoke run (exploratory) measures the per-seed SD and runtime (JRN-0002 to JRN-0004). Seed count: 20 adequate at n = 20,000; the owner decides the trigger wording and whether to raise to 50 (AP-002).
- [ ] Fixture manifest for golden tests. Golden examples are inline in `tests/` (hand-computed); a separate manifest file is not written yet.
- [x] Owner freezes the protocols; protocol hashes recorded in the registry (G-FREEZE). Done 2026-11-24 with real data for EXP-004 (UCI Adult); freeze record `research/freeze.json`, content revision 48f0652.
- Gate: protocol frozen before confirmatory runs; exploratory results visibly separated.

## M2: Core implementation (11.6: schemas, manifests and report generators alongside the core)

Acceptance criteria:

- [x] Generator, policy P0 first, then P1 to P3, metrics; pure functions, typed, seeded (`src/rigged/`).
- [x] Unit tests: confusion matrices, group counts, zero denominators, threshold monotonicity; property tests; golden hand-computed fixtures; analytic differential test (101 tests, all passing on 2026-11-24).
- [x] Versioned JSON result schema with validation; run manifest (runtime, peak memory, OS, CPU, package versions, git revision, config hash).
- [x] CLI: smoke, run (refuses confirmatory while unfrozen), report, test.
- [x] Report generator producing tables and figures from results (CSV, Markdown, SVG; PDF through pandoc and Typst, visually inspected).
- Open items carried forward: proposed protocol amendments AP-001 to AP-008 (`research/protocol_amendment_proposals.md`) await the owner.
- Gate: correctness before UI polish.

## M3: Experiments (11.6: reports as experiments finish; provenance at run time)

Acceptance criteria:

- [ ] Smoke matrix run and validated. (Run exploratorily in M2, JRN-0002; to be rerun under the frozen protocol.)
- [ ] Frozen full matrix run for EXP-001 to EXP-004; every run, failure and deviation exported.
- [ ] Per-experiment report drafted as each finishes.
- Gate: complete planned matrix or documented failure; no silently dropped runs.

## M4: Interpretation (11.6: finish reports, evidence audit, manuscript synthesis)

Acceptance criteria:

- [ ] Confounders and sensitivity (EXP-003) analysed; expected versus observed compared.
- [ ] Claims register and claims audit complete; artifact manifest complete.
- [ ] Manuscript synthesised, including contradictory and null results.
- [ ] Second review pass challenging the preferred hypothesis.
- Gate: every numerical claim maps to result ID, config and figure; every external claim to a verified source.

## M5: Interactive experience (11.6: identical results and labels across outputs)

Acceptance criteria:

- [ ] Static fairness trade-off explorer and subgroup outcome charts; measured results separated from sandbox results.
- [ ] Accessibility: keyboard, contrast, reduced motion, mobile; empty, error and loading states; fail closed on malformed results.
- [ ] Offline after initial load; no runtime service.
- Gate: as above.

## M6: Release candidate (11.6: PDFs inspected, clean-clone reproduction, owner checklist)

Acceptance criteria:

- [ ] Clean clone, locked install, tests, smoke reproduction, demo build, manifest and link checks, secret and licence scans, with actual outputs.
- [ ] Manuscript and report PDFs compiled and visually inspected.
- [ ] Owner review checklist completed.
- Gate: verified facts only; the owner approves any publication.

## Cut order if the five-day target is threatened

Experimental cuts are made before the freeze (master prompt 11.6); after the freeze, any cut is a documented deviation.

1. Demo extras beyond the trade-off explorer and subgroup charts.
2. EXP-003 grid C (non-Gaussian shapes).
3. Policy P1.
Never cut: controls, experiment reports, claims audit, uncertainty reporting.
