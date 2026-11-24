# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Numerical helpers, checked against the standard library and closed forms."""

import math

import numpy as np
import pytest

from rigged import numerics as nm


def test_norm_cdf_matches_stdlib_erf():
    xs = np.linspace(-40, 40, 8001)
    ref = np.array([0.5 * math.erfc(-x / math.sqrt(2)) for x in xs])
    assert np.max(np.abs(nm.norm_cdf(xs) - ref)) < 1e-13


def test_norm_cdf_symmetry_and_bounds():
    xs = np.linspace(-10, 10, 1001)
    c = nm.norm_cdf(xs)
    assert np.all((c >= 0) & (c <= 1))
    assert np.allclose(c + nm.norm_cdf(-xs), 1.0, atol=1e-14)
    assert np.all(np.diff(c) >= 0)


def test_norm_ppf_round_trip_and_invalid():
    for p in (1e-6, 0.025, 0.3, 0.5, 0.975):
        assert float(nm.norm_cdf(nm.norm_ppf(p))) == pytest.approx(p, abs=1e-12)
    for bad in (0.0, 1.0, -0.1, 2.0):
        with pytest.raises(ValueError):
            nm.norm_ppf(bad)


@pytest.mark.parametrize("family", nm.FAMILIES)
def test_family_cdf_ppf_round_trip(family):
    for p in (0.01, 0.2, 0.5, 0.6914624612740131, 0.95):
        assert nm.family_cdf(family, nm.family_ppf(family, p)) == pytest.approx(p, abs=1e-10)


@pytest.mark.parametrize("family", nm.FAMILIES)
def test_family_pdf_is_standardised(family):
    lo, hi = nm.family_support(family)
    w = np.linspace(lo, hi, 400_001)
    f = nm.family_pdf(family, w)
    assert np.trapezoid(f, w) == pytest.approx(1.0, abs=1e-5)
    assert np.trapezoid(w * f, w) == pytest.approx(0.0, abs=1e-4)
    # The Student t3 variance converges slowly (tail mass beyond 200 is excluded).
    assert np.trapezoid(w * w * f, w) == pytest.approx(1.0, abs=2e-2 if family == "student_t3" else 1e-4)


@pytest.mark.parametrize("family", nm.FAMILIES)
def test_standardised_latent_draws_match_family(family):
    rng = np.random.default_rng(5)
    z = rng.standard_normal(200_000)
    w3 = rng.standard_normal((200_000, 3))
    w = nm.standardised_latent(family, z, w3)
    assert w.mean() == pytest.approx(0.0, abs=0.01)
    for q in (-1.0, 0.0, 0.7):
        assert np.mean(w <= q) == pytest.approx(nm.family_cdf(family, q), abs=0.004)


def test_matched_mean_gives_requested_base_rate():
    for fam in nm.FAMILIES:
        for s in (0.5, 1.0, 2.0):
            for pi in (0.1, 0.3085, 0.5):
                mu = nm.matched_mean(fam, s, pi)
                assert nm.base_rate(fam, mu, s) == pytest.approx(pi, abs=1e-10)
    assert nm.matched_mean("gaussian", 1.0, float(nm.norm_cdf(-0.5))) == pytest.approx(-0.5, abs=1e-12)


def test_unknown_family_rejected():
    with pytest.raises(ValueError):
        nm.family_cdf("cauchy", 0.0)
    with pytest.raises(ValueError):
        nm.standardised_latent("cauchy", np.zeros(2), np.zeros((2, 3)))


@pytest.mark.parametrize("df,expected", [(1, 12.7062047), (2, 4.30265273), (19, 2.09302405), (100, 1.98397152)])
def test_t_ppf_known_values(df, expected):
    assert nm.t_ppf(0.975, df) == pytest.approx(expected, abs=1e-5)
