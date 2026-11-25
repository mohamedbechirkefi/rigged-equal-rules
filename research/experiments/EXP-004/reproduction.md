<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# EXP-004 reproduction

- **Revision:** b455d59294ea98e2b050ef30f20bc74b7993969e.
- **Dependencies:** `uv.lock`.
- **Data:** UCI Adult (Becker and Kohavi 1996, DOI 10.24432/C5XW20, CC BY 4.0). The archive is committed at `data/raw/adult.zip` with SHA-256 7537312dd56c2b98035880805ce99e68183a30ee468aa5329d6df0fbb3cc21bb. The run refuses any other hash.

```
python3 scripts/download_adult.py                  # only if data/raw/adult.zip is missing
../.tools/py/bin/uv sync --frozen --all-groups --all-extras
.venv/bin/python -m pytest -q                      # expected: 116 passed
scripts/run_confirmatory.sh EXP-004
PYTHONPATH=src .venv/bin/python -m rigged.cli report --experiment EXP-004
PYTHONPATH=src .venv/bin/python scripts/exp004_base_rates.py
```

**Outputs:** `results/EXP-004/` contains:
- `results.json` (SHA-256 d00eae903565c63d58bba98477928dbe60bbde4ee4b1c17e980e4f8656ea58c5)
- `run_manifest.json`, `provenance.json`
- `tables/{summary,contrasts,policy_vs_p0,base_rate_gap}.csv`; `analytic_check.csv` is empty by design
- `figures/XFIG-EXP-004-01-eog.svg`
- `SHA256SUMS`

Metrics are expected to reproduce exactly; runtime and timestamp fields differ. Use a separate clone.
