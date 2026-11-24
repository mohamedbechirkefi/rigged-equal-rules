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


@pytest.mark.parametrize("cell", [gaussian_cell(0.5, 1.0), gaussian_cell(1.0, 2.0)], ids=lambda c: c.cell_id)
def test_p1_calibration_bins_match_analytic_posterior(cell):
    """Each fitted bin rate of P1 agrees with the mean analytic posterior of its members within 4 binomial SE."""
    from rigged.analytic import gaussian_posterior
    from rigged.generator import populations
    from rigged.policies import fit_calibration

    fit, _ = populations(cell, 5100, 20_000)
    for g, mask in (("A", ~fit.group_b), ("B", fit.group_b)):
        x, y = fit.x[mask], fit.y[mask]
        cal = fit_calibration(x, y, 20)
        idx = np.searchsorted(cal.inner_edges, x, side="right")
        post = gaussian_posterior(cell, g, x)
        for b in range(cal.bin_rate.shape[0]):
            members = idx == b
            p = post[members].mean()
            se = math.sqrt(max(p * (1 - p), 1e-4) / members.sum())
            assert abs(cal.bin_rate[b] - p) <= 4 * se + 1e-9, (g, b)


def test_gaussian_posterior_limits():
    from rigged.analytic import gaussian_posterior
    cell = gaussian_cell(0.5, 1.0)
    p = gaussian_posterior(cell, "B", np.array([-10.0, 0.0, 10.0]))
    assert p[0] < 1e-6 and p[2] > 1 - 1e-6 and 0 < p[1] < 1
    assert np.all(np.diff(gaussian_posterior(cell, "A", np.linspace(-3, 3, 50))) > 0)
