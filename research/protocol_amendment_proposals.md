<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# Proposed amendments to the draft protocol (for the owner, before the freeze)

| Field | Value |
|---|---|
| Date | 2026-11-24 (M2 session) |
| Applies to | `research/protocol.md` DRAFT v0.1 and `research/experiments/EXP-00{1,2,3}/protocol.md` DRAFT v0.1 |
| Status | Proposals only. None has been applied. The draft protocols were not edited. Accepting, changing or rejecting each proposal is the owner's decision (G-FREEZE). |
| Evidence | Exploratory runs JRN-0002 (SMOKE), JRN-0003 (SIZING), JRN-0004 (DEGEN) in `research/experiment_journal.jsonl`; outputs in `results/exploratory/`. All simulated, all exploratory, none a finding. |

## AP-001: Compute budget (planning value wrong by about two orders of magnitude)

- Draft: "under 30 minutes of wall-clock on the local laptop for the full matrix" (section 9); EXP-001 "under 5 minutes".
- Measured (SIZING, n = 20,000): mean time per run 6 to 11 ms by policy in a first execution and 21 to 38 ms in the recorded execution, which ran while the machine's load average was about 81. Projected full matrix (1,380 unique runs): 10.1 s and 34.5 s respectively. The analytic cross-check costs about 0.3 to 0.45 s per cell.
- Proposal: replace the budget with "under 5 minutes wall clock for the full matrix including reports" and record the measured values. The budget is not a constraint on the design.

## AP-002: Seed count and the rule for raising it

- Draft: 20 seeds; "If the smoke run shows a per-seed SD above 0.03, the seed count is raised to 50 before the freeze" (section 6). Planning estimate of the per-seed EOG SD: about 0.011.
- Measured at n = 20,000 (SIZING, 20 seeds): per-seed SD of the P0 EOG 1.05 pp (control cell) and 1.25 pp (primary cell), at most 1.73 pp over the P0 cells measured; SD of the primary paired difference 0.61 pp (common random numbers reduce it); 95% bootstrap half-width of the primary contrast 0.26 pp, against a smallest effect of interest of 2 pp. 20 seeds are adequate for the primary analysis.
- Problem: the rule is written for "the smoke run", but the smoke matrix uses n = 2,000, where the P0 EOG SD over 3 seeds was 3.78 pp and 4.77 pp, above the 3 pp trigger. Read literally, the rule would fire because of the smaller n, not because of the planned design. The rule also does not say which metric and policy it covers: the largest per-seed SD measured at n = 20,000 is 4.60 pp (P1, cell d1.00-r2.00).
- Proposal: (a) restate the trigger as "the per-seed SD of the primary metric under P0 at the planned n = 20,000"; (b) keep 20 seeds, or, because runs are cheap and master prompt section 3 asks for more seeds "if inexpensive", raise to 50 seeds for every experiment (projected cost under 2 minutes). Either choice must be fixed before the freeze.

## AP-003: Direction of EXP-001 H1b

- Draft: "at delta = 0, EOG increases with rho ... Direction to be confirmed analytically before freeze; if the analytic sign is ambiguous, H1b becomes non-directional."
- Analytic population values (numerical integration, `rigged.analytic.p0_population_metrics`, no simulation): at delta = 0, EOG = 0.000 pp (rho = 1), 0.177 pp (rho = 1.5), 0.081 pp (rho = 2). The relation is not monotone and every value is far below the 2 pp smallest effect of interest. For reference, at delta = 0.5: 6.307, 8.265, 9.008 pp; at delta = 1: 9.050, 13.369, 15.401 pp.
- Proposal: drop the directional H1b. Either make it non-directional, or restate it as an equivalence-style statement ("at delta = 0, |EOG| stays within 2 pp for every rho"), stating that non-significance is not equivalence unless a bounded interval is shown.

## AP-004: Exploratory seeds disjoint from confirmatory seeds

- Draft: the smoke matrix uses seeds 0 to 2, which are also confirmatory seeds. The populations differ (n = 2,000 versus 20,000), but the first 2,000 group-assignment uniforms of a seed are shared.
- Implemented now: the SIZING and DEGEN runs use seeds 1000 and above; `rigged.cli run --exploratory` refuses seeds 0 to 19.
- Proposal: state in section 6 that exploratory and test runs use seeds of 1000 and above, and move the smoke matrix to seeds 1000 to 1002.

## AP-005: Capacity tolerance of P3

- Draft (section 3): ties are broken "so that realised capacity matches kappa to within one individual".
- Implementation: this holds exactly for P0, P1 and P2 on the fitting population. P3 equalises TPR across groups by bisection on a common TPR; on a finite population the overall selected count can miss kappa * n. Measured maximum deviation over 160 P3 runs at n = 20,000: 5 individuals (0.025% of n).
- Proposal: state the P3 tolerance explicitly (for example "within 10 individuals, recorded per run as `fit_selected` and `fit_target`"), or require randomised group thresholds for exact capacity.

## AP-006: Knowledge available before the freeze (disclosure)

- The P0 population values of every planned cell can be computed now by numerical integration. The analytic check passed in all 28 metric-cell comparisons of the SIZING run (largest |z| = 2.21; criterion 3).
- The SIZING run (exploratory, seeds 1000+) contained four EXP-003 cells, chosen because their runtime or stability was least certain. One of them, B-sB2 (fixed base-rate gap, s_B = 2), has an analytic P0 EOG of -9.73 pp, opposite in sign to the primary cell. EXP-003 H2 (sign stability across s_B) is therefore already determined under the Gaussian model before any confirmatory run.
- Proposal: the frozen protocol should say that the hypotheses were finalised with the analytic values and this exploratory run available, and should present EXP-003 grids A and B as a quantification of a known analytic result rather than as a test with an unknown outcome. Grids C and D (non-Gaussian shapes, operating point) can stay as tests only if the owner accepts that exploratory estimates for three of those cells have also been seen.

## AP-007: The ECE gap does not vary across policies

- Draft (section 5): ECE_g is computed "for the group-blind calibrated score fitted on the fitting population". That score does not depend on the policy, so within a cell and seed the ECE gap is the same for P0, P1, P2 and P3 (visible in every exploratory table).
- Proposal: either keep it as a property of the score, reported once per cell and not compared between policies, or add a policy-specific calibration measure (for example the PPV gap at the selected margin, or the calibration of the score each policy thresholds).

## AP-008: P1 calibration resolution

- Implementation: P1 uses 20 quantile bins per group, as the draft specifies. The calibrated score is a step function, so the common threshold falls inside one bin and the seeded tie-break selects part of that bin at random. The P1 EOG per-seed SD reaches 4.60 pp (cell d1.00-r2.00), about 2.7 times that of P0 in the same cell.
- Check now implemented: each fitted bin rate agrees with the analytic Gaussian posterior P(Y = 1 | X) of its members within 4 binomial standard errors (`tests/test_analytic.py`), so the bins are correctly estimated; the extra spread comes from the step-function resolution near the threshold.
- Proposal: add a descriptive sensitivity analysis for P1 on the number of bins (for example 10, 20, 50), or define P1 on the analytic posterior as a second variant, so that P1 results are not an artefact of binning. Decide before the freeze.

## Not an amendment: degenerate cells

The DEGEN probe (n = 60) shows that empty groups, groups without qualified members and zero capacity give explicit failures or null metrics with reasons. No planned cell of EXP-001 to EXP-003 is degenerate: the SIZING run had no failure and no undefined value at n = 20,000, including the smallest planned group (p_B = 0.2, kappa = 0.1).
