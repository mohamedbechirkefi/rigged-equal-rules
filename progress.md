<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# Progress journal

Append-only, dated. Commands and their actual outputs.

## 2026-11-24: M0 session (bootstrap, feasibility, M1 drafts)

**Milestone:** M0, plus M1 drafts. **Starting state:** branch `main`, one commit (`6cb6674`, master prompt and the owner's licence package), working tree clean.

### Decisions

DEC-001 (licence is the owner's custom NC research licence), DEC-002 (zero-cost toolchain without TeX), DEC-003 (synthetic data only), DEC-004 (draft primary metric EOG, baseline P0), DEC-005 (dependency pinning with an upload cut-off). See `research/decision_log.md`.

### Commands and actual outputs

Hardware and tools (full table in `research/feasibility.md`):

```
$ sysctl -n machdep.cpu.brand_string hw.ncpu hw.memsize
Apple M1 Pro
10
17179869184
$ sw_vers
ProductName: macOS  ProductVersion: 15.3.1  BuildVersion: 24D70
$ df -h /Users/bechir
/dev/disk3s1  460Gi  311Gi  129Gi  71%  ...  /System/Volumes/Data
$ /usr/local/bin/python3 --version
Python 3.12.1
$ .tools/py/bin/uv --version
uv 0.9.5 (d5f39331a 2025-10-21)
$ .tools/py/bin/typst --version
no such file or directory   (typst is a Python package, not an executable)
$ .tools/py/bin/python -c "import typst, pypdf, PIL; ..."
typst 0.15.0 / pypdf 6.20.0 / pillow 11.3.0
$ .tools/pandoc --version
pandoc 3.6.3
$ helix/.tools/node/bin/node --version
v22.23.3
$ git --version
git version 2.42.1
$ which tex pdflatex xelatex
tex not found / pdflatex not found / xelatex not found
```

Dependency lock:

```
$ .tools/py/bin/uv lock
Using CPython 3.12.1 interpreter at: /Library/Frameworks/Python.framework/Versions/3.12/bin/python3
Resolved 16 packages in 8ms
$ .tools/py/bin/uv sync --frozen
(installed) ... pytest==9.2.0, referencing==0.37.0, rpds-py==2026.9.1, sortedcontainers==2.4.0, typing-extensions==4.16.0, ...
$ .venv/bin/python -c "import numpy, jsonschema, pytest, hypothesis; ..."
2.5.4 4.26.0 9.2.0 6.170.15
```

PyPI release dates checked before pinning (JSON API, upload time of first file): numpy 2.5.4 on 2026-10-10 (2.5.5 of 2026-11-15 excluded as too recent); pytest 9.2.0 on 2026-10-27; hypothesis 6.170.15 on 2026-11-06; jsonschema 4.26.0 on 2026-01-07.

Toolchain smoke check (EXPLORATORY, journal entry JRN-0001; no scientific content):

```
$ pandoc research/paper/manuscript.md -s -t latex -o research/paper/manuscript.tex
exit 0 (118 lines)
$ pandoc research/paper/manuscript.md -s -t typst -o <scratch>/manuscript.typ
exit 0
$ python -c "import typst; typst.compile(...)"
typst.TypstError: font fallback list must not be empty        (FAILURE: pandoc's typst template passes an empty font list)
$ pandoc ... -t typst -V mainfont="Libertinus Serif" -o <scratch>/manuscript.typ ; python -c "import typst; typst.compile(...)"
compiled
$ pypdf: pages 2; first-page text begins "When equal rules produce unequal outcomes (working title)"
sha256 of the scratch PDF: 1a0368b23600df229586f1ecf7187e65b77d6f15f762715e00608c020eb4d276
```

Rendered page 1 as PNG and inspected it: title and status paragraph render; the headings-only skeleton puts the remaining headings on page 2 (to be revisited with a project Typst template in M6). The PDF is not committed (skeleton only). A SPDX comment and a "generated, do not edit" note were prepended to `manuscript.tex` because pandoc drops the Markdown HTML comment.

Literature and dataset pages opened with WebFetch (2026-11-24): arXiv 1609.05807, 1703.00056, 1610.02413, 1701.08230, 1709.02012, 1803.04383; fairmlbook.org; UCI Adult dataset page; folktables README; US Census API terms of service; propublica/compas-analysis repository page. Only landing pages and abstracts were read; see `research/literature_review.md`.

### Files created or changed

Created: `CLAUDE.md`, `roadmap.md`, `progress.md`, `README.md`, `CITATION.cff`, `pyproject.toml`, `uv.lock`, `research/{decision_log,literature_review,protocol,limitations,feasibility}.md`, `research/claims_register.csv` (header only), `research/experiment_registry.csv`, `research/experiment_journal.jsonl`, `research/experiments/EXP-00{1,2,3}/protocol.md`, `research/paper/{manuscript.md,manuscript.tex,references.bib,supplementary.md,figures/README.md}`, `research/publication/{artifact_manifest.json,claims_audit.md,reproducibility_report.md,author_review.md,release_checklist.md}`, `data/manifest.json`, READMEs in `results/`, `src/`, `tests/`, `experiments/`, `demo/`, `articles/`.
Changed: `CONTRIBUTING.md` (appended section 6, development commands). Licence files untouched.

### Failures and notes

- `typst` is not an executable in `.tools/py/bin`; it is used as a Python package.
- First Typst compile failed (empty font list); fixed with `-V mainfont`.
- `build/` (used by the PDF commands in CONTRIBUTING.md) is not in `.gitignore`; `.gitignore` belongs to the owner's licence package and was not changed. Owner may add it.
- No tests exist yet; none were run.
- The scratch directory used for the smoke PDF is shared with other sessions; the first outputs were written at its top level and then moved into a `rigged/` subfolder. If another session had files with the same names there (`manuscript.typ`, `manuscript.pdf`, `page1.png`, `page2.png`), they may have been overwritten. Nothing inside any repository was affected.

### Outstanding risks

- The primary hypothesis is analytically implied by the Gaussian model; the value of the study rests on quantification, the sensitivity analysis and the explanation (stated in the protocol).
- `manuscript.tex` cannot be compiled locally.

### Next action

Owner: review and freeze (or amend) `research/protocol.md` and the three EXP protocols; confirm DEC-003 and DEC-004. Meanwhile (allowed without the freeze): M1 full-text reading and analytic TPR derivation, then M2 implementation starting with the generator, P0 and the metric tests, then the exploratory smoke run.

## 2026-11-24: M2 session (core implementation while the freeze is pending)

**Milestone:** M2. **Starting state:** branch `main` at `9770a5f`, tree clean. The protocol is DRAFT v0.1, not frozen; every run in this session is exploratory.

### What was built

Package `src/rigged/` (pure, typed, seeded; ingestion is not needed because data are synthetic): `config` (validated cells and runs, canonical config hash), `numerics` (normal CDF and quantiles, Gaussian, Student t3 and shifted log-normal latent families, Student t quantile; no SciPy, DEC-006), `generator` (SYN-001/1.0.0, common random numbers, separate fitting and evaluation streams), `policies` (P0 baseline first, then P1, P2, P3; seeded tie-breaking; explicit `PolicyFitError`), `metrics` (group confusion matrices, SR, TPR, FNR, FPR, PPV, ECE, utility, accuracy, gaps; null with a reason on zero denominators), `analytic` (P0 population values by numerical integration; Gaussian posterior for P1), `stats` (percentile bootstrap over seeds, t-interval), `matrices` (draft EXP-001 to EXP-003 matrices; exploratory SMOKE, SIZING, DEGEN), `runner`, `schema` with `schemas/` (result bundle 1.0.0, run manifest 1.0.0, validated at export and import), `protocol_guard` (DEC-008), `report` (CSV, Markdown, SVG, PDF through pandoc and Typst), `cli` (`smoke`, `run`, `report`, `test`). Wrapper `scripts/rigged`. Tests in `tests/` (eight files). `pyproject.toml`: pytest `pythonpath = ["src"]` only; no dependency added; `uv lock --check --offline` reports "Resolved 16 packages".

### Commands and actual outputs

```
$ .venv/bin/python -m pytest -q          (first full run)
1 failed, 97 passed      (test_summarise_degenerate compared a float mean of 0.2 values to exactly 0.0; test changed to exactly representable 0.25)
$ .venv/bin/python -m pytest -q
98 passed in 7.33s
$ UV=.../uv scripts/rigged test
98 passed in 7.19s
-> commit 95c5f9a
$ scripts/rigged smoke --matrix SMOKE|SIZING|DEGEN --pdf     (first execution, at 95c5f9a)
SMOKE ok 24, failed 0, wall clock 0.07 s
SIZING ok 400, failed 0, wall clock 2.94 s; projected full-matrix runtime: 10.1 s
DEGEN ok 93, failed 27, wall clock 0.12 s
```

Visual inspection of the SIZING PDF (pages rendered to PNG): a 12-column table overflowed at a page break and overlapped the footer, axis labels were clipped and the figure caption was duplicated. Fixed in the report generator (two narrower tables, breakable Typst figures, `fontsize=10pt`, rotated labels); re-rendered pages checked. Commit `16e3b4f`. The first outputs were deleted and every exploratory matrix was rerun from the clean revision:

```
$ scripts/rigged smoke --matrix SMOKE --pdf    ok 24, failed 0, wall clock 0.31 s
$ scripts/rigged smoke --matrix SIZING --pdf   ok 400, failed 0, wall clock 9.88 s; projected full-matrix runtime: 34.5 s
$ scripts/rigged smoke --matrix DEGEN --pdf    ok 93, failed 27, wall clock 0.43 s
$ uptime
load averages: 81.19 45.91 21.92        (other processes on the machine; explains the slower second execution)
```

The two SIZING executions gave identical results apart from runtime and memory fields (400 of 400 run records compared). Commit `a74cc18` then added the analytic Gaussian posterior and a P1 calibration check (no change to run outputs): `101 passed in 8.71s`.

### Exploratory measurements (JRN-0002 to JRN-0004; not findings)

- Runtime per run at n = 20,000: mean 6 to 11 ms by policy (first execution) and 21 to 38 ms (recorded execution under load). Projected full draft matrix, 1,380 unique runs: 10.1 s to 34.5 s, against a planning budget of 30 minutes. Peak RSS 75 to 84 MiB.
- Seed spread at n = 20,000 (20 seeds): P0 EOG per-seed SD 1.05 pp (control) and 1.25 pp (primary cell); SD of the primary paired difference 0.61 pp; bootstrap half-width 0.26 pp against a 2 pp smallest effect of interest. 20 seeds are adequate. Largest per-seed SD seen: 4.60 pp (P1, d1.00-r2.00).
- Smoke matrix at n = 2,000: P0 EOG SD 3.78 pp and 4.77 pp over 3 seeds, above the protocol's 3 pp trigger, which was meant for n = 20,000 (AP-002).
- Analytic check of P0: 28 of 28 metric-cell comparisons within 3 bootstrap SE (largest |z| 2.21).
- Degenerate cases: none in the planned matrices (no failure, no undefined value at n = 20,000). The DEGEN probe produced 27 explicit `PolicyFitError` failures and null metrics with reasons, as designed.

### Proposed amendments (owner's decision; not applied)

`research/protocol_amendment_proposals.md`: AP-001 compute budget; AP-002 seed-count trigger and optional 50 seeds; AP-003 H1b direction (analytic EOG at delta = 0 is 0, 0.177, 0.081 pp for rho = 1, 1.5, 2: not monotone); AP-004 exploratory seeds of 1000 and above; AP-005 P3 capacity tolerance (up to 5 individuals measured); AP-006 disclosure of pre-freeze knowledge (EXP-003 H2 is analytically determined; B-sB2 seen in the exploratory run); AP-007 ECE gap is policy-independent; AP-008 P1 bin resolution.

### Decisions

DEC-006 to DEC-010 in `research/decision_log.md`.

### Files created or changed

Created: `src/rigged/` (15 modules and 2 schemas), `tests/` (conftest and 8 test files), `scripts/rigged`, `results/exploratory/{smoke,sizing,degen}/`, `research/protocol_amendment_proposals.md`. Changed: `pyproject.toml`, `CONTRIBUTING.md` (section 7 appended), `README.md`, `src/README.md`, `tests/README.md`, `results/README.md`, `data/manifest.json`, `roadmap.md`, `research/experiment_registry.csv` (statuses), `research/experiment_journal.jsonl` (JRN-0002 to JRN-0004), `research/decision_log.md`. Protocols, master prompt and licence files untouched.

### Not done, and why

- No confirmatory run, no protocol hash, no experiment report: the protocol is not frozen (G-FREEZE).
- The analytic TPR expressions are implemented numerically but not written into the draft protocol text, which is the owner's to change.
- No separate golden-fixture manifest file (golden values are inline in the tests).
- Nothing pushed (G-PUBLIC). No demo UI (M5).

### Outstanding risks

- The primary hypothesis and EXP-003 grids A and B are analytically determined under the Gaussian model (AP-006).
- The reproduction commands in the EXP protocols need `PYTHONPATH=src` or `scripts/rigged` (DEC-010).

### Next action

Owner: review AP-001 to AP-008, amend and freeze the protocols, record the hashes in the registry. Then M3: `scripts/rigged run --experiment EXP-001` (and EXP-002, EXP-003) and the per-experiment reports.
