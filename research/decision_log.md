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
