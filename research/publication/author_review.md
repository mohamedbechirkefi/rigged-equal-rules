<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# Owner review

Status: updated at M6 (2026-11-25). Items the owner must decide or approve. Only the owner ticks a box; at M6 no box was ticked and none had been ticked by an agent since M5. At M5, four boxes that an AI session had ticked to record owner decisions were unticked (DEC-024); the decisions themselves stand and are recorded in the decision log, cited next to each item.

- [ ] Freeze the project protocol and the EXP-001 to EXP-004 protocols (G-FREEZE). Recorded as decided by the owner on 2026-11-24, with the pre-data amendments of 2026-11-24 and 2026-11-25 (DEC-012, DEC-016 to DEC-018).
- [ ] Confirm the primary metric (equal-opportunity gap), the baseline (P0) and the 2 pp smallest effect of interest. Recorded as frozen with the protocols.
- [ ] Data decision: synthetic data for EXP-001 to EXP-003; UCI Adult for EXP-004. Recorded as decided by the owner (round 2, DEC-011; DEC-003 superseded for EXP-004).
- [ ] DEC-019: a disclosed limitation on H4, with no rerun. Recorded as decided by the owner (2026-11-25, DEC-021).
- [ ] Review the manuscript text (`research/paper/manuscript.md`, M5 version) and supplementary file, including the reading of EXP-004 as a contradiction of the base-rate prediction (`research/publication/review_pass_2.md`, R3).
- [ ] Approve author and affiliation metadata (currently: Mohamed Bechir Kefi, no affiliation).
- [ ] Approve the AI-assistance disclosure text (manuscript section 11). Recorded as approved by the owner with the funding and competing-interest statements on 2026-11-25 (DEC-023).
- [ ] Decide whether full-text reading of the cited sources is required before release (at M6 the full text of each paper was opened and the cited passage checked; none was read in full).
- [ ] Review the demo (`demo/`, M5) and the article drafts (`articles/medium.md`, `articles/linkedin.md`).
- [ ] Supply the repository URL and the demo URL at a release decision (placeholders now).
- [ ] Approve any publication, push or release (G-PUBLIC).

## Prepared for the owner (M6, 2026-11-25)

Release candidate 0.1.0-rc1 is prepared locally. Nothing is pushed, tagged or released. Under owner, 2026-11-25, "Next" (second) (`labs/_shared/owner-approvals-2026-11-25e.md`), this section lists what to read for each box and every open decision; it decides none of them.

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

- Whether to publish, push, tag or release anything, and under which licence terms, is the owner's decision (G-PUBLIC); M6 released nothing.
- Whether the five protocols are recorded as frozen by the owner is for the owner to confirm by ticking the first box (the decision is recorded in DEC-012 and DEC-016 to DEC-018).
- The manuscript title is a working title, because the titles approved on 2026-11-25 (post-M4) named other projects; the owner may approve it or give another.
- The author line, the affiliation and the repository and demo URLs are facts only the owner can supply.
- The owner has not yet reviewed the manuscript text, including the reading of EXP-004 as a contradiction of the base-rate prediction.
- The owner may decide whether the passage-level check of the cited sources is enough, or whether full reading is required before release.
- The owner may accept Figure 2 (EXP-002) as it is, with its crowded axis labels, or ask for a regenerated figure, which would be a change to a checksummed result file and needs a decision of its own.
- `CITATION.cff` has no `date-released` (coordinator default under the record above); the owner re-adds it at publication, together with the version of the actual release.
- The CLA and licence files are unchanged and remain the owner's decision.

### Owner placeholders remaining (file and line, at the M6 commit)

| File | Line | Placeholder |
|---|---|---|
| `research/paper/manuscript.md` | 4 | author line: "(no affiliation; author metadata pending the owner's approval)" |
| `research/paper/manuscript.md` | 260 | repository URL: `<repository URL, not yet published>` |
| `research/paper/manuscript.md` | 275 | demo URL: `<demo URL, not yet published>` |
| `research/paper/manuscript.md` | 279 | "the owner's full-text review of this manuscript is pending (M6 owner checklist)" |
| `CITATION.cff` | 8 | message: working title, author metadata pending, repository URL not yet published |
| `CITATION.cff` | 11 | comment: author metadata pending; repository URL to be added at release |
| `README.md` | 2 | title marked "(working title)" |
| `README.md` | 46 | demo URL placeholder |
| `README.md` | 87 | author metadata pending; repository URL placeholder |
| `articles/medium.md` | 4 | author metadata pending |
| `articles/medium.md` | 34 | repository and demo URL placeholders |
| `articles/linkedin.md` | 12 | repository and demo URL placeholders |
| `demo/README.md` | 19 | demo URL placeholder |
| `demo/src/App.tsx` | 60 to 61 | page footer: author metadata pending; repository URL placeholder |

`research/paper/manuscript.tex` and the PDFs carry the same placeholders, since they are generated from `manuscript.md`.

