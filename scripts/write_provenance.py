# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Write results/EXP-NNN/provenance.json after a confirmatory run (M3 brief: provenance at run time).

Usage: python3 scripts/write_provenance.py EXP-NNN <exit status> <start UTC> <end UTC> <command>

Reads the run manifest written by the runner and adds what it does not hold: the exit status of the
command, the wrapper's start and end times, the SHA-256 of the data manifest, of the freeze record,
of the frozen config and protocols, and a SHA-256 manifest of every file in the result directory.
Computes no metric.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str]) -> int:
    exp, status, start, end, command = argv[1], int(argv[2]), argv[3], argv[4], argv[5]
    out = ROOT / "results" / exp
    man_path = out / "run_manifest.json"
    man = json.loads(man_path.read_text(encoding="utf-8")) if man_path.exists() else None
    files = sorted(p for p in out.rglob("*") if p.is_file() and p.name != "provenance.json")
    doc = {
        "experiment_id": exp,
        "command": command,
        "exit_status": status,
        "wrapper_start_utc": start,
        "wrapper_end_utc": end,
        "git_revision": man["environment"]["git_revision"] if man else None,
        "git_dirty": man["environment"]["git_dirty"] if man else None,
        "hardware": ({k: man["environment"][k] for k in ("cpu", "cpu_count", "machine", "os")} if man else None),
        "matrix_start_utc": man["environment"]["started_utc"] if man else None,
        "matrix_end_utc": man["environment"]["finished_utc"] if man else None,
        "wall_clock_s": man["wall_clock_s"] if man else None,
        "data_manifest_sha256": sha(ROOT / "data" / "manifest.json"),
        "freeze_record_sha256": sha(ROOT / "research" / "freeze.json"),
        "project_protocol_sha256": sha(ROOT / "research" / "protocol.md"),
        "experiment_protocol_sha256": sha(ROOT / "research" / "experiments" / exp / "protocol.md"),
        "config_sha256": sha(ROOT / "research" / "experiments" / exp / "config.json"),
        "runs": ([{"run_id": r["run_id"], "config_hash": r["config_hash"], "seed": r["seed"], "status": r["status"],
                   "runtime_s": r["runtime_s"]} for r in man["runs"]] if man else []),
        "per_run_timestamps": "not recorded per run by the runner (schema 1.0.0); each run's duration is runtime_s, "
                              "runs execute sequentially in run order between matrix_start_utc and matrix_end_utc",
        "files_sha256": {str(p.relative_to(out)): sha(p) for p in files},
    }
    (out / "provenance.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out / 'provenance.json'} ({len(doc['runs'])} runs, {len(files)} files hashed)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
