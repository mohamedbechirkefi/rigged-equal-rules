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
