<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# Decision log

Append-only. Each entry: id, date, decision, who decided, context, alternatives, consequences.

## DEC-001 (2026-11-24): Licence is the owner's custom non-commercial research licence

- **Decided by:** the owner.
- **Decision:** All original material is licensed under the "RIGGED Source-Available Non-Commercial Research License v1.0" (SPDX `LicenseRef-RIGGED-NC-Research-1.0`), with a Contributor License Agreement (`CLA.md`).
- **Context:** Master prompt section 2 asks for an "owner-approved permissive code license". On 2026-11-24 the owner chose this protective licence instead, for their own protection. The licence package was committed in the first commit.
- **Alternatives:** a permissive licence (MIT, Apache-2.0), as the prompt suggested; not chosen by the owner.
- **Consequences:** The project is source-available, not OSI open source. Sessions do not change the licence files. Third-party data and dependencies keep their own licences (`data/manifest.json`, `uv.lock`). `CITATION.cff` names the licence in a comment rather than an SPDX licence field.

## DEC-002 (2026-11-24): Zero-cost publication toolchain without TeX

- **Decided by:** the AI assistant, following the session brief; open to owner review.
- **Decision:** Markdown is canonical. PDFs are produced with pandoc 3.6.3 (Markdown to Typst) and the `typst` 0.15.0 Python package. `manuscript.tex` is generated with pandoc and is not compiled locally.
- **Context:** No TeX distribution is installed (`which pdflatex xelatex tex` finds nothing). Installing one is possible but unnecessary.
- **Consequences:** PDF layout follows Typst defaults plus a project template; the LaTeX source is provided for venues that need it but is untested locally.

## DEC-003 (2026-11-24): Synthetic data only; no external dataset

- **Decided by:** the AI assistant (proposal); confirmed only when the owner freezes the protocol.
- **Decision:** All experiments use the project's own seeded synthetic generator. UCI Adult, folktables (ACS PUMS) and the ProPublica COMPAS data are documented but not used.
- **Context:** The question is about starting distributions, which a generator controls exactly. Real datasets would introduce real demographic groups, which the claims boundary excludes, and COMPAS has no stated licence.
- **Consequences:** Results hold only within the generator's assumptions; this is stated in every report.

## DEC-004 (2026-11-24): Draft primary metric is the equal-opportunity gap (proposal)

- **Decided by:** the AI assistant (proposal pending owner freeze).
- **Decision:** Primary metric EOG = TPR_A - TPR_B; baseline policy P0 (common raw-score threshold); primary contrast delta = 0.5 versus delta = 0 at rho = 1; smallest effect of interest 2 pp.
- **Alternatives:** selection-rate gap (rejected as primary: it differs whenever base rates differ and does not compare equals); PPV gap; utility. All are reported as secondary.
- **Consequences:** See `research/protocol.md` sections 4 and 5. The owner may change this before freezing.

## DEC-005 (2026-11-24): Dependency pinning with an upload cut-off

- **Decided by:** the AI assistant, following the session brief.
- **Decision:** `pyproject.toml` pins numpy 2.5.4, jsonschema 4.26.0, pytest 9.2.0, hypothesis 6.170.15; `[tool.uv] exclude-newer = "2026-11-10T00:00:00Z"` keeps every resolved distribution at least two weeks older than 2026-11-24. `uv.lock` was produced with uv 0.9.5.
- **Consequences:** Upgrades require a dated decision entry.

## DEC-006 (2026-11-24): No SciPy; numerical functions implemented and tested in the package

- **Decided by:** the AI assistant (M2); open to owner review.
- **Decision:** The normal CDF (Hart's double-precision approximation), quantiles, latent-family distributions and the Student t quantile are implemented in `src/rigged/numerics.py`; the dependency set stays numpy and jsonschema.
- **Context:** Only a few special functions are needed. Each is tested against the standard library (`math.erfc`, `statistics.NormalDist`) or tabulated values.
- **Consequences:** No new dependency, `uv.lock` unchanged.

## DEC-007 (2026-11-24): Exploratory runs use seeds of 1000 and above

- **Decided by:** the AI assistant (M2), as a safeguard; proposed for the protocol as AP-004.
- **Decision:** The SIZING and DEGEN exploratory matrices use seeds 1000 and above; tests use seeds 2000 and above or 5000 and above; `rigged.cli run --exploratory` refuses the confirmatory seeds 0 to 19. The protocol's own smoke matrix (seeds 0 to 2, n = 2,000) was run as written.
- **Consequences:** No confirmatory seed was evaluated at the planned n before the freeze.

## DEC-008 (2026-11-24): What "frozen" means to the code

- **Decided by:** the AI assistant (M2); open to owner review.
- **Decision:** `rigged.protocol_guard` treats an experiment as frozen only if its registry row has a protocol hash equal to the SHA-256 of its protocol file and neither that protocol nor `research/protocol.md` declares DRAFT in its header. Otherwise `run` refuses (exit code 2). The code never writes a hash.
- **Consequences:** At freeze, the owner records the hash (`shasum -a 256 research/experiments/EXP-NNN/protocol.md`) in the registry and removes the DRAFT status.

## DEC-009 (2026-11-24): P3 fitting by bisection on a common TPR

- **Decided by:** the AI assistant (M2); open to owner review.
- **Decision:** P3 thresholds select, in each group, the top round(tau * qualified) qualified scores; tau is found by bisection so the overall count is as close to kappa * n as the finite population allows. Realised fitting TPR gap and count are recorded per run. The tolerance question is raised as AP-005.

## DEC-010 (2026-11-24): The package is run from `src/` without installation

- **Decided by:** the AI assistant (M2).
- **Decision:** `pyproject.toml` keeps `package = false`; pytest uses `pythonpath = ["src"]`; the CLI runs as `scripts/rigged` or `PYTHONPATH=src uv run --frozen python -m rigged.cli`. Installing a build backend would add a download for no benefit.
- **Consequences:** The reproduction commands in the EXP protocols (`uv run python -m rigged.cli ...`) need `PYTHONPATH=src` or `scripts/rigged`; this is noted for the owner and not edited in the draft protocols.

## DEC-011 (2026-11-24): UCI Adult adopted for a second test (EXP-004); DEC-003 superseded for EXP-004 only

- **Decided by:** the owner ("Approve all", second round; approvals file section 1: "UCI Adult, CC BY 4.0, second test on a real score distribution"). Design details by the AI assistant under that approval.
- **Licence check:** dataset page https://archive.ics.uci.edu/dataset/2/adult, opened 2026-11-24: "This dataset is licensed under a Creative Commons Attribution 4.0 International (CC BY 4.0) license." DOI 10.24432/C5XW20. Matches the approval.
- **Data:** `adult.zip` from https://archive.ics.uci.edu/static/public/2/adult.zip, 620,237 bytes, SHA-256 7537312dd56c2b98035880805ce99e68183a30ee468aa5329d6df0fbb3cc21bb, downloaded by `scripts/download_adult.py`. CC BY and under 20 MB, so committed with attribution (approvals redistribution rule). No direct personal identifier; only six columns are used.
- **Use:** score model (logistic regression on age, education-num, log1p capital-gain, log1p capital-loss) fitted on `adult.data` only (JRN-0005), method written into the protocol before the fit; EXP-004 tests on `adult.test`: Group B = hours-per-week below 40 versus a random-permutation control, P0 to P3, 20 seeds. No synthetic parameter is calibrated: the synthetic factors are design choices, not estimates.
- **Alternatives:** groups by sex or race (rejected: protected groups are outside the claims boundary); calibrating sigma_A from the real score's discrimination (rejected: not the approved role, and it would change the primary synthetic design).
- **Consequences:** EXP-004 registered and frozen. The partition is a stated agent choice for the owner to ratify.

## DEC-012 (2026-11-24): Approved amendments A1 to A6 applied before the freeze

- **Decided by:** the owner ("yes for all others"; approvals file section 7, RIGGED).
- **Decision:** A1 EXP-003 sign test reported as analytically determined; A2 20 seeds, conditional raise removed; A3 budget under 5 minutes; A4 H1b not monotone, stated, non-directional; A5 P3 capacity tolerance of 10 individuals, enforced in code as a recorded failure; A6 exploratory seeds 1000 and above, smoke matrix moved to 1000 to 1002. AP-007 and AP-008 were not in the approved list and were not applied.

## DEC-013 (2026-11-24): EXP-004 P3 tolerance of 30 individuals (agent choice, to ratify)

- **Decided by:** the AI assistant, before any test-file metric; open to owner ratification.
- **Context:** the real score has ties (4,257 distinct values in 32,561 training rows). A training-file check with random partitions (JRN-0006) found P3 count deviations up to 19 individuals, 4 of 20 above A5's 10.
- **Decision:** tolerance 30 for EXP-004 only; A5's 10 stays for EXP-001 to EXP-003.
- **Alternatives:** keep 10 (about 20% of EXP-004 P3 runs would fail and could halt the cell under section 8); randomised group thresholds for P3 (a change to the policy itself, not approved).

## DEC-014 (2026-11-24): Freeze mechanics (G-FREEZE, owner-approved)

- **Decided by:** the owner approved the freeze; mechanics by the AI assistant.
- **Decision:** confirmatory configs are the canonical export of each matrix (`research/experiments/EXP-NNN/config.json`, including every run's config hash; EXP-004 also embeds the fitted score model and the archive hash). `research/freeze.json` holds the approvals, C1 to C4, the SHA-256 of the project protocol, of each experiment protocol and config, of the data manifest, and the frozen content revision 48f0652. `run` refuses unless the registry hash, the freeze record, the protocols, the config file, the config built by the current code and (EXP-004) the data manifest all match. `export-configs` refuses to rewrite a frozen config. Extends DEC-008.

## DEC-015 (2026-11-24): fit_threshold fallback for subnormal tie uniforms

- **Decided by:** the AI assistant.
- **Context:** a Hypothesis example (tie uniforms 0.0 and 5e-324) made the midpoint round onto the lower value, so `fit_threshold` raised "tie uniforms collide". Generator uniforms are multiples of 2^-53, so no planned run can hit this.
- **Decision:** when the midpoint fails but the two uniforms differ, gamma = the upper uniform (selects the same individuals). Behaviour is unchanged in every other case; config hashes unchanged.

## DEC-016 (2026-11-24): EXP-004 primary group attribute is sex; hours-per-week below 40 is secondary (pre-data amendment)

- **Decided by:** the owner ("Approve all", 2026-11-24, round 3; `owner-approvals-2026-11-24c.md`, section 1): "The primary comparison in EXP-004 (UCI Adult) uses **sex** as the group attribute. This is the standard comparison for this dataset. Hours-per-week below 40 stays as a secondary check. Nothing has been computed on the test file. Keep it that way until the confirmatory run." Mechanics by the AI assistant.
- **Decision:** dated pre-data amendment to the frozen v1.0 protocols (project protocol section 13, round 3, R3-1 to R3-10; EXP-004 protocol v1.1, section 10). Cells R-sex and R-sex-random (primary contrast), R-hours and R-hours-random (secondary contrast; R-random renamed). Group B of R-sex set by a rule written into the protocol before it was applied: the sex value with the lower base rate on `adult.data` (JRN-0007: Female 0.1095, Male 0.3057; Group B = Female). Same draws per seed; 320 runs. A kept row with sex other than Male or Female is a schema error. The EXP-004 claims boundary is rewritten for a protected attribute. Nothing was computed on `adult.test`.
- **Alternatives:** keep hours as primary (overruled by the owner); a sex-random control built with a fresh permutation per attribute (rejected: one shared index permutation keeps the common random numbers of round 2).
- **Consequences:** supersedes DEC-011's rejection of sex as a group attribute for EXP-004. New hashes in `research/freeze.json`; superseded hashes kept there with the reason. The master prompt (section 2) excludes "protected-group claims"; the owner's decision is applied with claims limited to this partition of this file (flagged in `progress.md`).

## DEC-017 (2026-11-24): EXP-004 P3 capacity tolerance of 30 ratified

- **Decided by:** the owner ("Approve all", 2026-11-24, round 3): "The P3 capacity tolerance of 30, needed because real scores contain ties, is ratified."
- **Decision:** DEC-013 stands, now owner-ratified, for all four EXP-004 cells. Listed under `owner_ratifications` in `research/freeze.json`.

## DEC-018 (2026-11-25): EXP-004 grouping, option A: hours-per-week below 40 primary, sex removed (pre-data amendment)

- **Decided by:** the owner, 2026-11-25, "approve all recommendations, RIGGED A" (`owner-approvals-2026-11-25.md`, item 1, which replaces item 1 of `owner-approvals-2026-11-24c.md`): "EXP-004's primary group attribute is hours-per-week below 40." Sex is "not used in any confirmatory or exploratory analysis. This respects the master prompt's claims boundary: 'No real hiring decisions or protected-group claims; do not suggest a universal fairness metric.'" "The P3 capacity tolerance of 30 is still ratified." Mechanics by the AI assistant.
- **Decision:** dated pre-data amendment to the frozen v1.1 protocols (project protocol section 13, A25-1 to A25-9; EXP-004 protocol v1.2, section 11), written into the protocols before code was changed (commit 4daea38). Cells R-hours (primary) and R-hours-random (control), 160 runs, same draws. R-sex and R-sex-random withdrawn; sex is no longer a used column; JRN-0007 (training-file base rates by sex) withdrawn from use. History is not rewritten: commits 97de686 and 50aac6b stay as the record of the superseded round-3 design.
- **Consequences:** supersedes DEC-016 (DEC-017 stands). Resolves the conflict with the master prompt and `CLAUDE.md` flagged in round 3. New hashes in `research/freeze.json`; v1.1 hashes kept under `superseded` with the reason. Nothing was computed on `adult.test` before or during the amendment.

## DEC-019 (2026-11-25): EXP-003 implementation check failed on 4 of 60 comparisons (deviation, for the owner)

- **Decided by:** the AI assistant records it; the owner decides what follows.
- **Context:** protocol section 7 requires the simulated P0 seed means to agree with the population values within 3 bootstrap SE ("implementation check, not a hypothesis test"); EXP-001 section 12 treats disagreement as an implementation bug. On the confirmatory seeds, EXP-001 and EXP-002 passed 48/48 each; EXP-003 passed 56/60. Outside: D-k0.1-pB0.5 EOG (z -3.08) and SR gap (z -4.07); D-k0.5-pB0.2 FPR gap (z 5.05) and PPV gap (z -3.38).
- **Action:** nothing was changed or rerun as confirmatory. One exploratory diagnosis (JRN-0014): the same frozen matrix on seeds 1000 to 1019 passed 60/60 (largest |z| in those cells 1.72). This suggests a realisation of the confirmatory seed set, shared by all cells under common random numbers, rather than a code fault; it is not proof.
- **Consequences:** EXP-003 results are reported in full with the failed check stated; H4 (grid D) carries the caveat. The owner may accept it as a disclosed limitation or ask for an investigation.

## DEC-020 (2026-11-25): M3 execution choices and minor deviations

- **Decided by:** the AI assistant, before any confirmatory output, except where stated.
- **Decision:**
  - Provenance revision b455d59 (tree clean; all frozen hashes matched; 116 tests passed; archive SHA-256 matched). `scripts/run_confirmatory.sh` runs each experiment through the guard, then the report generator, then `scripts/write_provenance.py` (exit status, times, data manifest, config and protocol hashes, per-run id, config hash, seed, status and runtime, file hashes).
  - Smoke and metric validation were written to new directories (`results/exploratory/m3-smoke`, `m3-sizing`) so the M2 outputs are kept.
  - EXP-001 and EXP-002 were run as separate matrices, so the 240 shared P0 runs were computed twice rather than once (EXP-002 protocol section 6). The two copies are identical apart from runtime (checked on every summary field).
  - EXP-004's descriptive base-rate gap (protocol section 3) is not produced by the report generator; `scripts/exp004_base_rates.py` was written after the run to compute it from `results.json` with the frozen interval method. No other analysis was added.
  - EXP-002's tolerance sensitivity (1 pp and 5 pp, protocol section 10) is read from the committed intervals; no new computation.
- **Owner decision recorded:** item 4 of `owner-approvals-2026-11-25.md` ("approve all recommendations, RIGGED A"): the 11.3/11.6 experiment reports are written from committed results only. Per the coordinator's instruction, the coordinator writes `research/experiments/EXP-NNN/report.md` and `reproduction.md`; this session returned their text.

## DEC-021 (2026-11-25): DEC-019 is a disclosed limitation on EXP-003 H4; nothing is rerun

- **Decided by:** the owner, 2026-11-25, "Approve all recommendations, push then next" (`owner-approvals-2026-11-25b.md`, item 2): "The EXP-003 implementation-check failures (4 of 60) are a disclosed limitation on H4. Nothing is rerun."
- **Decision:** EXP-003 keeps its frozen verdicts. H4 is reported as supported in sign, with the limitation stated wherever H4 appears (EXP-003 report, manuscript sections 5.3 and 7, CLM-009, CLM-011, `research/limitations.md`). No confirmatory or further exploratory rerun.
- **Consequences:** closes the open item of DEC-019.

## DEC-022 (2026-11-25): M4 choices (exploratory checks, audit, manuscript)

- **Decided by:** the AI assistant, under the M4 brief (`labs/_shared/M4-brief.md`), except where stated.
- **Decision:**
  - Two cheap exploratory checks, both in one process (8.6 s), written to `results/exploratory/m4-confounders/` by `scripts/m4_exploratory.py`:
    - JRN-0015 checks the protocol's named confounder "calibration-fit error in P1", which had no policy-level committed evidence. It uses the exact Gaussian posterior by numerical integration, with an in-session Monte Carlo cross-check in three cells.
    - JRN-0016 describes the EXP-004 score on the full test pool by the hours partition only. No protected attribute is used and no model is fitted.
    - Neither check changes a frozen verdict.
  - Evidence audit by `scripts/m4_evidence_audit.py`: per-run identities, an independent re-derivation of the summary and contrast tables, SHA256SUMS, and a number trace for the manuscript, the supplementary file, the reports and the claims register. The artifact manifest is built by `scripts/build_artifact_manifest.py` and the supplementary file by `scripts/build_supplementary.py`, both from committed tables.
  - One wrong number corrected in the EXP-001 report: the C4 SIZING value 6.31 became 6.30 pp. Stale status text corrected in the EXP-003 report and the registry. Two short M4 addenda appended to the EXP-002 and EXP-004 reports; their frozen verdicts and existing text are unchanged.
  - Claims register: new columns (experiment, run IDs, config hash, figure or table, manuscript section). Rows CLM-016 to CLM-030 added, CLM-020 to CLM-025 being external claims marked abstract-only. CLM-012 narrowed to "contradiction of the base-rate prediction".
  - Manuscript synthesised to master prompt 11.4, then revised after the second review pass (`research/publication/review_pass_2.md`, section 3).
  - `research/freeze.json` and the frozen protocols, configs and seeds are not touched.
- **Alternatives:** a P1 binning sensitivity by simulation (rejected: it would be a new analysis with no frozen config, and integration answers the protocol's question directly); per-seed bootstrap intervals for JRN-0016 (rejected: the check is descriptive, and the confirmatory intervals already exist).


## DEC-023 (2026-11-25): Funding, competing-interest and AI-use statements approved by the owner (post-M4 item 2)

- **Date:** 2026-11-25
- **Decided by:** the owner: owner, 2026-11-25, "Approve all" (post-M4), item 2 (`/Users/bechir/research/labs/_shared/owner-approvals-2026-11-25c.md`): "The wording drafted in each manuscript is approved. Where a draft still has a placeholder that needs a fact only the owner knows, it stays a placeholder. M5 lists any such placeholder for the owner." Recorded by the AI assistant under the coordinator brief `/Users/bechir/research/labs/_shared/POST-M4-brief.md`.
- **Decision:** the funding, competing-interest and AI-use wording in manuscript section 11 (`research/paper/manuscript.md` as of commit `69f4227`) is owner-approved. No wording was changed. Placeholders that need a fact only the owner knows stay as placeholders and are listed in `progress.md` under "Owner placeholders for M5".
- **Consequences:** no change to the manuscript, protocols, configs, seeds or results; no computation; `research/freeze.json` untouched. The unticked boxes in `research/publication/author_review.md` are left for the owner.

## DEC-024 (2026-11-25): M5 interactive experience: stack, data export, sandbox, records

- **Date:** 2026-11-25
- **Decided by:** the owner started M5: owner, 2026-11-25, "Next" (`/Users/bechir/research/labs/_shared/owner-approvals-2026-11-25d.md`). That record names the stack: "The master prompt's default stack is used: TypeScript, React and Vite. Versions are pinned and come from the shared template, `labs/_shared/demo-template/`, which was verified on 2026-11-25." The choices below were made by the AI assistant under the coordinator brief `labs/_shared/M5-brief.md`.
- **Decision:**
  - **Stack.** `demo/` is a copy of the shared template (React 19.3.1, Vite 8.3.5, vitest 4.1.12, TypeScript 5.9.3), with its `.npmrc` and lockfile. No pinned version changed and no dependency was added. Charts are hand-written SVG.
  - **Data.** `scripts/export_demo_data.py` writes `demo/public/data/results.json` (schema `lab-demo-results` 1.0.0) from committed tables, the registry, the claims register and the artifact manifest only. One entry per registered experiment (EXP-001 to EXP-004) plus the three exploratory checks (JRN-0014 to JRN-0016), each with status, frozen-rule verdict and claim IDs. Display strings are formatted from table values at the manuscript's precision; `code_revision` is the confirmatory revision b455d59 from the manifest; no timestamps. Extensions `explorer` (EXP-002 grid), `real_score` (EXP-004) and `display_exceptions` are validated fail-closed in `demo/src/results.ts`.
  - **Exact numbers.** `tests/test_demo_export.py` re-runs the export in memory and checks byte identity, and checks that every display string is verbatim in the manuscript. Two documented exceptions: per-cell explorer values are checked verbatim against `research/paper/supplementary.md` (tables S2, S3, S5); group-level true positive rates (TPR_A, TPR_B) are not printed in the manuscript and are listed as `group-rate`. The same test checks that README, CITATION.cff, the article drafts and `demo/README.md` print no decimal number absent from the manuscript or supplementary file.
  - **Visual.** The roadmap and master prompt name a "fairness trade-off explorer and subgroup outcome charts". The explorer shows four gap panels (SR, EOG, PPV, FPR) for P0 to P3 with 95% intervals and the 2 pp band, for any of the 12 EXP-002 cells or the two EXP-004 cells; the subgroup chart shows each group's true positive rate with intervals.
  - **Sandbox: faithful port of the engine logic, with its own random numbers.** `demo/src/engine.ts` ports the Gaussian generator, P0 to P3 (including numpy's linear quantile, round half to even and the P3 bisection) and the metrics. `demo/src/engine.test.ts` feeds it the Python engine's own numpy draws (fixture from `scripts/make_demo_fixture.py`: n = 600, exploratory seed 1000, two cells, under one second of compute, one process) and requires counts to match exactly and every metric within 1e-9; it passes. The sandbox's random numbers come from mulberry32 and Box-Muller, not numpy's PCG64, so sandbox seeds do not reproduce research seeds; a second test checks that the mean P0 EOG over 10 sandbox seeds at the primary cell lies within 3 SE of the population value. The page states this and labels all sandbox output "Sandbox output, not a research result". Bounds: 10 seeds, 20,000 individuals per population, cancellable Web Worker.
  - **Checker.** `demo/tools/a11y_check.mjs` is the template's, unchanged except for the SPDX header; to let its keyboard check count each results table once, the tables were given distinct ids in the page (the checker was not relaxed).
  - **Author review checklist.** Four boxes in `research/publication/author_review.md` had been ticked by AI sessions to record owner decisions (freeze, metric and baseline, data, DEC-019). They were unticked, because only the owner ticks a box; each item now cites its recorded decision.
  - **Text consistency.** Manuscript section 11: "The owner has not yet reviewed this manuscript's text" replaced by the true state (statements approved on 2026-11-25, DEC-023; full-text review pending, M6). Manuscript section 10 gains a paragraph describing the demo, with a demo-URL placeholder; version line M5; `manuscript.tex` regenerated with pandoc 3.6.3. README rewritten from its M2 state; CITATION.cff status message updated; `articles/medium.md` and `articles/linkedin.md` drafted (they did not exist); `demo/README.md` written.
- **Alternatives:** an exact port of numpy's PCG64 and ziggurat normal sampler (rejected: large and fragile for no gain in what the sandbox can show; identity on given draws is tested instead); no sandbox (rejected: the port is faithful on identical draws).
- **Consequences:** no frozen protocol, config, seed or result changed; no confirmatory run; nothing pushed. Owner placeholders remain: author line and affiliation, repository URL, demo URL. The manuscript title was not among the titles approved on 2026-11-25 (that approval named other projects), so it stays a working title.
