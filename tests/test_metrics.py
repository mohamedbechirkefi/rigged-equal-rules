# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Confusion matrices, group counts, zero denominators and threshold monotonicity (master prompt
section 10, project-specific verification), plus hand-computed golden values."""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from rigged.metrics import confusion, evaluate, expected_calibration_error

Y = np.array([1, 1, 1, 0, 0, 0, 1, 0], dtype=bool)
SEL = np.array([1, 0, 1, 1, 0, 0, 0, 0], dtype=bool)
GB = np.array([0, 0, 0, 0, 1, 1, 1, 1], dtype=bool)
CAL = np.array([0.9, 0.9, 0.1, 0.1, 0.5, 0.5, 0.5, 0.5])


def test_golden_confusion_matrices_and_rates():
    m = evaluate(Y, GB, SEL, CAL, cost_ratio=1.0, ece_bins=10)
    a, b = m["groups"]["A"], m["groups"]["B"]
    assert (a["tp"], a["fp"], a["tn"], a["fn"]) == (2, 1, 0, 1)
    assert (b["tp"], b["fp"], b["tn"], b["fn"]) == (0, 0, 3, 1)
    assert a["sr"] == 0.75 and a["tpr"] == pytest.approx(2 / 3) and a["fpr"] == 1.0 and a["ppv"] == pytest.approx(2 / 3)
    assert a["fnr"] == pytest.approx(1 / 3)
    assert b["sr"] == 0.0 and b["tpr"] == 0.0 and b["fpr"] == 0.0
    assert m["gaps"]["eog"] == pytest.approx(2 / 3)
    assert m["gaps"]["sr_gap"] == 0.75
    o = m["overall"]
    assert (o["tp"], o["fp"], o["tn"], o["fn"]) == (2, 1, 3, 2)
    assert o["utility_per_capita"] == pytest.approx(0.125)
    assert o["accuracy"] == pytest.approx(5 / 8)
    assert a["ece"] == pytest.approx(0.25) and b["ece"] == pytest.approx(0.25)


def test_zero_denominators_are_null_with_reason():
    m = evaluate(Y, GB, SEL, CAL, cost_ratio=1.0, ece_bins=10)
    assert m["groups"]["B"]["ppv"] is None
    assert m["undefined"]["B.ppv"] == "zero denominator (ppv)"
    assert m["gaps"]["ppv_gap"] is None
    assert "ppv_gap" in m["undefined"]


def test_empty_group_and_no_positives():
    y = np.array([0, 0, 1], dtype=bool)
    gb = np.array([0, 0, 0], dtype=bool)  # group B empty
    m = evaluate(y, gb, np.array([1, 0, 0], dtype=bool), np.array([0.2, 0.2, 0.2]), 1.0, 10)
    b = m["groups"]["B"]
    assert b["n"] == 0 and b["sr"] is None and b["tpr"] is None and b["fnr"] is None and b["ece"] is None
    assert all(m["gaps"][k] is None for k in m["gaps"])
    y2 = np.zeros(4, dtype=bool)
    m2 = evaluate(y2, np.array([0, 0, 1, 1], dtype=bool), np.zeros(4, dtype=bool), np.zeros(4), 1.0, 10)
    assert m2["groups"]["A"]["tpr"] is None and m2["undefined"]["A.tpr"].startswith("zero denominator")
    assert m2["groups"]["A"]["ppv"] is None


def test_confusion_shape_mismatch():
    with pytest.raises(ValueError):
        confusion(np.zeros(3, dtype=bool), np.zeros(4, dtype=bool))


def test_ece_rejects_out_of_range_and_handles_empty():
    assert expected_calibration_error(np.zeros(0, dtype=bool), np.zeros(0), 10) is None
    with pytest.raises(ValueError):
        expected_calibration_error(np.array([True]), np.array([1.2]), 10)
    assert expected_calibration_error(np.array([True, False]), np.array([1.0, 0.0]), 10) == 0.0


def naive_confusion(y, sel):
    tp = fp = tn = fn = 0
    for yi, si in zip(y, sel):
        if yi and si:
            tp += 1
        elif not yi and si:
            fp += 1
        elif yi:
            fn += 1
        else:
            tn += 1
    return tp, fp, tn, fn


@settings(max_examples=200, deadline=None)
@given(st.lists(st.tuples(st.booleans(), st.booleans(), st.booleans()), min_size=0, max_size=50))
def test_confusion_invariants_and_differential(rows):
    y = np.array([r[0] for r in rows], dtype=bool)
    sel = np.array([r[1] for r in rows], dtype=bool)
    gb = np.array([r[2] for r in rows], dtype=bool)
    if y.size == 0:
        return
    m = evaluate(y, gb, sel, np.full(y.shape, 0.5), 1.0, 10)
    total = 0
    for g, mask in (("A", ~gb), ("B", gb)):
        gm = m["groups"][g]
        assert (gm["tp"], gm["fp"], gm["tn"], gm["fn"]) == naive_confusion(y[mask], sel[mask])
        assert gm["tp"] + gm["fp"] + gm["tn"] + gm["fn"] == gm["n"] == int(mask.sum())
        assert gm["positives"] == int(y[mask].sum()) and gm["selected"] == int(sel[mask].sum())
        for k in ("sr", "tpr", "fnr", "fpr", "ppv", "ece"):
            assert gm[k] is None or 0.0 <= gm[k] <= 1.0
        total += gm["n"]
    assert total == y.size == m["overall"]["n"]
    for name, v in m["gaps"].items():
        assert (v is None) == (name in m["undefined"])


@settings(max_examples=100, deadline=None)
@given(st.lists(st.tuples(st.floats(-3, 3), st.booleans()), min_size=1, max_size=60),
       st.floats(-3, 3), st.floats(0, 2))
def test_threshold_monotonicity_of_rates(rows, t, dt):
    """Raising a threshold never increases SR, TPR or FPR in either group."""
    x = np.array([r[0] for r in rows])
    y = np.array([r[1] for r in rows], dtype=bool)
    gb = np.arange(x.size) % 2 == 1
    lo = evaluate(y, gb, x > t, np.full(x.shape, 0.5), 1.0, 10)
    hi = evaluate(y, gb, x > t + dt, np.full(x.shape, 0.5), 1.0, 10)
    for g in ("A", "B"):
        for k in ("sr", "tpr", "fpr"):
            a, b = lo["groups"][g][k], hi["groups"][g][k]
            assert (a is None) == (b is None)
            if a is not None:
                assert b <= a
