# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Decides whether an experiment's protocol is frozen. Confirmatory runs require a frozen protocol.

An experiment counts as frozen only if all of these hold (fail closed otherwise):

1. its registry row carries a protocol hash equal to the SHA-256 of its protocol file as it is now;
2. neither the experiment protocol nor the project protocol declares itself a draft;
3. the freeze record ``research/freeze.json`` exists and lists the experiment;
4. the SHA-256 of ``research/protocol.md``, of the experiment protocol and of its config file
   (``research/experiments/EXP-NNN/config.json``) equal the values in the freeze record;
5. when the caller passes the config built by the current code, the config file equals it
   (a code change that alters the matrix is refused);
6. when the record lists a data manifest hash for the experiment, ``data/manifest.json`` matches it.

Freezing is the owner's decision (G-FREEZE); this module only reads the records.
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from .environment import REPO_ROOT

FREEZE_RECORD = Path("research") / "freeze.json"


@dataclass(frozen=True)
class ProtocolStatus:
    experiment_id: str
    path: str
    sha256: str
    frozen: bool
    reason: str


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _is_draft(text: str) -> bool:
    head = "\n".join(text.splitlines()[:12]).upper()
    return "DRAFT" in head or "NOT FROZEN" in head


def _strip(h: str) -> str:
    return (h or "").strip().removeprefix("sha256:")


def protocol_status(experiment_id: str, root: Path = REPO_ROOT, expected_config: dict | None = None) -> ProtocolStatus:
    proto = root / "research" / "experiments" / experiment_id / "protocol.md"
    rel = str(proto.relative_to(root))

    def no(reason: str, digest: str = "") -> ProtocolStatus:
        return ProtocolStatus(experiment_id, rel, digest, False, reason)

    if not proto.exists():
        return no("protocol file missing")
    digest = sha256_file(proto)
    registry = root / "research" / "experiment_registry.csv"
    recorded = None
    if registry.exists():
        with registry.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if row.get("experiment_id") == experiment_id:
                    recorded = (row.get("protocol_hash") or "").strip()
    if recorded is None:
        return no("experiment not in the registry", digest)
    if not recorded:
        return no("no protocol hash recorded in the registry", digest)
    if _strip(recorded) != digest:
        return no("protocol file differs from the recorded hash", digest)
    project = root / "research" / "protocol.md"
    if _is_draft(proto.read_text(encoding="utf-8")) or (
            project.exists() and _is_draft(project.read_text(encoding="utf-8"))):
        return no("a protocol still declares DRAFT status", digest)
    record_path = root / FREEZE_RECORD
    if not record_path.exists():
        return no("no freeze record (research/freeze.json)", digest)
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
        entry = record["experiments"][experiment_id]
    except (ValueError, KeyError, TypeError):
        return no("freeze record unreadable or does not list the experiment", digest)
    if not project.exists() or _strip(record.get("project_protocol", {}).get("sha256", "")) != sha256_file(project):
        return no("research/protocol.md differs from the freeze record", digest)
    if _strip(entry.get("protocol_sha256", "")) != digest:
        return no("experiment protocol differs from the freeze record", digest)
    cfg = root / entry.get("config_path", f"research/experiments/{experiment_id}/config.json")
    if not cfg.exists():
        return no("frozen config file missing", digest)
    if _strip(entry.get("config_sha256", "")) != sha256_file(cfg):
        return no("config file differs from the freeze record", digest)
    if expected_config is not None:
        try:
            on_disk = json.loads(cfg.read_text(encoding="utf-8"))
        except ValueError:
            return no("config file is not valid JSON", digest)
        if on_disk != json.loads(json.dumps(expected_config)):
            return no("the matrix built by the current code differs from the frozen config", digest)
    if entry.get("data_manifest_sha256"):
        manifest = root / "data" / "manifest.json"
        if not manifest.exists() or _strip(entry["data_manifest_sha256"]) != sha256_file(manifest):
            return no("data/manifest.json differs from the freeze record", digest)
    return ProtocolStatus(experiment_id, rel, digest, True, "frozen: protocol, config and freeze record match")
