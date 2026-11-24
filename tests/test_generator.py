# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
import numpy as np
import pytest

from rigged.config import CellConfig
from rigged.generator import STREAM_EVAL, STREAM_FIT, build_population, draw, populations


def test_draws_are_deterministic_and_streams_differ():
    a, b = draw(7, STREAM_FIT, 500), draw(7, STREAM_FIT, 500)
    for f in ("group_u", "z", "w3", "noise", "tie_u"):
        assert np.array_equal(getattr(a, f), getattr(b, f))
    e = draw(7, STREAM_EVAL, 500)
    assert not np.array_equal(a.z, e.z)
    assert not np.array_equal(a.z, draw(8, STREAM_FIT, 500).z)


def test_invalid_draw_arguments():
    with pytest.raises(ValueError):
        draw(0, STREAM_FIT, 0)
    with pytest.raises(ValueError):
        draw(-1, STREAM_FIT, 10)
    with pytest.raises(ValueError):
        draw(0, 5, 10)


def test_common_random_numbers_across_cells():
    d = draw(3, STREAM_FIT, 1000)
    p1 = build_population(CellConfig(cell_id="a", mu_b=0.0), d)
    p2 = build_population(CellConfig(cell_id="b", mu_b=-0.5, sigma_b=1.0), d)
    assert np.array_equal(p1.group_b, p2.group_b)
    # Group A is unchanged by group B parameters.
    assert np.array_equal(p1.x[~p1.group_b], p2.x[~p2.group_b])
    # Lowering mu_B shifts B's latent values by exactly delta.
    assert np.allclose(p1.q[p1.group_b] - 0.5, p2.q[p2.group_b])


def test_group_counts_and_labels():
    fit, ev = populations(CellConfig(cell_id="c", mu_b=-1.0, p_b=0.3), 0, 20_000)
    for pop in (fit, ev):
        n_b = int(pop.group_b.sum())
        assert n_b + int((~pop.group_b).sum()) == pop.n == 20_000
        assert n_b / pop.n == pytest.approx(0.3, abs=0.015)
        assert np.array_equal(pop.y, pop.q > 0)
        assert pop.y[pop.group_b].mean() == pytest.approx(0.1587, abs=0.02)


def test_noiseless_score_equals_latent():
    pop = build_population(CellConfig(cell_id="c", sigma_a=0.0, sigma_b=0.0), draw(1, STREAM_FIT, 100))
    assert np.array_equal(pop.x, pop.q)


def test_extreme_group_shares():
    d = draw(2, STREAM_FIT, 300)
    assert not build_population(CellConfig(cell_id="c", p_b=0.0), d).group_b.any()
    assert build_population(CellConfig(cell_id="c", p_b=1.0), d).group_b.all()
