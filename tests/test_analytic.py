# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Differential tests: the analytic P0 values against closed forms and against the simulation."""

import math

import numpy as np
import pytest

from rigged.analytic import overall_rate, p0_population_metrics, population_threshold
from rigged.config import RunSpec
from rigged.matrices import exp003_cells, gaussian_cell
from rigged.numerics import norm_cdf
from rigged.runner import execute


def test_selection_rate_matches_gaussian_closed_form():
    cell = gaussian_cell(0.5, 2.0)
    for t in (-1.0, 0.0, 0.35, 1.5):
        closed = 0.5 * (1 - norm_cdf((t - 0.0) / math.sqrt(1 + 0.25))) + \
            0.5 * (1 - norm_cdf((t + 0.5) / math.sqrt(1 + 1.0)))
        assert overall_rate(cell, t) == pytest.approx(float(closed), abs=1e-8)


def test_population_threshold_hits_capacity():
    cell = gaussian_cell(1.0, 1.5)
    assert overall_rate(cell, population_threshold(cell)) == pytest.approx(0.30, abs=1e-9)


def test_equal_groups_have_zero_population_gaps():
    m = p0_population_metrics(gaussian_cell(0.0, 1.0))
    for k in ("eog", "sr_gap", "fpr_gap", "ppv_gap"):
        assert abs(m[k]) < 1e-9


def test_population_eog_increases_with_delta_at_rho_1():
    """The sign predicted by the mechanism in research/protocol.md section 4 (implementation check)."""
    vals = [p0_population_metrics(gaussian_cell(d, 1.0))["eog"] for d in (0.0, 0.25, 0.5, 1.0)]
    assert all(b > a for a, b in zip(vals, vals[1:]))


def test_population_threshold_rejects_degenerate_capacity():
    with pytest.raises(ValueError):
        population_threshold(gaussian_cell(0.5, 1.0, kappa=0.0))


@pytest.mark.parametrize("cell", [gaussian_cell(0.5, 1.0), gaussian_cell(1.0, 2.0)]
                         + [c for c, _ in exp003_cells() if c.cell_id in ("C-student_t3", "C-lognormal")],
                         ids=lambda c: c.cell_id)
def test_simulation_agrees_with_population_values(cell):
    """Large-n P0 simulation over 5 seeds (seeds 5000+, not confirmatory) within 4 binomial SE."""
    pop = p0_population_metrics(cell)
    eogs = [execute(RunSpec("TEST", cell, "P0", 5000 + s, 100_000), trace_memory=False)["gaps"]["eog"]
            for s in range(5)]
    se = 1.2 * math.sqrt(0.25 / 25_000 + 0.25 / 15_000) / math.sqrt(5)
    assert np.mean(eogs) == pytest.approx(pop["eog"], abs=4 * se)
