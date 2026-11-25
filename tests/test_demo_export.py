# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""M5 consistency (master prompt 11.6): the demo shows the manuscript's numbers, exactly.

1. Re-running the export in memory reproduces the committed demo/public/data/results.json byte for byte.
2. Every display and interval_display string appears verbatim in research/paper/manuscript.md, or is a
   documented exception: per-cell explorer values must then appear verbatim in
   research/paper/supplementary.md, and group-level rates are listed under display_exceptions.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "demo" / "public" / "data" / "results.json"
MANUSCRIPT = (ROOT / "research" / "paper" / "manuscript.md").read_text(encoding="utf-8")
SUPPLEMENTARY = (ROOT / "research" / "paper" / "supplementary.md").read_text(encoding="utf-8")


def _export_module():
    spec = importlib.util.spec_from_file_location("export_demo_data", ROOT / "scripts" / "export_demo_data.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _displays(node, path="$"):
    """Yield (path, dict) for every dict carrying a display string."""
    if isinstance(node, dict):
        if isinstance(node.get("display"), str):
            yield path, node
        for k, v in node.items():
            yield from _displays(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _displays(v, f"{path}[{i}]")


def test_committed_results_json_equals_fresh_export():
    mod = _export_module()
    assert RESULTS.read_text(encoding="utf-8") == mod.render(mod.build())


def test_schema_and_no_timestamps():
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    assert data["schema"] == "lab-demo-results" and data["schema_version"] == "1.0.0"
    assert data["code_revision"].startswith("b455d59")
    text = RESULTS.read_text(encoding="utf-8")
    for marker in ("created", "generated_at", "timestamp", "2026-"):
        assert marker not in text, marker
    ids = [e["id"] for e in data["experiments"]]
    assert ids[:4] == ["EXP-001", "EXP-002", "EXP-003", "EXP-004"]  # every registered experiment


def test_every_display_string_is_in_the_manuscript_or_documented():
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    documented = data["display_exceptions"]
    assert set(documented) == {"supplementary", "group-rate"}
    checked = 0
    missing = []
    for path, d in _displays(data):
        strings = [d["display"]] + ([d["interval_display"]] if d.get("interval_display") else [])
        if "exception" in d:
            assert d["exception"] == "group-rate", path
            assert path.endswith(".tpr_a") or path.endswith(".tpr_b"), path
            continue
        if d.get("source") == "supplementary":
            haystack = SUPPLEMENTARY
        else:
            assert path.startswith("$.experiments"), path
            haystack = MANUSCRIPT
        for s in strings:
            checked += 1
            if s not in haystack:
                missing.append((path, s))
    assert not missing, missing
    assert checked > 150


def test_no_sex_or_protected_attribute_in_the_export():
    text = RESULTS.read_text(encoding="utf-8").lower()
    for word in ("\"sex\"", " sex ", "race", "gender", "female", "male"):
        assert word not in text, word


def test_public_texts_use_only_manuscript_numbers():
    """README, CITATION.cff, the article drafts and the demo README print no decimal number that the
    manuscript (or its supplementary file) does not print."""
    import re

    pattern = re.compile(r"(?<![\w.])[-+]?\d+\.\d+(?![\w.])")
    bad = []
    for rel in ("README.md", "CITATION.cff", "articles/medium.md", "articles/linkedin.md", "demo/README.md"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        for num in pattern.findall(text):
            if num in ("1.0", "1.2.0", "2.0"):
                continue
            if num not in MANUSCRIPT and num not in SUPPLEMENTARY:
                bad.append((rel, num))
    assert not bad, bad
