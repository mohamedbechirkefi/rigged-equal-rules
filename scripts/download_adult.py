# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Download the UCI Adult archive (CC BY 4.0) into data/raw/ and record its provenance.

Deterministic: one fixed URL, one fixed file name. If the file already exists and matches the
expected SHA-256 recorded below, nothing is downloaded. The provenance record (URL, access date,
size, SHA-256 of the archive and of each member) is written to data/raw/adult.provenance.json.

Usage: python scripts/download_adult.py [--force]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

URL = "https://archive.ics.uci.edu/static/public/2/adult.zip"
LANDING = "https://archive.ics.uci.edu/dataset/2/adult"
DOI = "10.24432/C5XW20"
LICENCE = "CC BY 4.0 (stated on the dataset page)"
# Recorded at the first download (2026-11-24); a mismatch stops the script.
EXPECTED_SHA256 = "7537312dd56c2b98035880805ce99e68183a30ee468aa5329d6df0fbb3cc21bb"
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
TARGET = RAW / "adult.zip"
MAX_BYTES = 50 * 1024 * 1024


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--force", action="store_true", help="download even if the file exists")
    args = p.parse_args(argv)
    RAW.mkdir(parents=True, exist_ok=True)
    if TARGET.exists() and not args.force:
        data = TARGET.read_bytes()
        print(f"exists: {TARGET.relative_to(ROOT)} ({len(data)} bytes)")
    else:
        with urllib.request.urlopen(URL, timeout=60) as resp:  # noqa: S310 (fixed https URL)
            data = resp.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            print("REFUSED: archive larger than 50 MB", file=sys.stderr)
            return 2
        TARGET.write_bytes(data)
        print(f"downloaded {URL} -> {TARGET.relative_to(ROOT)} ({len(data)} bytes)")
    digest = sha256_bytes(data)
    if EXPECTED_SHA256 and digest != EXPECTED_SHA256:
        print(f"SHA-256 MISMATCH: got {digest}, expected {EXPECTED_SHA256}", file=sys.stderr)
        return 3
    members = {}
    with zipfile.ZipFile(TARGET) as zf:
        for info in sorted(zf.infolist(), key=lambda i: i.filename):
            b = zf.read(info.filename)
            members[info.filename] = {"bytes": len(b), "sha256": sha256_bytes(b)}
    prov = {
        "id": "EXT-001", "name": "UCI Adult", "url": URL, "landing_page": LANDING, "doi": DOI,
        "licence": LICENCE, "file": str(TARGET.relative_to(ROOT)), "bytes": len(data), "sha256": digest,
        "members": members,
        "recorded_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    (RAW / "adult.provenance.json").write_text(json.dumps(prov, indent=1) + "\n", encoding="utf-8")
    print(f"sha256 {digest}")
    for name, m in members.items():
        print(f"  {name}: {m['bytes']} bytes, sha256 {m['sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
