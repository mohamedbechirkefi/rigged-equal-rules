# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Capture of the execution environment for run manifests."""

from __future__ import annotations

import platform
import resource
import subprocess
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from . import __version__

REPO_ROOT = Path(__file__).resolve().parents[2]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git(args: list[str]) -> str | None:
    try:
        r = subprocess.run(["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def cpu_name() -> str:
    if sys.platform == "darwin":
        try:
            r = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True, timeout=5)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            pass
    return platform.processor() or platform.machine() or "unknown"


def peak_rss_bytes() -> int | None:
    """Peak resident set size of this process (ru_maxrss: bytes on macOS, KiB on Linux)."""
    try:
        r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except (OSError, ValueError):
        return None
    return int(r if sys.platform == "darwin" else r * 1024)


def environment(started_utc: str) -> dict:
    import os

    status = _git(["status", "--porcelain", "--untracked-files=no"])
    return {
        "git_revision": _git(["rev-parse", "HEAD"]),
        "git_dirty": None if status is None else bool(status),
        "python": platform.python_version(),
        "numpy": version("numpy"),
        "jsonschema": version("jsonschema"),
        "rigged": __version__,
        "os": f"{platform.system()} {platform.release()} ({platform.platform()})",
        "machine": platform.machine(),
        "cpu": cpu_name(),
        "cpu_count": os.cpu_count(),
        "started_utc": started_utc,
        "finished_utc": utc_now(),
    }
