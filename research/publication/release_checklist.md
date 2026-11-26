<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# Release checklist

Status (2026-11-25, M6; corrected 2026-11-26): release candidate 0.1.0-rc1 prepared and verified as recorded below. The repository is public at <https://github.com/mohamedbechirkefi/rigged-equal-rules> since 2026-11-25 (pushed on the owner's approval); no tag or release exists, and none is made without the owner's explicit approval (B16 sign-off, then B18). Each ticked item was verified in the M6 session; the evidence is named next to it.

- [x] Every registered experiment has a truthful standalone report (`research/experiments/EXP-NNN/report.md`; M3, with M4 corrections and addenda). M6: the four reports were rebuilt as PDFs and inspected; their figure captions were checked against the plotted columns (EXP-003 caption corrected); `rigged.cli report` rerun on the committed results in a clean clone left every generated file byte-identical.
- [x] Integrated manuscript complete; PDF compiled with the Typst chain and visually inspected (`scripts/build_pdfs.py`; `research/paper/manuscript.pdf`, 14 pages, every page inspected at 60 ppi; reproducibility report, section 3).
- [x] `manuscript.tex` regenerated from the final Markdown (`pandoc research/paper/manuscript.md -s -t latex`, pandoc 3.6.3, after the last manuscript edit).
- [x] Claims audit complete; every number traceable (M4: `claims_audit.md`, `evidence_audit.md`, `number_trace.csv`, `artifact_manifest.json`). M6: 21 of 21 result hashes and 45 of 45 config and protocol hashes in the artifact manifest match; external claims CLM-020 to CLM-024 checked against the full-text passages, CLM-021 and CLM-022 narrowed (evidence audit, section 9).
- [x] Reproducibility report complete with actual outputs (`reproducibility_report.md`: clean clone, 121 tests passed, M3 smoke reproduced exactly except runtime fields, demo 18 tests passed, `A11Y-CHECK PASS`, export deterministic).
- [x] README, CITATION.cff, NOTICE.md and data manifest current (README status and navigation updated; `CITATION.cff` repaired, `date-released` removed, version 0.1.0-rc1, title equal to the manuscript's, structure checked against CFF 1.2.0; `NOTICE.md` read and unchanged; `data/manifest.json` hashes match `data/raw/adult.zip`, 6 of 6).
- [x] Demo works offline after initial load; accessibility checks recorded (`node tools/a11y_check.mjs dist`: 9 PASS lines and `A11Y-CHECK PASS`, in the clean clone and in the working repository).
- [x] Articles (`articles/medium.md`, `articles/linkedin.md`) use the same verified results (`tests/test_demo_export.py::test_public_texts_use_only_manuscript_numbers`, passed).
- [x] Links, citations and quoted paths resolve (`python3 scripts/check_links.py`: PASS; `tests/test_links.py`, 3 passed).
- [x] Secret, identifier and licence scan (reproducibility report, section 5; `dependency_licences.md`: no dependency flagged).
- [ ] Owner sign-off of `author_review.md` (the owner only).
- [ ] Owner approval to publish, recorded in `research/decision_log.md` (G-PUBLIC; the owner only).

## Version and date at the release (owner, 2026-11-26, decision sheet, B8)

The release candidate keeps version `0.1.0-rc1` and no `date-released` in `CITATION.cff`. At the release, the version becomes `0.1.0` and `date-released` is set to the release day. `pyproject.toml` stays at `0.0.0`, because changing it would change the lockfile and the recorded environments.

## Release notes (draft)

- Figure 2 (EXP-002, `results/EXP-002/figures/XFIG-EXP-002-01-eog.svg`) is kept with its crowded, partly overlapping rotated axis labels, because it is a checksummed result file; every plotted value is in Supplementary Table S2 (owner, 2026-11-26, decision sheet, B11).
- External build and check tools are used but not redistributed by this repository: pandoc (GPL-2.0-or-later) for the PDFs, Google Chrome for the demo's accessibility check, the fonts bundled with the typst package (Libertinus Serif, OFL-1.1, embedded as subsets in the committed PDFs as that licence permits), and the MPL-2.0 packages listed in `dependency_licences.md` (lightningcss, build only; hypothesis, test only) (B13).
