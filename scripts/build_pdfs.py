# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Build the manuscript, supplementary and experiment-report PDFs (pandoc to Typst, typst Python package).

Same pandoc options as ``rigged.report.build_pdf``, with these additions: ``--columns=400`` (so pipe tables
get natural column widths instead of widths proportional to their Markdown dashes), unnumbered figures and
8.5 pt table text (see ``HEADER``). The first level-one heading becomes the
document title (``-M title=...``, so the PDF title metadata is set), and Typst compiles with
``research/`` as its root, because the manuscript embeds figures from ``research/experiments/``.

Usage (from the repository root, with the toolchain Python that has the ``typst`` package):
    ../.tools/py/bin/python scripts/build_pdfs.py [--typ-dir DIR] [--png-dir DIR]

``--typ-dir`` keeps the intermediate ``.typ`` files there (default: deleted); ``--png-dir`` also renders every
page to PNG at 60 ppi for visual inspection. The PDF is written next to its Markdown source.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

import typst

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
# The zero-cost toolchain sits next to the repository (labs/.tools); RIGGED_PANDOC overrides it, as for the
# report generator.
PANDOC = os.environ.get("RIGGED_PANDOC", str(ROOT.parent / ".tools" / "pandoc"))
# Figure captions already carry "Figure N (FIG-NNN)", so Typst's own numbering is switched off; long tables
# break across pages and use a slightly smaller, unjustified type.
HEADER = ("#show figure: set block(breakable: true)\n#set figure(numbering: none)\n"
          "#show table: set text(size: 8.5pt)\n#show table: set par(justify: false)")
DOCUMENTS = [
    ("manuscript", RESEARCH / "paper" / "manuscript.md"),
    ("supplementary", RESEARCH / "paper" / "supplementary.md"),
    *[(f"exp-00{i}", RESEARCH / "experiments" / f"EXP-00{i}" / "report.md") for i in range(1, 5)],
]


def to_typst(md: Path, typ: Path) -> None:
    """The first level-one heading becomes the document title (PDF metadata and title block)."""
    lines = md.read_text(encoding="utf-8").splitlines()
    i = next(k for k, line in enumerate(lines) if line.startswith("# "))
    title = lines[i][2:].strip()
    body = "\n".join(lines[:i] + lines[i + 1:]) + "\n"
    subprocess.run([PANDOC, "-f", "markdown", "-s", "-t", "typst", "-M", f"title={title}",
                    "-V", "mainfont=Libertinus Serif", "-V", "fontsize=10pt",
                    "--columns=400", "-V", f"header-includes={HEADER}", "-o", str(typ)], input=body, text=True, cwd=md.parent, check=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--typ-dir")
    ap.add_argument("--png-dir")
    args = ap.parse_args()
    keep = Path(args.typ_dir) if args.typ_dir else None
    for name, md in DOCUMENTS:
        # The .typ file sits next to its source so relative image paths resolve; it is removed afterwards
        # unless --typ-dir asks for a copy.
        typ = md.with_name(f".{md.stem}.build.typ")
        to_typst(md, typ)
        try:
            pdf = md.with_suffix(".pdf")
            typst.compile(str(typ), output=str(pdf), root=str(RESEARCH))
            if args.png_dir:
                png = Path(args.png_dir)
                png.mkdir(parents=True, exist_ok=True)
                typst.compile(str(typ), output=str(png / f"{name}-{{p}}.png"), format="png", ppi=60,
                              root=str(RESEARCH))
            if keep:
                keep.mkdir(parents=True, exist_ok=True)
                (keep / f"{name}.typ").write_text(typ.read_text(encoding="utf-8"), encoding="utf-8")
        finally:
            typ.unlink()
        print(f"wrote {pdf.relative_to(ROOT)} ({pdf.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
