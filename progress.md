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

## 2026-11-24: data and freeze session (UCI Adult, amendments, G-FREEZE owner-approved)

**Brief:** `labs/_shared/DATA-FREEZE-brief.md`; authority `labs/_shared/owner-approvals-2026-11-24b.md` sections 1 and 7 (RIGGED). **Starting state:** `main` at `deabab3`, tree clean.

### Decisions

DEC-011 (UCI Adult adopted for EXP-004), DEC-012 (amendments A1 to A6), DEC-013 (EXP-004 P3 tolerance 30, to ratify), DEC-014 (freeze mechanics), DEC-015 (fit_threshold subnormal fallback).

### Commands and actual outputs

```
WebFetch https://archive.ics.uci.edu/dataset/2/adult (2026-11-24)
  "This dataset is licensed under a Creative Commons Attribution 4.0 International (CC BY 4.0) license." DOI 10.24432/C5XW20; Download (605.7 KB)
$ python3 -I scripts/download_adult.py
downloaded https://archive.ics.uci.edu/static/public/2/adult.zip -> data/raw/adult.zip (620237 bytes)
sha256 7537312dd56c2b98035880805ce99e68183a30ee468aa5329d6df0fbb3cc21bb
  adult.data: 3974305 bytes; adult.test: 2003153 bytes; adult.names, old.adult.names, Index
```

The protocol amendment (section 13, round 2) and the EXP-004 protocol were written before the fit. Then:

```
$ PYTHONPATH=src .venv/bin/python scripts/fit_adult_score.py        (JRN-0005, exploratory)
adult.data: 32,561 read, 32,561 kept, 0 excluded; adult.test: 16,281 read, 16,281 kept, 0 excluded
missing (?): workclass 1,836 / 963, occupation 1,843 / 966, native-country 583 / 274 (unused columns)
intercept -1.46116; coefficients (standardised) age 0.54567, education-num 0.88671, log1p gain 0.51544, log1p loss 0.27457
converged in 7 iterations; training mean log loss 0.43510; 0.39 s
```

P3 feasibility on tied real scores (JRN-0006; training file only, random partitions, seeds 1000 to 1019, no metric computed): 4,257 distinct scores in 32,561 rows; fit_selected minus target ranged -19 to +9, 4 of 20 beyond 10. EXP-004 P3 tolerance set to 30 (DEC-013).

```
$ ../.tools/py/bin/uv sync --frozen --all-groups --all-extras
Audited 14 packages
$ .venv/bin/python -m pytest -q        (after the amendments; before the fallback fix)
1 failed, 110 passed, 1 skipped   (Hypothesis example: tie uniforms 0.0 and 5e-324 in fit_threshold; DEC-015)
$ .venv/bin/python -m pytest -q
111 passed, 1 skipped   -> commit 48f0652 (freeze content)
$ PYTHONPATH=src .venv/bin/python -m rigged.cli export-configs --check
EXP-001 to EXP-004: matches
(freeze record and registry hashes written)
$ .venv/bin/python -m pytest -q
112 passed
$ PYTHONPATH=src .venv/bin/python -m rigged.cli export-configs
REFUSED: EXP-001 is frozen; its config is not rewritten   (exit 2)
guard with the code-built configs: EXP-001 to EXP-004 frozen: protocol, config and freeze record match
```

No confirmatory run was executed. No EXP-004 metric on `adult.test` was computed. The test suite never runs EXP-004 on the real pool.

### Files created or changed

Created: `scripts/download_adult.py`, `scripts/fit_adult_score.py`, `src/rigged/adult.py`, `data/raw/adult.zip`, `data/raw/adult.provenance.json`, `data/ingestion_report.json`, `research/experiments/EXP-00{1,2,3,4}/config.json`, `research/experiments/EXP-004/{protocol.md,score_model.json}`, `research/freeze.json`, `tests/test_adult.py`, `tests/fixtures/adult_synthetic.test` (hand-written synthetic rows).
Changed: protocols (amendments, FROZEN headers), `src/rigged/{config,matrices,policies,protocol_guard,runner,report,cli}.py`, `tests/test_schema_runner_cli.py`, `data/manifest.json`, registry, journal (JRN-0005, JRN-0006), decision log, limitations, roadmap, CITATION.cff, manuscript.md and .tex.

### Risks and items for the owner

- Ratify the EXP-004 partition (hours-per-week below 40, random-permutation control) and the EXP-004 P3 tolerance of 30.
- AP-007 and AP-008 were not in the approved list and were not applied.
- Protocol reproduction commands still read `uv run python -m rigged.cli ...` (need `PYTHONPATH=src` or `scripts/rigged`); correct commands are in `research/freeze.json`.

### Next action

M3 when the coordinator schedules it: `scripts/rigged run --experiment EXP-001` to `EXP-004`, then reports.

## 2026-11-24: round 3 of the owner's decisions (EXP-004 grouping)

**Milestone:** M1 gate (amendment to a frozen protocol, before data). **Starting state:** `main` at `77f1efa`, tree clean.

### Decisions

DEC-016 (EXP-004 primary group attribute sex, hours-per-week below 40 secondary; pre-data amendment), DEC-017 (P3 tolerance of 30 ratified).

### What was done, in order

1. Wrote the round-3 amendment into `research/protocol.md` section 13 (R3-1 to R3-10), including the rule for Group B (lower base rate on `adult.data`), before applying it.
2. Applied the rule on the training file only (JRN-0007, exploratory). Actual output:

```
adult.data kept 32561; counts {'Male': 21790, 'Female': 10771}; positives {'Male': 6662, 'Female': 1179}
base rates Male 0.3057, Female 0.1095  -> Group B = Female
```

3. Recorded the result in the protocol, updated the EXP-004 protocol to v1.1 (cells R-sex, R-sex-random, R-hours, R-hours-random; 320 runs; claims boundary), code (`rigged.adult`: sex column, `group_b_sex`, `sex_base_rates`, `lower_base_rate_value`, `real_populations(..., permute)`; `rigged.config`, `rigged.matrices`, `rigged.cli`), the EXP-004 config (written from the code; it now pins `group_b`), data manifest, registry, limitations and tests.

```
$ .venv/bin/python -m pytest -q                       (before the freeze record update)
1 failed, 115 passed   (the guard refused the changed EXP-004 config and protocol, as intended)
-> commit 97de686 (amendment content)
(freeze record updated: new hashes, superseded hashes with reason, round-3 approval, ratification, C4 extension)
$ ../.tools/py/bin/uv sync --frozen --all-groups --all-extras
Audited 14 packages
$ .venv/bin/python -m pytest -q
117 passed
$ PYTHONPATH=src .venv/bin/python -m rigged.cli export-configs --check
EXP-001 to EXP-004: matches
guard with the code-built configs: EXP-001 to EXP-004 frozen: protocol, config and freeze record match
guard with Group B flipped to Male in code: refused ("the matrix built by the current code differs from the frozen config"; test_guard_refuses_a_changed_group_b)
$ PYTHONPATH=src .venv/bin/python -m rigged.cli export-configs
REFUSED: EXP-001 is frozen; its config is not rewritten   (exit 2)
```

Nothing was computed on `adult.test`: no metric, base rate or group count. No run was executed.

### New hashes (SHA-256)

- `research/protocol.md`: 408822479b83377602279c58860e4bfcc427dcf22d0612e423f1e3aa5277d79c
- `research/experiments/EXP-004/protocol.md`: 907f5d29a36c802e7d29f6949916d6792c85f4033c6e61570f3b70aed8f73454
- `research/experiments/EXP-004/config.json`: 04b34c6880c3d5825af56d55636e6036425e20f9d3f254e854f797f961937a30
- `data/manifest.json`: 4af198a00a8fba9ee4a17f10796d0e297da781d64d1637bfc8336163445efb1c
- EXP-001 to EXP-003 protocols and configs unchanged.

### Risks and items for the owner

- Conflict noted: the master prompt (section 2) says "No real hiring decisions or protected-group claims", and `CLAUDE.md` says groups are never protected groups. The owner's round-3 decision makes sex the EXP-004 primary attribute. It is applied with claims limited to this partition of this 1994 extract under this score (protocol R3-10); `CLAUDE.md` was not edited. The owner may wish to confirm the wording.
- AP-007 and AP-008 remain not applied (not in any approved list).

### Next action

M3 when the coordinator schedules it: `scripts/rigged run --experiment EXP-001` to `EXP-004`, then reports.

## 2026-11-25: pre-data amendment, EXP-004 grouping option A

**Authority:** `labs/_shared/owner-approvals-2026-11-25.md`, item 1 ("approve all recommendations, RIGGED A"), replacing item 1 of `owner-approvals-2026-11-24c.md`. **Starting state:** `main` at `50aac6b`, tree clean.

### What was done, in order

1. Wrote the amendment into `research/protocol.md` (section 12 rewritten; section 13, A25-1 to A25-9) and the EXP-004 protocol (v1.2, section 11) before any code change; committed alone (`4daea38`).
2. Code, config, tests and records (`618a352`): `rigged.adult` no longer reads sex as a used column (no `group_b_sex`, `sex_base_rates`, `lower_base_rate_value`; no schema error on sex values); EXP-004 cells R-hours and R-hours-random, 160 runs; config written from the code; data manifest, registry and limitations updated.

```
$ .venv/bin/python -m pytest -q                        (before the freeze record update)
2 failed, 114 passed    (the guard refused the changed EXP-004 files, as intended)
(freeze record updated: new hashes, round-3 hashes kept under superseded with the reason, approval quoted, C4 extended)
$ ../.tools/py/bin/uv sync --frozen --all-groups --all-extras
Audited 14 packages in 3ms
$ .venv/bin/python -m pytest -q
116 passed in 7.34s
$ PYTHONPATH=src .venv/bin/python -m rigged.cli export-configs --check
EXP-001 to EXP-004: matches
guard with the code-built configs: EXP-001 to EXP-004 frozen: protocol, config and freeze record match
guard on a scratch copy with a changed EXP-004 config: refused ("config file differs from the freeze record")
guard with Group B threshold changed to 35 in code: refused ("the matrix built by the current code differs from the frozen config")
```

Nothing was computed on `adult.test`.

### New hashes (SHA-256)

- `research/protocol.md`: d4690c159f45dfb91f0de44dd55a5ec4a7fb83a7e17bb79e378db01f1fae893b
- `research/experiments/EXP-004/protocol.md`: ff9b80ff4c2421b9057838e1775bcfb08da65ae9e26b30c6c4f3ecdc4bfe30ae
- `research/experiments/EXP-004/config.json`: 6fe218fd09d7ea15f1689e048cdb44b935d110307889b14121008df165aed0c1
- `data/manifest.json`: 37194645cd251abaab069a90a26908b3032bdd573097633fb9908bfe9540192d

The round-3 master-prompt conflict is resolved (DEC-018).

### Next action

M3 (`labs/_shared/M3-brief.md`).

## 2026-11-25: M3 confirmatory runs (EXP-001 to EXP-004)

**Brief:** `labs/_shared/M3-brief.md`; reports per the coordinator's `report-return-note.md` (text returned, written by the coordinator). **Starting state:** `main` at `9f464c5`, tree clean.

### Before the runs

```
$ ../.tools/py/bin/uv sync --frozen --all-groups --all-extras      Audited 14 packages
$ .venv/bin/python -m pytest -q                                    116 passed in 7.32s
$ shasum -a 256 data/raw/adult.zip                                 7537312dd56c...cc21bb (matches the manifest)
guard: EXP-001 to EXP-004 frozen: protocol, config and freeze record match; export-configs --check: 4 matches
$ rigged.cli smoke --matrix SMOKE --out results/exploratory/m3-smoke     ok 24, failed 0, wall clock 0.07 s   (JRN-0008)
$ rigged.cli smoke --matrix SIZING --out results/exploratory/m3-sizing   ok 400, failed 0, 2.82 s; analytic 28/28 within 3 SE,
  tables identical to the M2 SIZING run                                                                    (JRN-0009)
```

Provenance revision `b455d59` (commit of the preparation; tree clean, no editable install).

### Confirmatory runs (`scripts/run_confirmatory.sh EXP-NNN`, nice 10, one process)

```
EXP-001 ok 240, failed 0, wall clock 1.38 s, exit 0   (2026-11-25T00:15:05Z to 00:15:06Z)
EXP-002 ok 960, failed 0, wall clock 6.97 s, exit 0   (00:15:13Z to 00:15:21Z)
EXP-003 ok 420, failed 0, wall clock 2.56 s, exit 0   (00:15:34Z to 00:15:37Z)
EXP-004 ok 160, failed 0, wall clock 1.42 s, exit 0   (00:15:47Z to 00:15:49Z)
```

Headlines (95% percentile bootstrap over 20 seeds): EXP-001 D = 6.59 [6.20, 6.97] pp, H1 supported; EXP-002 H1 and H2 supported; EXP-003 H0 rejected (19.44 and -22.50 pp at equal base rates), B-sB2 -9.56 [-10.01, -9.12] pp (sign reversal, analytically determined), H3 and H4 sign kept; EXP-004 D = -7.45 [-8.75, -6.05] pp, H1-real disconfirmed (sign reversal). Journal JRN-0010 to JRN-0013; claims CLM-001 to CLM-015.

Deviation: EXP-003 implementation check 56/60 within 3 SE (DEC-019); exploratory rerun on seeds 1000 to 1019 passed 60/60 (JRN-0014). Other choices DEC-020.

```
$ PYTHONPATH=src .venv/bin/python scripts/exp004_base_rates.py    wrote results/EXP-004/tables/base_rate_gap.csv (8 rows)
$ .venv/bin/python -m pytest -q                                   116 passed in 6.79s
```

Results (under 20 MB in total) are committed with `SHA256SUMS` and `provenance.json` per experiment; `run_manifest.json`, `metrics.csv` and figures copied into `research/experiments/EXP-NNN/`. The M3 status line is left to the coordinator, who writes the experiment reports.

## 2026-11-25: M3 done (coordinator)

The owner approved the experiment reports (owner, 2026-11-25, "approve all recommendations, RIGGED A", item 4). Subagents may not write report files, so the reports were composed by the M3 session from committed results only and written by the coordinator: 4 report(s). The coordinator checked that every decimal number in them appears in a committed file. With the complete matrices (or documented failures) recorded above, the M3 gate holds. M3 is **done**. Next: M4 (interpretation), not started.

## 2026-11-25: M4 interpretation, evidence audit and manuscript

**Brief:** `labs/_shared/M4-brief.md`, including the RIGGED follow-up of `owner-approvals-2026-11-25b.md`, item 2: "The EXP-003 implementation-check failures (4 of 60) are a disclosed limitation on H4. Nothing is rerun." That follow-up is recorded as DEC-021. **Starting state:** `main` at `1cd5a51`, tree clean.

### Commands and actual outputs

```
$ .venv/bin/python -m pytest -q                                  116 passed in 7.60s   (before any change)
$ PYTHONPATH=src nice -n 10 .venv/bin/python scripts/m4_exploratory.py
wrote 4 tables to results/exploratory/m4-confounders            (8.6 s wall clock, one process; JRN-0015, JRN-0016)
in-session Monte Carlo cross-check of JRN-0015 (4,000,000 draws per cell, seed 1234, not saved):
  13.00, 22.26, 15.18 pp against 13.04, 22.25, 15.20 pp by integration
$ PYTHONPATH=src .venv/bin/python -m rigged.cli export-configs --check     EXP-001 to EXP-004: matches
$ PYTHONPATH=src .venv/bin/python scripts/m4_evidence_audit.py   (final run)
EXP-001 240 ok, identity issues 0, summary max dev 4.98e-11 (432), contrast max dev 3.83e-11 (24), sha mismatches []
EXP-002 960 ok, identity issues 0, summary max dev 4.98e-11 (1728), contrast max dev 4.63e-11 (96), sha mismatches []
EXP-003 420 ok, identity issues 0, summary max dev 5.00e-11 (756), contrast 0 rows, sha mismatches []
EXP-004 160 ok, identity issues 0, summary max dev 4.83e-11 (288), contrast max dev 4.93e-11 (96), sha mismatches []
number trace unmatched: manuscript 10 (8 DOI/arXiv ids, 7.67 a derived difference), EXP-001 report 1 (71.7 MiB, unit conversion), claims register 1 (DOI); all others 0
$ python3 scripts/build_supplementary.py                         wrote research/paper/supplementary.md
$ python3 scripts/build_artifact_manifest.py                     21 entries
$ pandoc research/paper/manuscript.md -s -t latex                manuscript.tex regenerated (pandoc 3.6.3)
$ .venv/bin/python -m pytest -q                                  116 passed in 7.42s   (after all changes; src/ and tests/ unchanged)
```

### What was done

1. **Confounders and sensitivity:** `research/publication/interpretation.md`. Each protocol-named competing explanation is marked addressed or not. Two cheap exploratory checks were added:
   - JRN-0015: P1 with the exact Gaussian posterior. At the primary cell the EOG is 13.04 pp, against the binned 14.89 [14.30, 15.45] pp, and the PPV gap is 2.10 pp against 1.00 pp. The exact value is outside the binned interval in 5 of 12 cells.
   - JRN-0016: the EXP-004 score on the full pool by the hours partition. 70.31% of qualified Group B members and 62.05% of qualified Group A members score above the pool's 70th percentile. Calibration in the large is +11.23 pp for Group B and -2.98 pp for Group A.
   No frozen verdict changed.
2. **Expected versus observed:** table in `interpretation.md` section 4 and manuscript Table 6.
3. **Claims register:** columns added, 30 rows (CLM-016 to CLM-030 new; CLM-020 to CLM-025 are external, abstract-only). CLM-012 narrowed.
4. **Evidence audit:** `research/publication/evidence_audit.md`, `evidence_audit_output.json`, `number_trace.csv`, `artifact_manifest.json`. Mismatches fixed: EXP-001 report C4 value 6.31 corrected to 6.30 pp; stale DEC-019 text in the EXP-003 report; stale registry statuses; `references.bib` header and missing becker1996. Finding disclosed: `research/freeze.json` was appended after the runs, so its run-time hash differs; no frozen hash changed.
5. **Manuscript:** `research/paper/manuscript.md` synthesised to 11.4 (abstract 246 words; about 5,300 words outside tables), plus `supplementary.md` generated from committed tables. Status line: independent research manuscript / preprint draft, not peer-reviewed.
6. **Second review pass:** `research/publication/review_pass_2.md`. Of 12 challenges, 11 hold in full or in part (R8 does not); 7 manuscript changes are recorded. They include P3's utility gain on the real score, reported as running against EXP-002 H2's direction; the EXP-004 reading narrowed to the base-rate prediction; and the mechanism presented as near-definitional.
7. **Records:** limitations, DEC-021 and DEC-022, journal JRN-0015 and JRN-0016, registry, roadmap, CONTRIBUTING (M4 commands), author review and release checklist. M4 addenda were appended to the EXP-002 and EXP-004 reports, with their verdicts unchanged.

Nothing frozen was touched (protocols, configs, seeds, `freeze.json`). No confirmatory rerun. No sex or other protected attribute was read in any new computation.

### M4 gate

Every numerical claim maps to a claim row with a result ID, a config hash and a table or figure (`claims_register.csv`, `artifact_manifest.json`). Every external claim maps to a source that was opened, marked abstract-only. **M4 is done.** The owner's review of the manuscript text is open (M6 checklist).

### Risks and items for the owner

- Every cited source is used at abstract level only. The owner may want full-text reading before any release.
- The EXP-004 interpretation (a contradiction of the base-rate prediction, with the predicted sign under P1) is the main scientific judgement for the owner to review.

### Next action

M5 (interactive experience), using the M4 labels.


## 2026-11-25: post-M4 owner decisions (statements)

**Starting state:** `69f4227`, working tree clean. Authority: owner, 2026-11-25, "Approve all" (post-M4) (`/Users/bechir/research/labs/_shared/owner-approvals-2026-11-25c.md`, item 2; coordinator brief `/Users/bechir/research/labs/_shared/POST-M4-brief.md`, item 2 only).

- Item 2: the funding, competing-interest and AI-use wording in manuscript section 11 is recorded as owner-approved (DEC-023). No wording changed.
- No frozen protocol, config, seed or result changed. No computation. No manuscript rebuild (the manuscript text did not change).

### Owner placeholders for M5

1. Manuscript author line: "Mohamed Bechir Kefi (no affiliation; author metadata pending the owner's approval)". Only the owner can confirm the author metadata.
2. Manuscript section 10: "The public URL is a placeholder until the owner approves a release: `<repository URL, not yet published>`". Only the owner can supply it, at a release decision (G-PUBLIC).
3. Manuscript section 11: "The owner has not yet reviewed this manuscript's text (pending, M6 owner checklist)." Only the owner can state that this review was done.

### Tests

`.venv/bin/python -m pytest -q`: 116 passed in 7.27s (after the changes; src/ and tests/ unchanged).

### Next action

M5, with the placeholders above put to the owner.


## 2026-11-25: M5 interactive experience

**Authority:** owner, 2026-11-25, "Next" (`/Users/bechir/research/labs/_shared/owner-approvals-2026-11-25d.md`); stack: the master prompt's default (TypeScript, React, Vite) from the shared template. Brief: `labs/_shared/M5-brief.md`. **Starting state:** `a42e132`, tree clean. Decisions: DEC-024.

### Commands and actual outputs

```
$ .venv/bin/python -m pytest -q                                   116 passed in 6.82s   (before any change)
$ rsync -a --exclude node_modules ../_shared/demo-template/ demo/ ; cd demo && npm ci --prefer-offline
added 53 packages
$ python3 scripts/export_demo_data.py                             wrote demo/public/data/results.json (108217 bytes)
$ python3 scripts/export_demo_data.py --check                     results.json matches the export
$ PYTHONPATH=src .venv/bin/python scripts/make_demo_fixture.py    wrote demo/src/fixtures/engine_fixture.json (0.74 s wall clock, one process)
$ pandoc research/paper/manuscript.md -s -t latex                 manuscript.tex regenerated (pandoc 3.6.3)
$ .venv/bin/python -m pytest -q                                   121 passed in 7.08s   (after all changes; 5 new tests in tests/test_demo_export.py)
$ cd demo && npm ci --prefer-offline && npm test                  Test Files 2 passed (2); Tests 18 passed (18)
$ npm run build                                                   dist/index.html 0.91 kB; dist/assets/sandbox.worker-CF6u4gxe.js 6.87 kB;
                                                                  dist/assets/index-DMVOV6WT.css 6.38 kB; dist/assets/index-B05VWmE4.js 251.67 kB; built in 380ms
$ node tools/a11y_check.mjs dist --screenshots <scratchpad>/rigged/shots
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
$ node tools/a11y_check.mjs <copy of dist with one explorer interval bound set to null>
FAIL results render (no fail-closed panel): 0 experiment panels
A11Y-CHECK FAIL (2)                                               (expected: the page fails closed)
```

An earlier checker run failed "keyboard reaches every focusable element: 35 reached of 40": six results tables had identical text and position, so the checker's key collided. The tables were given distinct ids; the checker was not changed.

### What was done

1. **Export** (`scripts/export_demo_data.py`): seven entries (EXP-001 to EXP-004; JRN-0014 to JRN-0016 labelled exploratory), the EXP-002 explorer grid and the EXP-004 cells, 17 source files with SHA-256, code revision b455d59. **Consistency test** (`tests/test_demo_export.py`): byte identity with a fresh export; every display string verbatim in the manuscript, or in the supplementary file for explorer cells, or a documented group-rate exception; no protected-attribute word; README, CITATION.cff, articles and demo README print only manuscript numbers.
2. **Page** (`demo/`): overview with status and claims boundary, the fairness trade-off explorer and subgroup outcome charts (hand-written SVG, 95% intervals, 2 pp band), published results with equal visual weight for supported, contradicted and exploratory entries, assumptions labelled as such, method and limitations, sandbox. Loading, error (fail closed) and empty states.
3. **Sandbox**: faithful port of the engine logic (`demo/src/engine.ts`), equal to the Python engine on identical draws (counts exact, metrics within 1e-9); own random numbers, labelled. Seed, scenario presets, delta, rho, kappa, p_B, n, seeds, Run, Cancel, Reset; JSON download of the sandbox output only.
4. **Screenshots inspected** (desktop light, desktop dark, mobile, plus the EXP-004 view and the mobile sandbox): fixed small chart text on mobile (charts now measure their container), clipped table captions (moved out of the scroll regions), a too-wide gap table (utility moved to the subgroup table), wrapping intervals. `docs/demo.png` (159 KB) added to the README with alt text.
5. **Text consistency**: manuscript section 11 stale review sentence replaced with the true state; section 10 describes the demo; version M5. README rewritten (it described M2). CITATION.cff message updated. Article drafts written. `author_review.md`: four agent-ticked boxes unticked (DEC-024). Roadmap: stale M2 note on AP-001 to AP-008 brought up to date.

Nothing frozen was touched; no confirmatory run; no push; no network use by the page.

### M5 gate

Offline after the initial load (checker step 7), responsive (no horizontal scroll at 360 px; screenshots inspected), keyboard usable (40 of 40 focusable elements reached with a visible outline), no fabricated data (every published number is traced to a committed table and checked verbatim), no runtime service. **M5 is done.**

### Owner placeholders remaining

1. Author line and affiliation: "Mohamed Bechir Kefi (no affiliation; author metadata pending the owner's approval)" (manuscript, README, page footer, articles, CITATION.cff).
2. Repository URL: `<repository URL, not yet published>`.
3. Demo URL: `<demo URL, not yet published>`.
4. The owner's full-text review of the manuscript (M6 checklist); the manuscript title remains a working title (the post-M4 title approval named other projects).

### Next action

M6 (release candidate), on the owner's word.


## 2026-11-25: M6 release candidate 0.1.0-rc1

**Authority:** owner, 2026-11-25, "Next" (second) (`labs/_shared/owner-approvals-2026-11-25e.md`); coordinator brief `labs/_shared/M6-brief.md`. **Starting state:** `98e57b1`, working tree clean. Decisions: DEC-025. `$S` below is the session scratch folder outside the repository.

### Commands and actual outputs

```
# Clean clone of 98e57b1 (local, no network)
$ git clone -q <this repository> $S/clone && cd $S/clone
$ ../.tools/py/bin/uv sync --frozen --all-groups --all-extras      (absolute path to labs/.tools used)
$ .venv/bin/python -m pytest -q                                   121 passed in 26.01s
$ UV=<uv> scripts/rigged smoke                                     M2 smoke (revision 16e3b4f): all 4 tables differ (expected: src changed in the pre-data amendments)
$ scripts/rigged smoke --matrix SMOKE --out results/exploratory/m3-smoke
$ scripts/rigged smoke --matrix SIZING --out results/exploratory/m3-sizing
  3 tables and the SVG byte-identical in each; summary.csv differs only in runtime_mean_s (8 and 20 rows, max deviation 0 elsewhere)
$ for e in EXP-001..EXP-004: PYTHONPATH=src .venv/bin/python -m rigged.cli report --experiment $e
  exit 0 x4; git status clean (generated tables, figures and reports byte-identical)
$ shasum -a 256 -c SHA256SUMS (results/EXP-001..004)              10, 10, 10, 11 OK; 0 failures
$ cd demo && npm ci --prefer-offline                              added 53 packages in 619ms
$ npm test                                                        Test Files 2 passed (2); Tests 18 passed (18)
$ npm run build                                                   index-B05VWmE4.js 251.67 kB; built in 265ms
$ node tools/a11y_check.mjs dist                                  9 PASS lines; A11Y-CHECK PASS
$ python3 scripts/export_demo_data.py && --check                  wrote 108217 bytes; matches; git status: 0 lines

# Working repository
$ ../.tools/py/bin/python scripts/build_pdfs.py --typ-dir $S/typ --png-dir $S/png
  manuscript.pdf 14 pages, supplementary.pdf 8, EXP-001 4, EXP-002 4, EXP-003 5, EXP-004 5 (largest 0.33 MB)
$ pypdf metadata check                                            6 of 6 titled; no e-mail address; no home-directory path
$ pandoc research/paper/manuscript.md -s -t latex -o research/paper/manuscript.tex   regenerated (pandoc 3.6.3)
$ python3 scripts/check_links.py                                  55 Markdown files, 23 links, 8 bib entries: PASS (after 1 fix)
$ python3 scripts/build_artifact_manifest.py                      21 entries (2 figure definitions corrected)
$ python3 scripts/export_demo_data.py                             wrote demo/public/data/results.json (108290 bytes)
$ manifest checks (Python, scratch script)                        data: 6 of 6 hashes match; artifact: 42 of 42 paths, 21 of 21 result hashes, 45 of 45 config and protocol hashes
$ secret scan of 247 tracked files                                e-mail 1 (public no-reply trailer in CLAUDE.md), tokens 0, private keys 0, secret assignments 0, .env 0, home paths 51 in 10 files
$ licence list (.venv metadata, demo/node_modules, package-lock)  14 Python + 84 npm; 0 flagged
$ .venv/bin/python -m pytest -q                                   124 passed in 7.21s (3 new tests in tests/test_links.py)
$ cd demo && npm ci --prefer-offline && npm test && npm run build && node tools/a11y_check.mjs dist
  Tests 18 passed (18); built in 269ms; A11Y-CHECK PASS
```

### What was done

1. **Clean clone:** `research/publication/reproducibility_report.md` rewritten with the outputs above. The M3 smoke matrices reproduce exactly (runtime fields aside); the M2 smoke outputs predate the amendments and do not, as expected (now stated in `results/README.md`, which was stale since M3).
2. **PDFs:** `scripts/build_pdfs.py` added; six PDFs committed. Every manuscript and supplementary page, and the first page and figure page of each report, were rendered to PNG and inspected. Builder fixes: title block and PDF title metadata; duplicated "Figure N: Figure N" captions; cramped table columns. Source fixes: strip plots embedded in the four reports; 14 lists that rendered inline; Figure 3 and 4 captions that said "P0" for plots that also show other policies; one code comment that wrapped. Disclosed, not fixed: Figure 2's crowded axis labels (checksummed result file).
3. **References and links:** each cited paper's full text was opened (arXiv or PMLR PDF, text extracted locally) and the passage behind each statement checked; 0 read in full, 7 passage-checked, 1 dataset page, 1 unverified (not cited). CLM-021 and CLM-022 narrowed; manuscript section 2 names the section or theorem. `scripts/check_links.py` and `tests/test_links.py` added.
4. **Scans:** `research/publication/dependency_licences.md` added; `demo/.npmrc` gained its SPDX header.
5. **CITATION.cff:** did not parse at HEAD; repaired; `date-released` removed; version 0.1.0-rc1; title equal to the manuscript's.
6. **Owner checklist:** no box ticked or unticked (none was agent-ticked); "Prepared for the owner (M6, 2026-11-25)" added with what to read, open decisions and the placeholder table.
7. **Release checklist:** 10 items ticked with evidence; the two owner items open.

Nothing frozen was touched (protocols, configs, seeds, `freeze.json`, `results/` apart from `results/README.md`); `src/` unchanged; no confirmatory run; licence files unchanged; nothing pushed.

### Note on home-directory paths (append-only records)

Earlier entries of this file, `research/decision_log.md` and `research/experiment_journal.jsonl` contain absolute paths under the owner's home folder (10 occurrences in total at M6). They are left as written because these records are append-only; an owner-approved edit could replace them with repository-relative paths before a public release.

### Risks and items for the owner

- The owner review checklist and every open decision are in `research/publication/author_review.md`, M6 section.
- Figure 2 remains crowded; regenerating it would touch a checksummed result file.

### Next action

The owner's review (`author_review.md`) and, separately, any G-PUBLIC decision. M6 is not done until the owner signs off.

### Fresh clone of the release candidate (94421ba)

```
$ git clone -q <this repository> $S/clone2                        HEAD 94421ba
$ uv sync --frozen --all-groups --all-extras                      exit 0
$ .venv/bin/python -m pytest -q                                   124 passed in 9.96s
$ python3 scripts/check_links.py                                  56 Markdown files, 23 links, 8 bib entries: PASS
$ CITATION.cff with yaml.safe_load                                parses
$ scripts/rigged smoke --matrix SMOKE --out results/exploratory/m3-smoke
  contrasts, policy_vs_p0, analytic_check identical; summary.csv differs only in runtime_mean_s (8 rows)
$ python3 scripts/export_demo_data.py --check                     results.json matches the export
$ cd demo && npm ci --prefer-offline && npm test && npm run build && node tools/a11y_check.mjs dist
  added 53 packages; Tests 18 passed (18); built in 262ms; A11Y-CHECK PASS
$ git status --short | wc -l                                      0
```

Both clones ($S/clone and $S/clone2), created in this session, were deleted.

## 2026-11-26: owner answers of 2026-11-26 applied

**Authority:** owner, 2026-11-26, decision sheet (`labs/_shared/owner-approvals-2026-11-26.md`); coordinator brief `labs/_shared/OWNER-ANSWERS-brief.md`. **Starting state:** `56791be`, working tree clean. Decision: DEC-026. `$S` is the session scratch folder outside the repository.

### Commands and actual outputs

```
$ ../.tools/py/bin/python scripts/build_pdfs.py --typ-dir $S/typ --png-dir $S/png
  manuscript.pdf 333233 bytes (13 pages, was 14), supplementary.pdf (source unchanged: restored with git checkout),
  EXP-001 4 pages, EXP-002 4, EXP-003 5, EXP-004 5
$ ../.tools/pandoc research/paper/manuscript.md -s -t latex -o research/paper/manuscript.tex
$ pypdf: 5 rebuilt PDFs titled; no home path, no e-mail address in their bytes
$ PNG inspection: manuscript pages 1 (author line), 12 (repository URL), 13 (demo URL, section 11); EXP-001 page 1 (authorship row)
$ PYTHONPATH=src python3 -c "rigged.report.build_pdf(<scratch copy of results/exploratory/degen/report.md>)"   PDF written, 197425 bytes (new default tool paths)
$ .venv/bin/python -m pytest -q                                   124 passed in 9.08s
$ python3 scripts/check_links.py                                  56 Markdown files, 23 links, 8 bib entries: PASS
$ python3 scripts/export_demo_data.py --check                     results.json matches the export
$ cd demo && npm ci --prefer-offline                              added 53 packages in 18s
$ npm test                                                        Test Files 2 passed (2); Tests 18 passed (18)
$ npm run build                                                   index-DSnvotB6.js 251.70 kB; built in 292ms (folder dist/)
$ node tools/a11y_check.mjs dist                                  A11Y-CHECK PASS (incl. "no request leaves the local origin")
$ git commit                                                      e7df1bc
$ python3 scripts/export_demo_data.py                             wrote demo/public/data/results.json (108290 bytes); git status: 0 lines
$ git grep -c <home path>                                          36 in 7 files (4 run.log, progress.md, decision_log.md, experiment_journal.jsonl)
```

### What was done

A1, B1, B2, B3, B6 to B11, B13, B14 and R-RIGGED-1 applied or recorded as listed in DEC-026: URLs filled, author line "Mohamed Bechir Kefi, independent researcher", working-title marks removed, `CITATION.cff` (`repository-code`, `affiliation`, placeholder comment removed), `demo/wrangler.jsonc` added, home paths scrubbed from `CLAUDE.md`, `research/feasibility.md` and `src/rigged/report.py`, release notes and the B8 record added to `release_checklist.md`, reproducibility report section 7, `author_review.md` section "Owner answers recorded (2026-11-26)". No box ticked; no result, config, seed, frozen file or checksummed output changed; nothing pushed or deployed.

### Next action

The owner: B15 article drafts, B16 full-text review and sign-off, B18 release. The coordinator deploys the demo.

## 2026-11-26: demo brand identity, motion and UI redesign

**Authority:** owner request of 2026-11-26; coordinator brief `labs/_shared/DEMO-BRAND-brief.md`. Decision DEC-027. **Starting state:** `a83cea8`, working tree clean. Presentation only: no result, data export, fixture, test expectation, frozen file or checksummed output changed; nothing pushed or deployed.

### Changed files

`demo/DESIGN.md` (new: plan, review against generated-page tells, two screenshot critique passes); `demo/src/Hero.tsx`, `demo/src/motion.ts` (new); `demo/src/App.tsx`, `Explorer.tsx`, `charts.tsx`, `Sandbox.tsx`, `main.tsx`, `style.css`; `demo/index.html` (theme colour, Open Graph tags, favicons); `demo/package.json` and `package-lock.json` (two Fontsource packages); `demo/public/brand/` (marks, lockups, wordmark, favicon SVG and 32 px PNG, `og.png` 1200 by 630); `demo/public/licenses/` (two OFL texts); `demo/README.md` (brand line, third-party notes).

### Commands and actual outputs

```
$ npm_config_before=2026-11-12 npm install --save-exact @fontsource/libre-caslon-text @fontsource/barlow-semi-condensed
  added 2 packages; versions 5.3.0 and 5.3.0
$ python3 -I svg_audit.py demo/public/brand/*.svg               no FAIL; marks 100, lockups and wordmark 91 (font-outline angle warnings)
$ npm test                                                        Test Files 2 passed (2); Tests 18 passed (18)
$ npm run build                                                   index-DAJq9arR.js 260.71 kB (gzip 81.17 kB), index-BHPGUEWk.css 13.97 kB; dist/ 667,968 bytes in total
$ node tools/a11y_check.mjs dist                                  9 PASS lines (keyboard 45 reached of 45; overflow 0px at 360 px; 0 running animations under reduced motion; no request leaves the local origin); A11Y-CHECK PASS
$ .venv/bin/python -m pytest -q                                   124 passed in 7.28s
$ .venv/bin/python -m pytest -q tests/test_demo_export.py         5 passed (after the demo README change)
```

Screenshots (Chrome headless, 1440 px and 390 px) are kept outside the repository.

### Next action

The coordinator deploys `demo/dist` with `demo/wrangler.jsonc`. The owner: B15, B16, B18 as before.

## 2026-11-26: unique typeface pair across the labs (owner request)

Brief: `labs/_shared/FONT-UNIQUE-brief.md`, row RIGGED (Libre Caslon Text and Karla; change the sans face). No number, data, fixture, test expectation, accessible name or scientific wording changed.

### Changes

- `demo/package.json`, `package-lock.json`: removed `@fontsource/barlow-semi-condensed` 5.3.0; added `@fontsource-variable/karla` 5.3.0 (exact, `npm_config_before=2026-11-12`). Karla has `tnum`, so numbers stay in the sans face with tabular figures.
- `demo/src/main.tsx`: imports `@fontsource-variable/karla/wght.css`. `demo/src/style.css`: `--rule` stack is now Karla; type re-tuned for the wider face (navigation 0.97 rem, tables 0.95 rem and 0.9 rem below 40 rem, tags 0.85 rem, key figures weight 650 with tighter tracking).
- `demo/public/licenses/`: `OFL-karla.txt` replaces the Barlow licence. `demo/src/App.tsx`: footer font credit names Karla (Jonny Pinhorn).
- `demo/public/brand/og.png`: the tagline "One rule, two starting distributions" redrawn in Karla 600 (instance cut with fontTools, drawn with Pillow); the rest of the image unchanged. Logo marks and wordmark are Libre Caslon Text outlines and were not redrawn.
- `demo/DESIGN.md` (type section: why Karla, re-tuned scale), `demo/README.md` (third-party font table).

### Checks (actual results)

- `npm test`: 2 files, 18 tests passed. `npm run build`: built; `dist` 756 KB. `node tools/a11y_check.mjs dist`: A11Y-CHECK PASS.
- `.venv/bin/python -m pytest -q tests/test_demo_export.py`: 5 passed.
- Screenshots through the DevTools protocol at 1440 px and 390 px (kept outside the repository): no horizontal page overflow; wide tables scroll inside their own container as before.

### Next action

None for this brief. Deployment is the coordinator's.
