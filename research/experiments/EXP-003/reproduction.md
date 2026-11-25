<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# EXP-003 reproduction

Revision b455d59294ea98e2b050ef30f20bc74b7993969e; dependencies in `uv.lock`; synthetic data.

```
../.tools/py/bin/uv sync --frozen --all-groups --all-extras
.venv/bin/python -m pytest -q                      # expected: 116 passed
scripts/run_confirmatory.sh EXP-003
PYTHONPATH=src .venv/bin/python -m rigged.cli report --experiment EXP-003
```

**Exploratory diagnosis (JRN-0014):**

```
PYTHONPATH=src .venv/bin/python -m rigged.cli run --experiment EXP-003 --exploratory --seed-offset 1000 --seeds 20
PYTHONPATH=src .venv/bin/python -m rigged.cli report --input results/exploratory/exp-003-x
```

**Outputs:** `results/EXP-003/` contains `results.json` (SHA-256 ad64b5ebbf349eced4f93ea51c57f7694c4412ab7dcbab3c213dd3175167f3e0), `run_manifest.json`, `provenance.json`, `tables/*.csv`, the figure and `SHA256SUMS`. The diagnosis is in `results/exploratory/exp-003-x/`. Use a separate clone.
