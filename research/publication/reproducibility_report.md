<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# Reproducibility report

Status: M6 release candidate 0.1.0-rc1, 2026-11-25. Every command below was run in this session; the outputs are the actual ones. Machine: the owner's laptop (Apple M1 Pro, macOS), Python 3.12.1, Node v22.23.3, pandoc 3.6.3, typst (Python package) 0.15.0. At most two workers were used; every computation here ran in one process.

- [x] Clean clone into a separate directory.
- [x] `uv sync --frozen` from `uv.lock`.
- [x] Test suite run; actual counts recorded.
- [x] Smoke reproduction; results compared with the committed smoke results within the documented tolerance.
- [x] Demo build.
- [x] Data manifest and links verified.
- [x] Secret and personal-identifier scan.
- [x] Licence headers and third-party licences checked.

## 1. Clean clone of the M5 state (commit 98e57b1)

`$S` is the session scratch folder (`/private/tmp/claude-501/.../scratchpad/rigged-equal-rules/m6`), outside the repository; the clone was deleted at the end of the session.

```
$ git clone -q <this repository> $S/clone       # local clone of HEAD 98e57b1, no network
$ ../.tools/py/bin/uv sync --frozen --all-groups --all-extras                 # environment of 14 distributions from uv.lock
$ .venv/bin/python -m pytest -q
121 passed in 26.01s
```

### Smoke reproduction (exploratory matrices, compared with the committed outputs)

The repository documents `scripts/rigged smoke` (CONTRIBUTING.md) as the smoke reproduction. Three committed smoke outputs exist:

| Output | Code revision recorded | Command rerun in the clone | Result |
|---|---|---|---|
| `results/exploratory/smoke/` (M2) | 16e3b4f | `UV=../.tools/py/bin/uv scripts/rigged smoke` | **Not reproduced, as expected.** All four tables differ. `src/` changed between 16e3b4f and b455d59 (9 files, the pre-data amendments A1 to A6), so the M2 outputs describe superseded code. They are kept as the historical record (JRN-0002) and labelled so in `results/README.md`. |
| `results/exploratory/m3-smoke/` (M3) | 9f464c5 | `scripts/rigged smoke --matrix SMOKE --out results/exploratory/m3-smoke` | **Reproduced.** `contrasts.csv`, `policy_vs_p0.csv`, `analytic_check.csv` and the SVG figure are byte-identical. `summary.csv` differs only in `runtime_mean_s`; every other value in all 8 rows is identical (maximum absolute difference 0). |
| `results/exploratory/m3-sizing/` (M3, n = 20,000) | 9f464c5 | `scripts/rigged smoke --matrix SIZING --out results/exploratory/m3-sizing` | **Reproduced.** Same pattern: three tables and the figure byte-identical; `summary.csv` identical in all 20 rows except `runtime_mean_s`. |

`git diff 9f464c5 HEAD -- src` and `git diff b455d59 HEAD -- src` are both empty, so the M3 smoke outputs exercise the exact confirmatory code. The documented tolerance (EXP-001 `reproduction.md`) is exact equality of every metric, with runtime, memory and timestamp fields free to differ; it holds.

No confirmatory experiment was rerun. Instead, the four report generators were rerun on the committed confirmatory results:

```
$ for e in EXP-001 EXP-002 EXP-003 EXP-004; do PYTHONPATH=src .venv/bin/python -m rigged.cli report --experiment $e; done
exit 0 (four times); git status: clean (every table, figure and generated report byte-identical)
$ (cd results/EXP-NNN && shasum -a 256 -c SHA256SUMS)
EXP-001: 10 OK, 0 not OK; EXP-002: 10 OK; EXP-003: 10 OK; EXP-004: 11 OK
```

### Demo

```
$ export PATH=<read-only Node 22 toolchain>/bin:$PATH   # Node v22.23.3
$ cd demo && npm ci --prefer-offline
added 53 packages in 619ms
$ npm test
Test Files  2 passed (2); Tests  18 passed (18)
$ npm run build
dist/index.html 0.91 kB; dist/assets/sandbox.worker-CF6u4gxe.js 6.87 kB; dist/assets/index-DMVOV6WT.css 6.38 kB;
dist/assets/index-B05VWmE4.js 251.67 kB; built in 265ms
$ node tools/a11y_check.mjs dist
PASS results render (no fail-closed panel): 7 experiment panels
PASS text contrast, light scheme (WCAG AA)
PASS text contrast, dark scheme (WCAG AA)
PASS keyboard reaches every focusable element: 40 reached of 40
PASS visible focus indicator
PASS no horizontal page scroll at 360 px: overflow 0px
PASS reduced motion: no running animations: 0 running
PASS no request leaves the local origin
PASS offline after first load: results stay, sandbox runs: Sandbox output ready: 5 seed(s) from seed 1, n 5000. P0 EOG 6.49 pp.
A11Y-CHECK PASS
```

### Export determinism

```
$ python3 scripts/export_demo_data.py
wrote demo/public/data/results.json (108217 bytes)
$ python3 scripts/export_demo_data.py --check
results.json matches the export
$ git status --short | wc -l
0
```

## 2. Findings and fixes (working repository)

| Finding | Where | Fix |
|---|---|---|
| The committed `CITATION.cff` did not parse as YAML (`ParserError while parsing a block mapping`): an M5 text replacement had also hit the `authors:` key of the dataset reference, moving it to column 0. | `CITATION.cff` | Rewritten with the reference's `authors` restored; validated structurally against CFF 1.2.0 (section 4). |
| The M2 smoke outputs are not reproducible at the current code. | `results/exploratory/smoke/` | Not a defect: expected after the pre-data amendments. Disclosed in `results/README.md`, which also described the confirmatory folders as "None exists" (stale since M3) and is corrected. |
| The experiment-report PDFs did not embed their strip plots, and three reports had lists rendered inline (no blank line before the list). | `research/experiments/EXP-NNN/report.md` | Figure embedded with a caption in each report; 14 blank lines inserted before lists. No text or number changed. |
| Figures 3 and 4 of the manuscript were captioned "P0 EOG", but the plots also show P3 (EXP-003, grids A and B) and P1 to P3 (EXP-004). | manuscript, EXP-003 report, artifact manifest | Captions and the two manifest definitions corrected. |
| One quoted path did not resolve (tables/base_rate_gap.csv, without its folder, in the EXP-004 report). | EXP-004 report | Full path `results/EXP-004/tables/base_rate_gap.csv`. |

The fixes were re-checked in a second fresh clone of the release-candidate commit (section 6).

## 3. PDFs

Built with `../.tools/py/bin/python scripts/build_pdfs.py --typ-dir $S/typ --png-dir $S/png` (pandoc to Typst, typst 0.15.0; same options as `rigged.report.build_pdf`, plus the title metadata, unnumbered figures and unjustified 8.5 pt table text).

| PDF | Pages | Size | Title metadata |
|---|---|---|---|
| `research/paper/manuscript.pdf` | 14 | 0.33 MB | manuscript title |
| `research/paper/supplementary.pdf` | 8 | 0.23 MB | "Supplementary material" |
| `research/experiments/EXP-001/report.pdf` | 4 | 0.10 MB | report title |
| `research/experiments/EXP-002/report.pdf` | 4 | 0.15 MB | report title |
| `research/experiments/EXP-003/report.pdf` | 5 | 0.12 MB | report title |
| `research/experiments/EXP-004/report.pdf` | 5 | 0.11 MB | report title |

Every page of the manuscript, every page of the supplementary file, and the first page and figure page of each report were rendered at 60 ppi and inspected (Figure 2 also at 150 ppi). Fixes made in the builder: the title had been rendered as a plain paragraph (now a title block and PDF metadata); figure captions read "Figure 1: Figure 1 (FIG-001)" (Typst numbering switched off); pipe tables wrapped intervals inside narrow fixed columns (`--columns=400`, smaller unjustified table text); a code-block comment wrapped into a misleading line (moved to its own line in the manuscript). Remaining, disclosed: the 48 rotated axis labels of Figure 2 (EXP-002) overlap in places; every plotted value is in Supplementary Table S2, and the figure is a checksummed result file, so it was not regenerated (`research/limitations.md`, M6). pypdf: every PDF has a title, no e-mail address and no home-directory path in its bytes. Equations (section 3 of the manuscript) render as Typst math; no raw Markdown, missing glyph or clipped figure was found.

`research/paper/manuscript.tex` was regenerated with `pandoc research/paper/manuscript.md -s -t latex` (not compiled: no TeX distribution, DEC-002).

## 4. Links, references, numbers, manifests

- `python3 scripts/check_links.py` (tested by `tests/test_links.py`): 55 tracked Markdown files, 23 Markdown links, the back-quoted repository paths of the reader-facing documents, and 8 bib entries: PASS (one path fixed, section 2).
- References: 8 entries in `references.bib`, all cited in the manuscript text and listed in its reference list; report citation keys all resolve. Read in full: 0. Full text opened and cited passage checked: 7 (six papers and the book's chapter 3). Dataset page: 1. Unverified: 1 (ding2021, not cited). Details: `research/literature_review.md`, section 5; evidence audit, section 9.
- Numbers: `tests/test_demo_export.py` already checks that README, CITATION.cff, both articles and the demo README print no decimal number absent from the manuscript or supplementary file, and that every demo display string is verbatim in them: pass.
- `data/manifest.json`: archive SHA-256 and all 5 member hashes match `data/raw/adult.zip`; every named path exists.
- `research/publication/artifact_manifest.json`: 21 entries, 42 paths all present, 21 of 21 result hashes and 45 of 45 config and protocol hashes match.

## 5. Scans

- Tracked files: 247 at the start of M6. E-mail addresses: 1 (`noreply@anthropic.com` in `CLAUDE.md`, the public co-author trailer the commit rule requires; not personal, kept). Tokens or keys: 0. Private key headers: 0. Password or secret assignments: 0. `.env` files: 0.
- Absolute home-directory paths: 51 hits in 10 files. Kept, with reasons: `CLAUDE.md` (6, toolchain locations the session rules name), `src/rigged/report.py` (2, overridable default tool paths; `src/` is kept identical to the confirmatory revision b455d59), `results/EXP-NNN/run.log` (28, checksummed result files), `research/feasibility.md` (5, the dated M0 environment record), and the append-only records `progress.md` (4), `research/decision_log.md` (3) and `research/experiment_journal.jsonl` (3), for which a note is appended instead. The new M6 script `scripts/build_pdfs.py` locates the toolchain relative to the repository and carries no home path.
- Dependency licences: `research/publication/dependency_licences.md` (14 Python distributions, 84 npm lockfile packages). No dependency is flagged; MPL-2.0 applies only to test or build tools that are not redistributed.
- SPDX headers: every file added since M0 carries the header where its format allows; `demo/.npmrc` lacked it and now has it (`npm config list` still reads its settings).

## 6. Re-check in a fresh clone of the release candidate

See `progress.md`, M6 entry, section "Fresh clone of the release candidate", for the commands and outputs after the fixes.
