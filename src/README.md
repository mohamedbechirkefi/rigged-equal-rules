<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# src/

Python package `rigged` (M2). All data it produces are synthetic; Groups A and B are abstract.

| Module | Role |
|---|---|
| `config.py` | Typed, validated cell and run configurations; canonical config hash |
| `numerics.py` | Normal CDF and quantile, latent families (Gaussian, Student t3, shifted log-normal), Student t quantile; no SciPy |
| `generator.py` | Seeded two-group generator SYN-001 with common random numbers; separate fitting and evaluation streams |
| `policies.py` | P0 (baseline, common raw threshold), P1 (common calibrated threshold), P2 (selection-rate parity), P3 (equal opportunity); seeded tie-breaking |
| `metrics.py` | Group confusion matrices, rates, ECE, utility, gaps; zero denominators give null with a reason |
| `analytic.py` | Population values of P0 by numerical integration (implementation check) |
| `stats.py` | Seed-level summaries: percentile bootstrap, t-interval, standardised effect |
| `matrices.py` | Draft matrices of EXP-001 to EXP-003 and the exploratory SMOKE, SIZING and DEGEN matrices |
| `runner.py` | Config to results; failures recorded, never dropped; result bundle and run manifest |
| `schema.py`, `schemas/` | Versioned JSON schemas (result bundle 1.0.0, run manifest 1.0.0), validated at export and import |
| `protocol_guard.py` | Reads the registry and protocols; a confirmatory run needs a frozen, hash-matching protocol |
| `report.py` | Tables (CSV, Markdown), SVG figures and an optional PDF (pandoc to Typst) from result files |
| `cli.py` | `smoke`, `run`, `report`, `test` |

Run with `scripts/rigged <command>` or `PYTHONPATH=src uv run --frozen python -m rigged.cli <command>`.
