# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Policies P0 to P3: golden examples, exact capacity, monotonicity, error paths."""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from rigged.config import CellConfig
from rigged.generator import populations
from rigged.policies import (PolicyFitError, Threshold, capacity_count, fit_calibration, fit_policy,
                             fit_threshold)


def naive_threshold_select(scores, tie_u, k):
    """Reference: rank by (score desc, tie uniform asc) and take the first k."""
    order = sorted(range(len(scores)), key=lambda i: (-scores[i], tie_u[i]))
    sel = [False] * len(scores)
    for i in order[:k]:
        sel[i] = True
    return sel


def test_fit_threshold_golden_with_ties():
    scores = np.array([5.0, 4.0, 4.0, 4.0, 3.0, 1.0])
    tie_u = np.array([0.9, 0.1, 0.6, 0.3, 0.5, 0.2])
    th = fit_threshold(scores, tie_u, 3)
    assert th == Threshold(4.0, pytest.approx(0.45))
    assert th.select(scores, tie_u).tolist() == [True, True, False, True, False, False]


def test_fit_threshold_extremes():
    s, u = np.array([2.0, 1.0, 1.0]), np.array([0.2, 0.4, 0.6])
    assert not fit_threshold(s, u, 0).select(s, u).any()
    assert not fit_threshold(s, u, 0).select(np.array([1e9]), np.array([0.0])).any()
    assert fit_threshold(s, u, 3).select(s, u).all()
    with pytest.raises(ValueError):
        fit_threshold(s, u, 4)
    with pytest.raises(PolicyFitError):
        fit_threshold(np.empty(0), np.empty(0), 0)


@settings(max_examples=200, deadline=None)
@given(st.lists(st.integers(0, 6), min_size=1, max_size=40), st.data())
def test_fit_threshold_selects_exactly_k_and_matches_reference(raw, data):
    scores = np.array(raw, dtype=np.float64)  # small integer range forces ties
    n = scores.shape[0]
    tie_u = np.array(data.draw(st.lists(st.floats(0, 1, exclude_max=True), min_size=n, max_size=n, unique=True)))
    k = data.draw(st.integers(0, n))
    sel = fit_threshold(scores, tie_u, k).select(scores, tie_u)
    assert int(sel.sum()) == k
    assert sel.tolist() == naive_threshold_select(scores.tolist(), tie_u.tolist(), k)


@settings(max_examples=100, deadline=None)
@given(st.lists(st.floats(-5, 5), min_size=2, max_size=60, unique=True), st.data())
def test_threshold_monotonicity_in_capacity(raw, data):
    """Raising the capacity never removes anyone (nested selections) and never raises the threshold."""
    scores = np.array(raw)
    tie_u = np.linspace(0.01, 0.99, scores.shape[0])
    k1 = data.draw(st.integers(0, scores.shape[0]))
    k2 = data.draw(st.integers(k1, scores.shape[0]))
    t1, t2 = fit_threshold(scores, tie_u, k1), fit_threshold(scores, tie_u, k2)
    s1, s2 = t1.select(scores, tie_u), t2.select(scores, tie_u)
    assert np.all(s2[s1])
    assert t2.t <= t1.t


def test_capacity_count():
    assert capacity_count(0.3, 2000) == 600
    assert capacity_count(0.0, 10) == 0
    assert capacity_count(1.0, 10) == 10


def test_calibration_golden():
    cal = fit_calibration(np.array([1.0, 2.0, 3.0, 4.0]), np.array([0, 0, 1, 1], dtype=bool), 2)
    assert cal.inner_edges.tolist() == [2.5]
    assert cal(np.array([0.0, 2.4, 2.5, 9.0])).tolist() == [0.0, 0.0, 1.0, 1.0]
    assert cal.bin_count.tolist() == [2, 2]


CELL = CellConfig(cell_id="c", mu_b=-0.5)


@pytest.fixture(scope="module")
def fit_pop():
    return populations(CELL, 11, 5000)[0]


def test_p0_common_threshold_exact_capacity(fit_pop):
    fp = fit_policy("P0", fit_pop, CELL)
    assert fp.thresholds["A"] == fp.thresholds["B"]
    assert int(fp.select(fit_pop).sum()) == capacity_count(0.3, 5000)


def test_p1_common_threshold_on_calibrated_scores(fit_pop):
    fp = fit_policy("P1", fit_pop, CELL)
    s = fp.scores(fit_pop)
    assert np.all((s >= 0) & (s <= 1))
    assert int(fp.select(fit_pop).sum()) == capacity_count(0.3, 5000)
    assert fp.to_dict()["calibration_min_bin_count"]["B"] > 0


def test_p2_group_rates_equal_kappa(fit_pop):
    fp = fit_policy("P2", fit_pop, CELL)
    sel = fp.select(fit_pop)
    for mask in (~fit_pop.group_b, fit_pop.group_b):
        assert int(sel[mask].sum()) == capacity_count(0.3, int(mask.sum()))


def test_p3_equal_tpr_on_fitting_population(fit_pop):
    fp = fit_policy("P3", fit_pop, CELL)
    d = fp.diagnostics
    n_pos_b = int((fit_pop.y & fit_pop.group_b).sum())
    assert abs(d["fit_tpr_gap"]) <= 2.0 / n_pos_b
    assert abs(d["fit_selected"] - d["fit_target"]) <= 5
    sel = fp.select(fit_pop)
    tpr = [sel[m & fit_pop.y].mean() for m in (~fit_pop.group_b, fit_pop.group_b)]
    assert tpr[0] - tpr[1] == pytest.approx(d["fit_tpr_gap"])


def test_policies_fail_explicitly_on_empty_group(make_pop):
    pop = make_pop([0.1, 0.5, 0.9], [0, 1, 1], [False, False, False])
    cell = CellConfig(cell_id="c")
    assert fit_policy("P0", pop, cell).select(pop).sum() == 1  # P0 does not need groups
    for pol in ("P1", "P2", "P3"):
        with pytest.raises(PolicyFitError, match="group B is empty"):
            fit_policy(pol, pop, cell)


def test_p3_fails_without_qualified_members(make_pop):
    pop = make_pop([0.1, 0.5, 0.9, 0.3], [0, 1, 0, 0], [False, False, True, True])
    with pytest.raises(PolicyFitError, match="no qualified member"):
        fit_policy("P3", pop, CellConfig(cell_id="c"))


def test_unknown_policy():
    with pytest.raises(ValueError):
        fit_policy("P7", None, CELL)


def test_policy_export_is_json_safe(make_pop):
    import json
    pop = make_pop([0.1, 0.5, 0.9, 0.3], [0, 1, 1, 1], [False, False, True, True])
    fp = fit_policy("P0", pop, CellConfig(cell_id="c", kappa=0.0))
    d = fp.to_dict()
    assert d["thresholds"]["A"]["selects_none"] is True and d["thresholds"]["A"]["t"] is None
    json.dumps(d, allow_nan=False)
