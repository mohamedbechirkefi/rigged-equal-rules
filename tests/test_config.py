# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
import math

import pytest

from rigged.config import CellConfig, ConfigError, RunSpec, canonical_hash


@pytest.mark.parametrize("kw", [
    {"cell_id": ""}, {"family": "cauchy"}, {"s_a": 0.0}, {"s_b": -1.0}, {"sigma_a": -0.1}, {"kappa": 1.5},
    {"kappa": -0.1}, {"p_b": 1.01}, {"cost_ratio": -1}, {"mu_a": math.nan}, {"mu_b": math.inf},
    {"calibration_bins": 0}, {"ece_bins": 0}, {"kappa": True},
])
def test_invalid_cell_rejected(kw):
    args = {"cell_id": "c"} | kw
    with pytest.raises(ConfigError):
        CellConfig(**args)


@pytest.mark.parametrize("kw", [{"policy": "P9"}, {"seed": -1}, {"n": 0}, {"seed": 1.5}, {"n": True}])
def test_invalid_run_rejected(kw):
    args = {"experiment_id": "X", "cell": CellConfig(cell_id="c"), "policy": "P0", "seed": 0, "n": 10} | kw
    with pytest.raises(ConfigError):
        RunSpec(**args)


def test_run_id_and_hash_are_stable():
    spec = RunSpec("EXP-001", CellConfig(cell_id="d0.50-r1.00", mu_b=-0.5), "P0", 3, 100)
    assert spec.run_id == "RUN-EXP-001-d0.50-r1.00-P0-s3"
    h = spec.config_hash()
    assert h.startswith("sha256:") and len(h) == 71
    assert h == RunSpec("EXP-001", CellConfig(cell_id="d0.50-r1.00", mu_b=-0.5), "P0", 3, 100).config_hash()
    assert h != RunSpec("EXP-001", CellConfig(cell_id="d0.50-r1.00", mu_b=-0.5), "P0", 4, 100).config_hash()


def test_canonical_hash_rejects_nan():
    with pytest.raises(ValueError):
        canonical_hash({"x": math.nan})


def test_base_rates_exposed():
    c = CellConfig(cell_id="c", mu_b=-0.5)
    assert c.base_rate_a == pytest.approx(0.5)
    assert c.base_rate_b == pytest.approx(0.3085375387259869)
