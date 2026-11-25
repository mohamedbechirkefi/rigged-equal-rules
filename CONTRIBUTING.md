<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# Contributing to RIGGED

RIGGED is an independent, source-available research project maintained by Mohamed Bechir Kefi: algorithmic fairness.

Technical suggestions, bug reports, reproducibility results, corrections and Pull Requests are welcome. The project is available for non-commercial research under the RIGGED Source-Available Non-Commercial Research License v1.0 ([LICENSE](LICENSE)); it is not OSI-approved open-source software.

## 1. Before you start

For major changes, open an Issue first. Read `master_prompt.md`, `research/protocol.md` and `research/claims_register.csv`: frozen protocols are never changed silently, and every reported number must trace to a result file.

## 2. Pull Request requirements

- Your contribution is original or appropriately licensed, and you have the right to submit it.
- No credentials, secrets, confidential information or personal data.
- Relevant tests are included and pass; you report what you actually ran.
- Third-party dependencies and data sources are identified with their licenses.
- New files carry the header `SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0` where the format allows.
- You accept the Contributor License Agreement before your contribution is merged.

## 3. Contributor License Agreement

A recorded acceptance of [CLA.md](CLA.md) is required before merging copyrightable contributions. When you open a Pull Request, the "CLA Assistant" check comments on it; read the CLA, then post this exact comment:

    I have read the RIGGED CLA v1.0 and I hereby sign it

The check records your public GitHub username and account ID, the date and the PR. You sign once. If the check does not update, comment `recheck`. Checking a box is not a signature; the comment is.

The CLA lets the maintainer use, modify, distribute, relicense and commercially exploit accepted contributions. You keep the copyright in your original contributions.

## 4. Governance

Mohamed Bechir Kefi is the project owner and lead maintainer, and the only person who can change the protected `main` branch. The maintainer decides the research direction, protocol freezes, claims, releases and licensing.

## 5. Privacy and disclosure

Never commit an e-mail address, a name or any other personal identifier in code, logs, fixtures or results. Report security issues privately through GitHub's private vulnerability reporting.

## 6. Development commands

Tool paths are those of the maintainer's machine; adjust them to your installation.

```
# Resolve and lock dependencies (uv 0.9.5; distributions uploaded before 2026-11-10 only)
uv lock

# Install the locked environment
uv sync --frozen

# Run the tests (available from M2)
uv run pytest

# Generate the manuscript LaTeX source (not compiled locally: no TeX distribution)
pandoc research/paper/manuscript.md -s -t latex -o research/paper/manuscript.tex

# Build a PDF through Typst (pandoc to Typst, then the typst Python package)
pandoc research/paper/manuscript.md -s -t typst -V mainfont="Libertinus Serif" -o build/manuscript.typ
python -c "import typst; typst.compile('build/manuscript.typ', output='build/manuscript.pdf')"
```

## 7. Running the engine (M2)

```
# Command-line interface (UV=/path/to/uv if uv is not on PATH)
scripts/rigged test                       # whole test suite
scripts/rigged smoke                      # protocol smoke matrix, exploratory -> results/exploratory/smoke/
scripts/rigged smoke --matrix SIZING      # exploratory sizing run at n = 20,000 on seeds 1000-1019
scripts/rigged smoke --matrix DEGEN       # exploratory degenerate-case probe
scripts/rigged run --experiment EXP-001   # refused (exit 2) until the owner freezes the protocol
scripts/rigged report --input results/exploratory/smoke --pdf
```

PDFs use pandoc and the typst Python package; set `RIGGED_PANDOC` and `RIGGED_TYPST_PYTHON` if the tools live elsewhere.

## M4 evidence pipeline (2026-11-25)

```
# Exploratory M4 confounder checks (JRN-0015, JRN-0016); never change a frozen verdict
PYTHONPATH=src .venv/bin/python scripts/m4_exploratory.py
# Evidence audit: raw-output re-derivation and number trace
PYTHONPATH=src .venv/bin/python scripts/m4_evidence_audit.py
# Supplementary tables and artifact manifest, from committed results
python3 scripts/build_supplementary.py
python3 scripts/build_artifact_manifest.py
```


## M5 demo (2026-11-25)

```
# Demo data from committed tables (deterministic; --check compares with the committed file)
python3 scripts/export_demo_data.py
# Sandbox test fixture from the Python engine (test fixture, not a result)
PYTHONPATH=src .venv/bin/python scripts/make_demo_fixture.py
# Build, test and check the static page (Node 22)
cd demo && npm ci && npm test && npm run build && npm run preview
node tools/a11y_check.mjs dist --screenshots <dir>   # from demo/
```


## M6 release candidate (2026-11-25)

```
# Manuscript, supplementary and experiment-report PDFs (pandoc to Typst; optional page PNGs for inspection)
../.tools/py/bin/python scripts/build_pdfs.py [--typ-dir <dir>] [--png-dir <dir>]
# LaTeX source of the manuscript (not compiled locally)
../.tools/pandoc research/paper/manuscript.md -s -t latex -o research/paper/manuscript.tex
# Relative links, quoted repository paths and citation keys (also run by tests/test_links.py)
python3 scripts/check_links.py
```
