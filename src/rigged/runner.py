# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Experiment runner: config to results. Separate from generation, policies, metrics and serialisation."""

from __future__ import annotations

import time
import tracemalloc
from pathlib import Path

from . import GENERATOR_VERSION, RESULT_SCHEMA_VERSION, __version__
from .config import RunSpec
from .environment import environment, peak_rss_bytes, utc_now
from .generator import STREAM_EVAL, STREAM_FIT, build_population, draw
from .matrices import Matrix
from .metrics import evaluate
from .policies import PolicyFitError, fit_calibration, fit_policy
from .protocol_guard import ProtocolStatus
from .schema import dump, validate


def execute(spec: RunSpec, draws_cache: dict | None = None, trace_memory: bool = True) -> dict:
    """Run one spec and return its result record. Policy-fit failures are recorded, not raised."""
    t0 = time.perf_counter()
    if trace_memory:
        tracemalloc.start()
    rec = {"run_id": spec.run_id, "experiment_id": spec.experiment_id, "cell_id": spec.cell.cell_id,
           "policy": spec.policy, "seed": spec.seed, "n": spec.n, "config": spec.to_dict(),
           "config_hash": spec.config_hash(), "status": "ok", "failure_reason": None}
    try:
        key = (spec.seed, spec.n)
        if draws_cache is not None and key in draws_cache:
            d_fit, d_eval = draws_cache[key]
        else:
            d_fit, d_eval = draw(spec.seed, STREAM_FIT, spec.n), draw(spec.seed, STREAM_EVAL, spec.n)
            if draws_cache is not None:
                draws_cache.clear()
                draws_cache[key] = (d_fit, d_eval)
        fit = build_population(spec.cell, d_fit)
        ev = build_population(spec.cell, d_eval)
        fp = fit_policy(spec.policy, fit, spec.cell)
        sel = fp.select(ev)
        # Group-blind calibrated score for the ECE metric, fitted on the fitting population only.
        cal = fit_calibration(fit.x, fit.y, spec.cell.calibration_bins)
        m = evaluate(ev.y, ev.group_b, sel, cal(ev.x), spec.cell.cost_ratio, spec.cell.ece_bins)
        rec["policy_fit"] = fp.to_dict()
        rec.update(m)
    except PolicyFitError as exc:
        rec["status"] = "failed"
        rec["failure_reason"] = f"PolicyFitError: {exc}"
    finally:
        peak = None
        if trace_memory:
            peak = int(tracemalloc.get_traced_memory()[1])
            tracemalloc.stop()
    rec["runtime_s"] = time.perf_counter() - t0
    rec["peak_traced_bytes"] = peak
    return rec


def run_matrix(matrix: Matrix, out_dir: Path, protocol: ProtocolStatus | None, command: str,
               trace_memory: bool = True, progress=None) -> tuple[dict, dict]:
    """Run every planned run of a matrix, validate and write result bundle and run manifest."""
    if matrix.label == "confirmatory" and (protocol is None or not protocol.frozen):
        raise PermissionError("confirmatory matrix requires a frozen protocol")
    started = utc_now()
    t0 = time.perf_counter()
    specs = matrix.runs()
    cache: dict = {}
    runs = []
    for i, spec in enumerate(specs):
        runs.append(execute(spec, cache, trace_memory))
        if progress is not None:
            progress(i + 1, len(specs), runs[-1])
    wall = time.perf_counter() - t0
    ok = sum(r["status"] == "ok" for r in runs)
    bundle = {
        "schema": "rigged.result_bundle", "schema_version": RESULT_SCHEMA_VERSION, "label": matrix.label,
        "matrix_id": matrix.matrix_id, "experiment_id": matrix.experiment_id, "description": matrix.description,
        "created_utc": started,
        "protocol": {"path": protocol.path if protocol else "research/protocol.md",
                     "sha256": protocol.sha256 if protocol else "",
                     "frozen": bool(protocol and protocol.frozen),
                     "status_reason": protocol.reason if protocol else "exploratory matrix; protocol not frozen"},
        "generator_version": GENERATOR_VERSION, "package_version": __version__, "n": matrix.n,
        "seeds": list(matrix.seeds), "counts": {"planned": len(specs), "ok": ok, "failed": len(runs) - ok},
        "runs": runs,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    digest = dump(bundle, "rigged.result_bundle", out_dir / "results.json")
    manifest = {
        "schema": "rigged.run_manifest", "schema_version": "1.0.0", "matrix_id": matrix.matrix_id,
        "label": matrix.label, "result_file": "results.json", "result_sha256": digest, "command": command,
        "wall_clock_s": wall, "peak_rss_bytes": peak_rss_bytes(), "environment": environment(started),
        "runs": [{"run_id": r["run_id"], "config_hash": r["config_hash"], "seed": r["seed"], "status": r["status"],
                  "runtime_s": r["runtime_s"], "peak_traced_bytes": r["peak_traced_bytes"]} for r in runs],
    }
    validate(manifest, "rigged.run_manifest")
    dump(manifest, "rigged.run_manifest", out_dir / "run_manifest.json")
    return bundle, manifest
