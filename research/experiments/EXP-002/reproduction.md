<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# EXP-002 reproduction

Revision b455d59294ea98e2b050ef30f20bc74b7993969e; dependencies in `uv.lock`; synthetic data.

```
../.tools/py/bin/uv sync --frozen --all-groups --all-extras
.venv/bin/python -m pytest -q                      # expected: 116 passed
scripts/run_confirmatory.sh EXP-002
PYTHONPATH=src .venv/bin/python -m rigged.cli report --experiment EXP-002
```

**Outputs:** `results/EXP-002/` contains `results.json`, `run_manifest.json`, `provenance.json`, `tables/*.csv`, `figures/XFIG-EXP-002-01-eog.svg` and `SHA256SUMS`.

`results.json` SHA-256: c1af46ad572af0f083091d669d83e1720e64941ef57a960a8ee59c53dfc369b3. Metrics are expected to reproduce exactly; runtime and timestamp fields differ. Use a separate clone, because the script overwrites the committed results.
