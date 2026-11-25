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


def test_cli_run_refuses_unfrozen_protocol(capsys, monkeypatch, tmp_path):
    # Point the guard at an empty repository: nothing is frozen there. No run is started.
    real = cli.protocol_status
    monkeypatch.setattr(cli, "protocol_status", lambda e, **kw: real(e, root=tmp_path, **kw))
    assert cli.main(["run", "--experiment", "EXP-001", "--out", str(tmp_path / "out")]) == cli.EXIT_REFUSED
    assert "REFUSED" in capsys.readouterr().err
    assert not (tmp_path / "out").exists()


def test_repository_guard_on_the_frozen_configs():
    """The committed freeze record accepts the configs built by the current code and refuses a changed one.

    Reads records only; no run is executed. Skipped before the freeze record exists.
    """
    from dataclasses import replace

    from rigged.matrices import REGISTERED, matrix_config
    from rigged.protocol_guard import FREEZE_RECORD
    from rigged.environment import REPO_ROOT
    if not (REPO_ROOT / FREEZE_RECORD).exists():
        pytest.skip("no freeze record yet")
    for exp_id, build_matrix in REGISTERED.items():
        s = protocol_status(exp_id, expected_config=matrix_config(build_matrix()))
        assert s.frozen, (exp_id, s.reason)
        changed = replace(build_matrix(), seeds=tuple(range(21)))
        s = protocol_status(exp_id, expected_config=matrix_config(changed))
        assert not s.frozen and "current code" in s.reason


def test_cli_exploratory_run_refuses_confirmatory_seeds(capsys):
    assert cli.main(["run", "--experiment", "EXP-001", "--exploratory", "--seed-offset", "5"]) == cli.EXIT_REFUSED


def test_cli_report_without_results(tmp_path):
    assert cli.main(["report", "--input", str(tmp_path)]) == 1


def _fake_repo(root: Path, proto_text: str, project_text: str, record_hash: bool, tamper: bool = False,
               config: dict | None = None, with_record: bool = True, manifest: bool = False):
    exp = root / "research" / "experiments" / "EXP-009"
    exp.mkdir(parents=True)
    proto = exp / "protocol.md"
    proto.write_text(proto_text)
    (root / "research" / "protocol.md").write_text(project_text)
    cfg = exp / "config.json"
    cfg.write_text(json.dumps(config if config is not None else {"cells": ["c1"], "seeds": [0, 1]}))
    h = hashlib.sha256(proto.read_bytes()).hexdigest() if record_hash else ""
    (root / "research" / "experiment_registry.csv").write_text(
        f"experiment_id,protocol_hash\nEXP-009,{'sha256:' + h if h else ''}\n")
    entry = {"protocol_sha256": h, "config_path": "research/experiments/EXP-009/config.json",
             "config_sha256": hashlib.sha256(cfg.read_bytes()).hexdigest()}
    if manifest:
        (root / "data").mkdir()
        (root / "data" / "manifest.json").write_text('{"v": 1}')
        entry["data_manifest_sha256"] = hashlib.sha256(b'{"v": 1}').hexdigest()
    if with_record:
        (root / "research" / "freeze.json").write_text(json.dumps({
            "project_protocol": {"sha256": hashlib.sha256((root / "research" / "protocol.md").read_bytes()).hexdigest()},
            "experiments": {"EXP-009": entry}}))
    if tamper:
        proto.write_text(proto_text + "\nedited after freeze\n")
    return root


FROZEN_P = "# P\nStatus: FROZEN v1.0\n"
FROZEN_PROJ = "# Project\nStatus: FROZEN\n"


def test_protocol_guard_states(tmp_path):
    cases = [
        (FROZEN_P, FROZEN_PROJ, True, False, True),
        (FROZEN_P, FROZEN_PROJ, False, False, False),
        (FROZEN_P, FROZEN_PROJ, True, True, False),
        ("# P\nStatus: DRAFT v0.1\n", FROZEN_PROJ, True, False, False),
        (FROZEN_P, "# Project\nStatus: DRAFT\n", True, False, False),
    ]
    for i, (p, proj, rec, tamper, expected) in enumerate(cases):
        root = tmp_path / str(i)
        _fake_repo(root, p, proj, rec, tamper)
        assert protocol_status("EXP-009", root).frozen is expected, i
    assert protocol_status("EXP-404", tmp_path / "0").frozen is False


def test_guard_accepts_frozen_config_and_refuses_changed_ones(tmp_path):
    cfg = {"cells": ["c1"], "seeds": [0, 1]}
    ok = _fake_repo(tmp_path / "ok", FROZEN_P, FROZEN_PROJ, True, config=cfg, manifest=True)
    s = protocol_status("EXP-009", ok, expected_config=cfg)
    assert s.frozen, s.reason
    # Code builds a different matrix than the frozen config.
    s = protocol_status("EXP-009", ok, expected_config={"cells": ["c1"], "seeds": [0, 1, 2]})
    assert not s.frozen and "current code" in s.reason
    # Config file edited after the freeze.
    (ok / "research" / "experiments" / "EXP-009" / "config.json").write_text(json.dumps({"cells": ["c2"]}))
    s = protocol_status("EXP-009", ok)
    assert not s.frozen and "config file differs" in s.reason
    # Project protocol edited after the freeze (still not a draft).
    r2 = _fake_repo(tmp_path / "proj", FROZEN_P, FROZEN_PROJ, True, config=cfg)
    (r2 / "research" / "protocol.md").write_text(FROZEN_PROJ + "edit\n")
    assert "research/protocol.md differs" in protocol_status("EXP-009", r2).reason
    # Data manifest changed after the freeze.
    r3 = _fake_repo(tmp_path / "data", FROZEN_P, FROZEN_PROJ, True, config=cfg, manifest=True)
    (r3 / "data" / "manifest.json").write_text('{"v": 2}')
    assert "data/manifest.json differs" in protocol_status("EXP-009", r3).reason
    # No freeze record at all.
    r4 = _fake_repo(tmp_path / "norec", FROZEN_P, FROZEN_PROJ, True, config=cfg, with_record=False)
    assert "no freeze record" in protocol_status("EXP-009", r4).reason


def test_committed_configs_match_code():
    from rigged.matrices import REGISTERED, matrix_config
    for exp_id, build_matrix in REGISTERED.items():
        path = Path(__file__).resolve().parents[1] / "research" / "experiments" / exp_id / "config.json"
        assert json.loads(path.read_text()) == json.loads(json.dumps(matrix_config(build_matrix()))), exp_id


def test_matrix_sizes_and_seeds():
    from rigged.matrices import CONFIRMATORY_SEEDS, exp001, exp002, exp003, exp004, smoke
    assert len(exp001().runs()) == 240 and len(exp002().runs()) == 960
    assert len(exp003().runs()) == 15 * 20 + 6 * 20
    m4 = exp004()
    assert len(m4.runs()) == 160 and all(c.p3_tolerance == 30 for c in m4.cells)
    assert all(c.p3_tolerance == 10 for c in exp003().cells)
    assert not set(smoke().seeds) & set(CONFIRMATORY_SEEDS) and min(smoke().seeds) >= 1000
