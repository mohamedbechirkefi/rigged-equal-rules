# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""EXP-004 ingestion, score model and populations, on synthetic fixtures only (never real rows).

No test here runs an EXP-004 run on the real pool: that would compute real-data metrics before the
confirmatory run is scheduled.
"""

from pathlib import Path

import numpy as np
import pytest

from rigged.adult import (AdultSchemaError, AdultTable, fit_logistic, group_b_hours, parse_adult, real_populations,
                          score)
from rigged.config import CellConfig, ConfigError
from rigged.policies import PolicyFitError, fit_p3

FIXTURE = Path(__file__).parent / "fixtures" / "adult_synthetic.test"


def test_parse_fixture_counts():
    table, rep = parse_adult(FIXTURE.read_text())
    assert rep["rows_read"] == 8 and rep["rows_kept"] == table.n == 4
    assert rep["excluded"] == {"wrong_field_count": 1, "used_numeric_missing_or_invalid": 2, "invalid_label": 1}
    assert rep["excluded_total"] == 4
    miss = rep["missing_by_column"]
    assert (miss["workclass"], miss["occupation"], miss["native_country"], miss["age"], miss["hours_per_week"]) == (
        1, 1, 1, 1, 1)
    assert miss["sex"] == 0
    assert table.y.tolist() == [False, True, True, False]  # trailing "." removed, both label spellings
    assert table.age.tolist() == [30, 45, 52, 23]
    assert group_b_hours(table).tolist() == [False, False, True, True]  # hours below 40 is Group B


def test_parse_rejects_empty_input():
    with pytest.raises(AdultSchemaError):
        parse_adult("|only a comment\n\n")


def _synthetic_table(n=20_000, seed=7000):
    rng = np.random.default_rng(seed)
    age = rng.integers(17, 90, n).astype(float)
    edu = rng.integers(1, 17, n).astype(float)
    gain = np.where(rng.random(n) < 0.1, rng.integers(1, 99999, n), 0).astype(float)
    loss = np.where(rng.random(n) < 0.05, rng.integers(1, 4000, n), 0).astype(float)
    hours = rng.integers(1, 99, n).astype(float)
    t0 = AdultTable(age, edu, gain, loss, hours, np.zeros(n, dtype=bool))
    true = {"mean": [40.0, 9.0, 1.0, 0.4], "sd": [15.0, 3.0, 3.0, 1.5], "intercept": -1.0,
            "coefficients": [0.5, 0.9, 0.4, 0.2]}
    p = 1 / (1 + np.exp(-score(t0, true)))
    y = rng.random(n) < p
    return AdultTable(age, edu, gain, loss, hours, y), true


def test_fit_logistic_converges_and_recovers_direction():
    table, true = _synthetic_table()
    m = fit_logistic(table)
    assert m["converged"] and m["iterations"] < 20
    # Coefficients are on the fitted standardisation; compare per-raw-unit slopes.
    slopes = np.asarray(m["coefficients"]) / np.asarray(m["sd"])
    true_slopes = np.asarray(true["coefficients"]) / np.asarray(true["sd"])
    assert np.allclose(slopes, true_slopes, rtol=0.25, atol=0.02)
    assert fit_logistic(table) == m  # deterministic


def test_score_is_linear_predictor():
    table, _ = parse_adult(FIXTURE.read_text())
    m = {"mean": [0.0] * 4, "sd": [1.0] * 4, "intercept": 0.5, "coefficients": [1.0, 0.0, 0.0, 0.0]}
    assert score(table, m).tolist() == [30.5, 45.5, 52.5, 23.5]


def test_real_populations_split_and_common_draws():
    n = 1001
    rng = np.random.default_rng(7100)
    x, y, g = rng.normal(size=n), rng.random(n) < 0.3, rng.random(n) < 0.4
    fh, eh = real_populations(x, y, g, 3, "hours")
    fr, er = real_populations(x, y, g, 3, "random")
    assert fh.n == 500 and eh.n == 501
    # Disjoint halves covering the pool.
    assert sorted(np.concatenate([fh.x, eh.x]).tolist()) == sorted(x.tolist())
    # Same split and tie uniforms in both cells (common random numbers); only the labels differ.
    assert np.array_equal(fh.x, fr.x) and np.array_equal(fh.tie_u, fr.tie_u) and np.array_equal(eh.y, er.y)
    assert int(fr.group_b.sum() + er.group_b.sum()) == int(g.sum())  # same group sizes
    assert not np.array_equal(fh.group_b, fr.group_b)
    a, _ = real_populations(x, y, g, 3, "hours")
    assert np.array_equal(a.x, fh.x)  # deterministic
    b, _ = real_populations(x, y, g, 4, "hours")
    assert not np.array_equal(b.x, fh.x)
    with pytest.raises(ValueError):
        real_populations(x, y, g, 3, "other")


def test_data_source_validated():
    with pytest.raises(ConfigError):
        CellConfig(cell_id="x", data_source="ADULT-R1:sex")
    with pytest.raises(ConfigError):
        CellConfig(cell_id="x", p3_tolerance=-1)
    c = CellConfig(cell_id="R-hours", data_source="ADULT-R1:hours")
    assert c.is_real and "base_rate_a" not in c.to_dict()
    assert "data_source" not in CellConfig(cell_id="s").to_dict()


def test_p3_capacity_tolerance(make_pop):
    # Heavily tied scores: P3 cannot hit the target count exactly.
    x = np.repeat(np.arange(10, dtype=float), 20)
    y = np.tile([True, False], 100)
    g = np.tile([True, True, False, False], 50)
    pop = make_pop(x, y, g, tie_u=np.linspace(0.001, 0.999, 200))
    loose = fit_p3(pop, CellConfig(cell_id="t", kappa=0.33, p3_tolerance=50))
    dev = abs(loose.diagnostics["fit_selected"] - loose.diagnostics["fit_target"])
    assert dev > 0 and loose.diagnostics["fit_tolerance"] == 50
    with pytest.raises(PolicyFitError, match="capacity tolerance"):
        fit_p3(pop, CellConfig(cell_id="t", kappa=0.33, p3_tolerance=dev - 1))
