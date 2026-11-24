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
