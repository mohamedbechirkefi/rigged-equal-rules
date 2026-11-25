# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Check relative links, quoted repository paths and citation keys in the tracked Markdown files (M6).

1. Every relative Markdown link or image ``[text](target)`` in a tracked ``.md`` file resolves to an existing
   file, and a ``#anchor`` resolves to a heading of the target (GitHub-style slug).
2. Every back-quoted repository path (for example ``research/paper/manuscript.md``) in the reader-facing
   documents (README, manuscript, supplementary, experiment reports, articles, publication folder) exists,
   resolved from the repository root or from the document's folder. Globs, placeholders and git-ignored
   outputs are skipped.
3. Every entry of ``research/paper/references.bib`` is cited in the manuscript (author and year), and every
   citation key used in the experiment reports resolves to a bib entry.

Usage: ``python3 scripts/check_links.py``; exit status 1 and one line per problem when anything fails.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[(?:[^\[\]]|\[[^\]]*\])*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
CODE = re.compile(r"`([^`\s]+)`")
FENCE = re.compile(r"^(```|~~~)")
PATH_HEAD = ("research/", "results/", "scripts/", "src/", "tests/", "data/", "demo/", "docs/", "articles/",
             "figures/", "tables/", "../experiments/")
READER_FACING = ("README.md", "research/paper/", "research/experiments/", "articles/", "research/publication/")
IGNORED_OUTPUTS = ("results/raw/", "demo/dist/", "demo/node_modules/", "build/")
BIB = ROOT / "research" / "paper" / "references.bib"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def tracked_markdown() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True, text=True, check=True)
    return [ROOT / p for p in out.stdout.split()]


def slug(heading: str) -> str:
    s = re.sub(r"[`*_]", "", heading.strip().lower())
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def anchors(md: Path) -> set[str]:
    return {slug(m.group(1)) for m in re.finditer(r"^#{1,6}\s+(.+?)\s*#*$", md.read_text(encoding="utf-8"),
                                                    re.M)}


def prose_lines(md: Path):
    fenced = False
    for n, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
        if FENCE.match(line.strip()):
            fenced = not fenced
            continue
        if not fenced:
            yield n, line


def check_links(files: list[Path]) -> list[str]:
    problems = []
    for md in files:
        for n, line in prose_lines(md):
            for target in LINK.findall(line):
                if re.match(r"^[a-z][a-z0-9+.-]*:", target):  # http:, https:, mailto: are external
                    continue
                path, _, frag = target.partition("#")
                dest = md if not path else (md.parent / path).resolve()
                where = f"{rel(md)}:{n}"
                if not dest.exists():
                    problems.append(f"{where}: link target missing: {target}")
                elif frag and dest.suffix == ".md" and frag not in anchors(dest):
                    problems.append(f"{where}: anchor missing: {target}")
    return problems


def check_quoted_paths(files: list[Path]) -> list[str]:
    problems = []
    for md in files:
        name = rel(md)
        if not name.startswith(READER_FACING):
            continue
        for n, line in prose_lines(md):
            for token in CODE.findall(line):
                token = token.rstrip(".,;:)").split("::")[0]  # pytest node ids name a file
                if not token.startswith(PATH_HEAD) or any(c in token for c in "*{}<>?|") or "NNN" in token:
                    continue
                if token.startswith(IGNORED_OUTPUTS) or ".." in token.replace("../experiments/", ""):
                    continue
                if not ((ROOT / token).exists() or (md.parent / token).exists()):
                    problems.append(f"{name}:{n}: quoted path missing: {token}")
    return problems


def bib_entries() -> dict[str, tuple[str, str]]:
    """key -> (first author's family name, year)."""
    text = BIB.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"@\w+\{([^,]+),(.*?)\n\}", text, re.S):
        body = m.group(2)
        author = re.search(r"author\s*=\s*\{([^,}]+)", body).group(1).strip()
        year = re.search(r"year\s*=\s*\{(\d{4})\}", body).group(1)
        out[m.group(1).strip()] = (author, year)
    return out


def check_citations() -> list[str]:
    problems = []
    entries = bib_entries()
    manuscript = (ROOT / "research" / "paper" / "manuscript.md").read_text(encoding="utf-8")
    body, _, references = manuscript.partition("\n## References")
    for key, (family, year) in entries.items():
        if not re.search(rf"{re.escape(family)}[^()\n]{{0,60}}\(?{year}", body):
            problems.append(f"references.bib: {key} ({family} {year}) is not cited in the manuscript text")
        if not re.search(rf"^- {re.escape(family)}, .*\({year}\)", references, re.M):
            problems.append(f"references.bib: {key} has no entry in the manuscript reference list")
    key_like = re.compile(r"\b(" + "|".join(sorted({re.sub(r"\d{4}$", "", k) for k in entries})) + r")(\d{4})\b")
    for report in sorted((ROOT / "research" / "experiments").glob("EXP-*/report.md")):
        for n, line in prose_lines(report):
            for name, year in key_like.findall(line):
                if f"{name}{year}" not in entries:
                    problems.append(f"{rel(report)}:{n}: citation key {name}{year} not in references.bib")
    return problems


def main() -> int:
    files = tracked_markdown()
    problems = check_links(files) + check_quoted_paths(files) + check_citations()
    for p in problems:
        print(p)
    n_links = sum(len(LINK.findall(line)) for md in files for _, line in prose_lines(md))
    print(f"{len(files)} Markdown files, {n_links} links, {len(bib_entries())} bib entries: "
          f"{'PASS' if not problems else f'FAIL ({len(problems)})'}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
