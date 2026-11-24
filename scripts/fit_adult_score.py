# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Fit the EXP-004 score model on adult.data (protocol section 13, round 2) and record ingestion counts.

Exploratory fit, run once before the freeze. Writes research/experiments/EXP-004/score_model.json
(fitted values) and data/ingestion_report.json (schema, missingness and exclusion counts).
Never reads group labels for the fit and never computes an EXP-004 metric.

Usage: PYTHONPATH=src python scripts/fit_adult_score.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from rigged.adult import ARCHIVE, ARCHIVE_SHA256, fit_logistic, load_archive, parse_adult

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    digest = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    if digest != ARCHIVE_SHA256:
        print(f"archive SHA-256 mismatch: {digest}", file=sys.stderr)
        return 3
    texts = load_archive()
    report = {"archive_sha256": digest}
    tables = {}
    for name in ("adult.data", "adult.test"):
        tables[name], report[name] = parse_adult(texts[name])
    model = fit_logistic(tables["adult.data"])
    model["fitted_on"] = "adult.data (official training file) after ingestion exclusions"
    model["archive_sha256"] = digest
    out = ROOT / "research" / "experiments" / "EXP-004" / "score_model.json"
    out.write_text(json.dumps(model, indent=1) + "\n", encoding="utf-8")
    (ROOT / "data" / "ingestion_report.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=1))
    print(json.dumps(model, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
