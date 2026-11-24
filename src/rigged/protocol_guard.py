# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Decides whether an experiment's protocol is frozen. Confirmatory runs require a frozen protocol.

An experiment counts as frozen only if (1) its registry row carries a protocol hash, (2) that hash
equals the SHA-256 of the experiment protocol file as it is now, and (3) neither the experiment
protocol nor the project protocol declares itself a draft. Anything else is unfrozen (fail closed).
Freezing is the owner's decision (G-FREEZE); this module only reads the records.
"""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path

from .environment import REPO_ROOT


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


def protocol_status(experiment_id: str, root: Path = REPO_ROOT) -> ProtocolStatus:
    proto = root / "research" / "experiments" / experiment_id / "protocol.md"
    rel = str(proto.relative_to(root))
    if not proto.exists():
        return ProtocolStatus(experiment_id, rel, "", False, "protocol file missing")
    digest = sha256_file(proto)
    registry = root / "research" / "experiment_registry.csv"
    recorded = None
    if registry.exists():
        with registry.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if row.get("experiment_id") == experiment_id:
                    recorded = (row.get("protocol_hash") or "").strip()
    if recorded is None:
        return ProtocolStatus(experiment_id, rel, digest, False, "experiment not in the registry")
    if not recorded:
        return ProtocolStatus(experiment_id, rel, digest, False, "no protocol hash recorded in the registry")
    if recorded.removeprefix("sha256:") != digest:
        return ProtocolStatus(experiment_id, rel, digest, False, "protocol file differs from the recorded hash")
    project = root / "research" / "protocol.md"
    if _is_draft(proto.read_text(encoding="utf-8")) or (
            project.exists() and _is_draft(project.read_text(encoding="utf-8"))):
        return ProtocolStatus(experiment_id, rel, digest, False, "a protocol still declares DRAFT status")
    return ProtocolStatus(experiment_id, rel, digest, True, "frozen: hash matches the registry")
