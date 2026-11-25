# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""M6: relative links, quoted repository paths and citation keys resolve (scripts/check_links.py)."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("check_links", ROOT / "scripts" / "check_links.py")
check_links = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_links)


def test_every_relative_link_and_quoted_path_resolves():
    files = check_links.tracked_markdown()
    assert len(files) > 20
    assert check_links.check_links(files) == []
    assert check_links.check_quoted_paths(files) == []


def test_every_bib_entry_is_cited_and_every_report_key_resolves():
    assert len(check_links.bib_entries()) == 8
    assert check_links.check_citations() == []


def test_checker_catches_broken_links(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text("# Title\n\n[a](missing.md) [b](doc.md#title) [c](doc.md#absent)\n", encoding="utf-8")
    problems = check_links.check_links([md])
    assert len(problems) == 2
    assert "missing.md" in problems[0] and "#absent" in problems[1]
