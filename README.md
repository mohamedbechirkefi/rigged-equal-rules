<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# RIGGED: when equal rules produce unequal outcomes

**Question.** Can equal rules yield unequal outcomes under different starting distributions?

**Status:** independent research manuscript / preprint draft, not peer-reviewed. Protocols frozen by the owner (2026-11-24, amended before data on 2026-11-25); 1,780 confirmatory runs at code revision b455d59, all ok; M4 (interpretation and evidence audit) and M5 (interactive demo) done; M6 release candidate 0.1.0-rc1 prepared (2026-11-25), awaiting the owner's review. The owner's full-text review of the manuscript is pending. Nothing is released or published.

![Screenshot of the RIGGED demo: the overview with the two headline results, 6.59 pp [6.20, 6.97] in simulation and -7.45 pp [-8.75, -6.05] on a real score, above the fairness trade-off explorer with its delta by rho cell picker and four dot-and-interval panels for the SR, EOG, PPV and FPR gaps.](docs/demo.png)

## Why it matters

A single score threshold is often called fair because it treats everyone the same way. This project measures, in a transparent and seeded setting, whether equally qualified individuals can still face different chances of selection when two abstract groups start from different distributions of qualification or are measured with different noise, and how alternative rules trade one fairness criterion against another. It then tests the synthetic prediction on one real score.

## Key findings (verified against committed results)

All intervals are 95% percentile bootstrap intervals over 20 seeds. EXP-001 to EXP-003 are simulated; EXP-004 uses real data.

- **One common threshold (EXP-001, simulated).** A starting-distribution gap of half a standard deviation raises the equal-opportunity gap (EOG) by 6.59 pp [6.20, 6.97] against an equal-distribution control; the analytic value is 6.31 pp. H1 supported, and implied by the model.
- **Incompatible criteria (EXP-002, simulated).** No rule among P0 to P3 meets selection-rate, equal-opportunity and predictive parity within 2 pp once distributions differ; P2 and P3 cost utility (-0.01773 [-0.01859, -0.01688] and -0.00215 [-0.00249, -0.00181] per capita). H1 and H2 supported.
- **Base rate or shape (EXP-003, simulated).** At equal base rates, changing only dispersion gives gaps of 19.44 and -22.50 pp; at a fixed base-rate gap the sign reverses (-9.56 pp). H0 rejected. H4 carries a disclosed limitation (implementation check 56 of 60, DEC-019).
- **A real score (EXP-004, UCI Adult, Group B is hours-per-week below 40).** The base-rate prediction is disconfirmed with a sign reversal: -7.45 pp [-8.75, -6.05]. A calibrated common rule (P1) gives the predicted sign (+30.52 pp [25.63, 35.58]).

What survives is narrow and near-definitional: under one common rule, the gap follows where each group's qualified members sit relative to the cutoff; the base rate does not fix its sign or size.

## Experiments

| ID | Question | Data | Runs | Status and verdict | Report |
|---|---|---|---|---|---|
| EXP-001 | One common threshold under unequal starting distributions | simulated | 240 | confirmatory, complete; H1 supported | `research/experiments/EXP-001/report.md` |
| EXP-002 | Equal and constrained rules; incompatible criteria | simulated | 960 | confirmatory, complete; H1 and H2 supported | `research/experiments/EXP-002/report.md` |
| EXP-003 | Base rate versus distribution shape | simulated | 420 | confirmatory, complete; H0 rejected, H2 sign reversal (analytically determined), H3 and H4 sign kept (H4 with DEC-019) | `research/experiments/EXP-003/report.md` |
| EXP-004 | A real score (UCI Adult) | real | 160 | confirmatory, complete; H1-real disconfirmed (contradiction) | `research/experiments/EXP-004/report.md` |

Exploratory checks (JRN-0014 to JRN-0016) are labelled exploratory everywhere and change no verdict.

## Research navigation

- Manuscript: `research/paper/manuscript.md` (canonical), `research/paper/manuscript.pdf` and `research/paper/manuscript.tex` (generated), `research/paper/supplementary.md` and `research/paper/supplementary.pdf`. Each experiment report has a PDF next to it (`research/experiments/EXP-NNN/report.pdf`). PDFs are built with `scripts/build_pdfs.py` (pandoc to Typst).
- Protocols and registry: `research/protocol.md`, `research/experiments/EXP-NNN/protocol.md`, `research/experiment_registry.csv`, `research/freeze.json`.
- Evidence: `research/claims_register.csv`, `research/publication/` (artifact manifest, claims and evidence audits, second review pass).
- Raw results, tables and figures: `results/EXP-NNN/`.
- Decisions and limitations: `research/decision_log.md`, `research/limitations.md`.

## Interactive demo

`demo/` is a static page (TypeScript, React and Vite, pinned versions): the published results with their intervals, a fairness trade-off explorer and subgroup outcome charts over the EXP-002 and EXP-004 summary tables, the assumptions, the method and limitations, and a sandbox that runs a port of the engine in a Web Worker. Sandbox output is labelled and is not a research result. The page makes no request to any other host, collects nothing and works offline after the first load. Demo: <https://rigged-equal-rules.kefimohamedbechir.workers.dev> (Cloudflare Workers static assets, free plan).

Quick start (Node 22):

```
cd demo && npm ci && npm run build && npm run preview
```

The demo's data file is regenerated with `python3 scripts/export_demo_data.py` and checked by `tests/test_demo_export.py`.

## Reproduction

From the repository root:

```
../.tools/py/bin/uv sync --frozen --all-groups --all-extras
.venv/bin/python -m pytest -q
python3 scripts/download_adult.py            # EXP-004 only; checks the archive SHA-256
scripts/run_confirmatory.sh EXP-001          # likewise EXP-002, EXP-003, EXP-004
```

Full commands are in `CONTRIBUTING.md` and in each `research/experiments/EXP-NNN/reproduction.md`.

## Architecture

`src/rigged/`: generator (SYN-001), policies P0 to P3, metrics, analytic cross-check, runner, versioned result schema, run manifests, report generator and CLI. `scripts/`: confirmatory runner, evidence audit, supplementary and manifest builders, demo export. `demo/`: the static page.

## Data and licences

Synthetic data are generated by the project's seeded code. EXP-004 uses the UCI Adult dataset (Becker and Kohavi 1996, DOI 10.24432/C5XW20, CC BY 4.0), redistributed unchanged. Only age, education-num, capital-gain, capital-loss, hours-per-week and the income label are read. See `data/manifest.json`.

## Scope and limitations

Groups A and B are abstract groups, never protected groups; no protected attribute is used anywhere. Nothing here is a claim about real hiring, any real selection decision, workers or the people in the data. The EOG is one criterion among several; no fairness metric is presented as universal. The simulated results hold only within the generator's assumptions, and EXP-004 covers one simple score and one partition of one 1994 extract. Full list: `research/limitations.md` and manuscript section 7.

## Licence

RIGGED Source-Available Non-Commercial Research License v1.0 (`LICENSE`, `NOTICE.md`). This is a custom licence, not an OSI-approved open-source licence. Third-party material keeps its own terms.

## Citation

See `CITATION.cff`. Author: Mohamed Bechir Kefi, independent researcher. Repository: <https://github.com/mohamedbechirkefi/rigged-equal-rules>. An AI assistant (Claude, Anthropic) is disclosed as a research and development assistant, not as an author.
