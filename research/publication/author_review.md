<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# Owner review

Status: updated at M6 (2026-11-25); owner answers of 2026-11-26 recorded below. Items the owner must decide or approve. Only the owner ticks a box; at M6 no box was ticked and none had been ticked by an agent since M5. At M5, four boxes that an AI session had ticked to record owner decisions were unticked (DEC-024); the decisions themselves stand and are recorded in the decision log, cited next to each item.

- [ ] Freeze the project protocol and the EXP-001 to EXP-004 protocols (G-FREEZE). Recorded as decided by the owner on 2026-11-24, with the pre-data amendments of 2026-11-24 and 2026-11-25 (DEC-012, DEC-016 to DEC-018).
- [ ] Confirm the primary metric (equal-opportunity gap), the baseline (P0) and the 2 pp smallest effect of interest. Recorded as frozen with the protocols.
- [ ] Data decision: synthetic data for EXP-001 to EXP-003; UCI Adult for EXP-004. Recorded as decided by the owner (round 2, DEC-011; DEC-003 superseded for EXP-004).
- [ ] DEC-019: a disclosed limitation on H4, with no rerun. Recorded as decided by the owner (2026-11-25, DEC-021).
- [ ] Review the manuscript text (`research/paper/manuscript.md`, M5 version) and supplementary file, including the reading of EXP-004 as a contradiction of the base-rate prediction (`research/publication/review_pass_2.md`, R3).
- [ ] Approve author and affiliation metadata (currently: Mohamed Bechir Kefi, independent researcher, the form the owner chose on 2026-11-26, B3).
- [ ] Approve the AI-assistance disclosure text (manuscript section 11). Recorded as approved by the owner with the funding and competing-interest statements on 2026-11-25 (DEC-023).
- [ ] Decide whether full-text reading of the cited sources is required before release (at M6 the full text of each paper was opened and the cited passage checked; none was read in full).
- [ ] Review the demo (`demo/`, M5) and the article drafts (`articles/medium.md`, `articles/linkedin.md`).
- [ ] Supply the repository URL and the demo URL at a release decision (filled on 2026-11-26 from the owner's answers B1 and B2).
- [ ] Approve any publication, push or release (G-PUBLIC).

## Prepared for the owner (M6, 2026-11-25)

Release candidate 0.1.0-rc1 is prepared. Correction (2026-11-26): the repository was pushed and is public at <https://github.com/mohamedbechirkefi/rigged-equal-rules> since 2026-11-25; nothing is tagged or released. Under owner, 2026-11-25, "Next" (second) (`labs/_shared/owner-approvals-2026-11-25e.md`), this section lists what to read for each box and every open decision; it decides none of them.

### What to read for each box

1. **Protocol freeze:** `research/freeze.json`; `research/protocol.md`; `research/experiments/EXP-001/protocol.md` to `EXP-004/protocol.md`; decision log DEC-012 and DEC-016 to DEC-018.
2. **Primary metric, baseline, smallest effect:** `research/protocol.md`, sections 3, 5 and 7; manuscript section 4.5.
3. **Data decision:** `data/manifest.json`; manuscript sections 4.4 and 8; decision log DEC-011.
4. **DEC-019 limitation on H4:** `research/experiments/EXP-003/report.md`, sections 7 and 8; decision log DEC-019 and DEC-021.
5. **Manuscript text and supplementary file:** `research/paper/manuscript.pdf` (14 pages) or `manuscript.md`; `research/paper/supplementary.pdf`; for the EXP-004 reading, `research/publication/review_pass_2.md`, challenge R3, and `research/publication/interpretation.md`, section 4. New at M6: section 2 now names the section or theorem checked in each source, and two statements were narrowed (Pleiss et al.; Corbett-Davies et al.).
6. **Author and affiliation metadata:** manuscript line 4; `CITATION.cff` (authors); README "Citation".
7. **AI-assistance disclosure:** manuscript section 11 (approved with the funding and competing-interest statements, DEC-023; unchanged at M6).
8. **Full-text reading of sources:** `research/literature_review.md`, section 5; `research/publication/evidence_audit.md`, section 9.
9. **Demo and article drafts:** `demo/` (build: `cd demo && npm ci && npm run build && npm run preview`); `docs/demo.png`; `articles/medium.md`; `articles/linkedin.md`.
10. **Repository and demo URLs:** the placeholders listed below.
11. **Publication:** `research/publication/release_checklist.md`; `research/publication/reproducibility_report.md`; `research/publication/dependency_licences.md`.

### Open decisions for this repository

- Whether to tag or release anything, and under which licence terms, is the owner's decision (G-PUBLIC); M6 released nothing. The push of 2026-11-25 was made on the owner's approval.
- Whether the five protocols are recorded as frozen by the owner is for the owner to confirm by ticking the first box (the decision is recorded in DEC-012 and DEC-016 to DEC-018).
- Settled on 2026-11-26 (see the next section): the manuscript title, the author line and affiliation, and the repository and demo URLs.
- The owner has not yet reviewed the manuscript text, including the reading of EXP-004 as a contradiction of the base-rate prediction.
- The owner may decide whether the passage-level check of the cited sources is enough, or whether full reading is required before release.
- Figure 2 (EXP-002) is kept as it is, with a release-note line (owner, 2026-11-26, B11).
- `CITATION.cff` has no `date-released`; at the release the version becomes 0.1.0 and `date-released` the release day (owner, 2026-11-26, B8).
- The CLA and licence files are unchanged and remain the owner's decision.

### Owner placeholders remaining (updated 2026-11-26)

The placeholders listed at the M6 commit (author line, repository URL, demo URL, working-title marks) were filled or removed on 2026-11-26 under the owner's answers (next section). No repository-URL, demo-URL, author or title placeholder remains in an editable file. One pending mark stays on purpose, because it is true until the owner's review:

| File | Line | Text |
|---|---|---|
| `research/paper/manuscript.md` | 279 | "the owner's full-text review of this manuscript is pending (M6 owner checklist)" (B16) |

`research/paper/manuscript.tex` and the PDFs were regenerated from the updated `manuscript.md`.

## Owner answers recorded (2026-11-26)

Source: owner, 2026-11-26, decision sheet (`labs/_shared/owner-decision-sheet-2026-11-26.md` for the ids, `labs/_shared/owner-approvals-2026-11-26.md` for the answers). Applied in this repository under DEC-026. No box above is ticked by this record.

- **A1:** the repository has been public since 2026-11-25; the out-of-date "prepared locally / nothing pushed" sentences in this file and `release_checklist.md` were corrected. Append-only records keep their dated wording.
- **B1:** repository URL <https://github.com/mohamedbechirkefi/rigged-equal-rules> in the manuscript (section 10), README, articles, demo footer and `CITATION.cff` (`repository-code`).
- **B2:** demo hosted as Cloudflare Workers static assets (free plan) at <https://rigged-equal-rules.kefimohamedbechir.workers.dev>, deployed by the coordinator; `demo/wrangler.jsonc` added (assets only, directory `./dist`).
- **B3:** author line "Mohamed Bechir Kefi, independent researcher" in the manuscript, the four experiment reports, README, `articles/medium.md` and the demo footer; `CITATION.cff` `affiliation: "Independent researcher"`. `research/freeze.json` (C3, "no affiliation") is frozen and unchanged.
- **B4:** funding none and competing interests none; the manuscript already printed both, with no "to be confirmed" mark.
- **B5, B12:** do not apply to this repository.
- **B6, B7:** the manuscript title "When equal rules produce unequal outcomes: a seeded simulation of one common threshold, with a contradicting test on a real score" is approved; "working title" marks removed (README, `CITATION.cff` message); `CITATION.cff` `title` equals it.
- **B8:** version stays 0.1.0-rc1 with no `date-released`; recorded in `release_checklist.md`.
- **B9:** home paths scrubbed from editable files; what remains and why: `reproducibility_report.md`, section 7.
- **B10:** committed PDFs stay and are attached to a release.
- **B11, B13:** release-note lines added to `release_checklist.md` (Figure 2; external build tools).
- **B14:** the source labels are accepted (all cited sources passage-checked, none read in full, as the manuscript states); no text change.
- **R-RIGGED-1:** the reading of EXP-004 as a contradiction of the base-rate prediction is accepted as written; no text change.

Still open (the owner's): B15 article drafts and their titles; B16 full-text review of the manuscript and sign-off of this checklist; B18 release, tag and any DOI or preprint; the boxes above, including the confirmation of the recorded protocol freezes.
