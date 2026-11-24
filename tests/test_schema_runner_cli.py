# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Integration: config to validated results, schema fail-closed, manifest, report, CLI guard."""

import copy
import hashlib
import json
from pathlib import Path

import pytest

from rigged import cli
from rigged.config import CellConfig, RunSpec
from rigged.matrices import Matrix, gaussian_cell
from rigged.protocol_guard import protocol_status
from rigged.report import build
from rigged.runner import execute, run_matrix
from rigged.schema import SchemaError, load, validate


def tiny_matrix(label="exploratory"):
    cells = (gaussian_cell(0.0, 1.0), gaussian_cell(0.5, 1.0),
             CellConfig(cell_id="G-noqualB", mu_b=-6.0, p_b=0.02))
    return Matrix("TINY", "TINY", label, "tiny test matrix", cells,
                  {c.cell_id: ("P0", "P1", "P2", "P3") for c in cells}, (2000, 2001, 2002), 400,
                  contrasts=(("d0.50-r1.00", "d0.00-r1.00"),))


@pytest.fixture(scope="module")
def tiny_run(tmp_path_factory):
    out = tmp_path_factory.mktemp("tiny")
    bundle, manifest = run_matrix(tiny_matrix(), out, None, "pytest")
    return out, bundle, manifest


def test_run_matrix_writes_valid_bundle_and_manifest(tiny_run):
    out, bundle, manifest = tiny_run
    assert bundle["counts"]["planned"] == 3 * 4 * 3 == len(bundle["runs"])
    assert load(out / "results.json", "rigged.result_bundle") == json.loads((out / "results.json").read_text())
    m = load(out / "run_manifest.json", "rigged.run_manifest")
    assert m["result_sha256"] == hashlib.sha256((out / "results.json").read_bytes()).hexdigest()
    assert m["environment"]["numpy"] == "2.5.4"
    assert len(m["runs"]) == len(bundle["runs"])


def test_failures_are_recorded_not_dropped(tiny_run):
    _, bundle, _ = tiny_run
    failed = [r for r in bundle["runs"] if r["status"] == "failed"]
    # Group B has (almost surely) no qualified member at mu_B = -6: P3 cannot be fitted.
    assert failed and all(r["policy"] == "P3" and r["cell_id"] == "G-noqualB" for r in failed)
    assert all("no qualified member" in r["failure_reason"] for r in failed)
    assert bundle["counts"]["failed"] == len(failed)


def test_runs_are_deterministic():
    spec = RunSpec("X", gaussian_cell(0.5, 1.5), "P1", 2100, 1000)
    a, b = execute(spec, trace_memory=False), execute(spec, trace_memory=False)
    for k in ("groups", "overall", "gaps", "policy_fit", "config_hash"):
        assert a[k] == b[k]


def test_common_random_numbers_pair_policies():
    """Within a seed, every policy sees the same evaluation population (same group counts)."""
    cell = gaussian_cell(0.5, 1.0)
    recs = [execute(RunSpec("X", cell, p, 2200, 1000), trace_memory=False) for p in ("P0", "P1", "P2", "P3")]
    for g in ("A", "B"):
        assert len({(r["groups"][g]["n"], r["groups"][g]["positives"]) for r in recs}) == 1


@pytest.mark.parametrize("mutate", [
    lambda d: d.pop("runs"),
    lambda d: d.update(label="final"),
    lambda d: d["runs"][0].update(run_id="bad id"),
    lambda d: d["runs"][0]["groups"]["A"].update(tpr=1.5),
    lambda d: d["runs"][0]["gaps"].update(eog="0.1"),
    lambda d: d["runs"][0].update(failure_reason="x"),
    lambda d: d["runs"][0].pop("groups"),
    lambda d: d.update(extra=1),
])
def test_schema_fails_closed(tiny_run, mutate):
    _, bundle, _ = tiny_run
    doc = copy.deepcopy(bundle)
    ok = next(i for i, r in enumerate(doc["runs"]) if r["status"] == "ok")
    doc["runs"][0], doc["runs"][ok] = doc["runs"][ok], doc["runs"][0]
    validate(doc, "rigged.result_bundle")
    mutate(doc)
    with pytest.raises(SchemaError):
        validate(doc, "rigged.result_bundle")


def test_load_rejects_malformed_json(tmp_path):
    p = tmp_path / "results.json"
    p.write_text("{not json")
    with pytest.raises(SchemaError):
        load(p, "rigged.result_bundle")
    with pytest.raises(SchemaError):
        load(tmp_path / "missing.json", "rigged.result_bundle")


def test_report_builds_tables_and_figure(tiny_run):
    out, _, _ = tiny_run
    res = build(out, analytic=False)
    text = Path(res["report"]).read_text()
    assert "EXPLORATORY" in text and "Not a finding" in text
    assert "PolicyFitError" in text
    assert (out / "tables" / "summary.csv").exists() and (out / "tables" / "contrasts.csv").exists()
    svg = Path(res["figures"][0]).read_text()
    assert svg.startswith("<svg") and "<title" in svg and "<desc" in svg


def test_confirmatory_matrix_needs_frozen_protocol(tmp_path):
    with pytest.raises(PermissionError):
        run_matrix(tiny_matrix("confirmatory"), tmp_path, None, "pytest")


def test_cli_run_refuses_unfrozen_protocol(capsys):
    assert not protocol_status("EXP-001").frozen
    assert cli.main(["run", "--experiment", "EXP-001"]) == cli.EXIT_REFUSED
    assert "REFUSED" in capsys.readouterr().err


def test_cli_exploratory_run_refuses_confirmatory_seeds(capsys):
    assert cli.main(["run", "--experiment", "EXP-001", "--exploratory", "--seed-offset", "5"]) == cli.EXIT_REFUSED


def test_cli_report_without_results(tmp_path):
    assert cli.main(["report", "--input", str(tmp_path)]) == 1


def _fake_repo(root: Path, proto_text: str, project_text: str, record_hash: bool, tamper: bool = False):
    (root / "research" / "experiments" / "EXP-009").mkdir(parents=True)
    proto = root / "research" / "experiments" / "EXP-009" / "protocol.md"
    proto.write_text(proto_text)
    (root / "research" / "protocol.md").write_text(project_text)
    h = hashlib.sha256(proto.read_bytes()).hexdigest() if record_hash else ""
    (root / "research" / "experiment_registry.csv").write_text(
        f"experiment_id,protocol_hash\nEXP-009,{'sha256:' + h if h else ''}\n")
    if tamper:
        proto.write_text(proto_text + "\nedited after freeze\n")


def test_protocol_guard_states(tmp_path):
    cases = [
        ("# P\nStatus: FROZEN v1.0\n", "# Project\nStatus: FROZEN\n", True, False, True),
        ("# P\nStatus: FROZEN v1.0\n", "# Project\nStatus: FROZEN\n", False, False, False),
        ("# P\nStatus: FROZEN v1.0\n", "# Project\nStatus: FROZEN\n", True, True, False),
        ("# P\nStatus: DRAFT v0.1\n", "# Project\nStatus: FROZEN\n", True, False, False),
        ("# P\nStatus: FROZEN v1.0\n", "# Project\nStatus: DRAFT\n", True, False, False),
    ]
    for i, (p, proj, rec, tamper, expected) in enumerate(cases):
        root = tmp_path / str(i)
        _fake_repo(root, p, proj, rec, tamper)
        assert protocol_status("EXP-009", root).frozen is expected, i
    assert protocol_status("EXP-404", tmp_path / "0").frozen is False
