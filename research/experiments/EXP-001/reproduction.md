<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# EXP-001 reproduction

- **Code revision:** b455d59294ea98e2b050ef30f20bc74b7993969e. The frozen hashes are in `research/freeze.json`.
- **Dependencies:** `uv.lock` (Python 3.12.1, numpy 2.5.4, jsonschema 4.26.0, pytest 9.2.0, hypothesis 6.170.15). Synthetic data; no external data.

Commands, from a clean clone at that revision:

```
../.tools/py/bin/uv sync --frozen --all-groups --all-extras
.venv/bin/python -m pytest -q                      # expected at b455d59: 116 passed
scripts/run_confirmatory.sh EXP-001                # run guard, run, report, provenance.json
PYTHONPATH=src .venv/bin/python -m rigged.cli report --experiment EXP-001   # regenerate tables and figure
```

**Outputs:** `results/EXP-001/`:
- `results.json` (schema rigged.result_bundle 1.0.0)
- `run_manifest.json`, `provenance.json`
- `tables/{summary,contrasts,policy_vs_p0,analytic_check}.csv`
- `figures/XFIG-EXP-001-01-eog.svg`
- `SHA256SUMS`

`results.json` SHA-256 at the confirmatory run: df4a452c70f2fa2c433cabce83c40c3aa247406f15c8ee5f48d90ebee8b520a2. The runner is deterministic under common random numbers. A rerun should reproduce every metric exactly; runtime, memory and timestamp fields will differ, so the file hash will differ. JRN-0009 showed byte-identical tables across two executions of SIZING.

Running the script inside this repository overwrites the committed `results/EXP-001/`. Use a separate clone.
