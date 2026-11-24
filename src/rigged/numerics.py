# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Numerical helpers without SciPy: normal CDF, quantiles, latent-family distributions, Student t.

Every function is pure and deterministic. The vectorised normal CDF uses Hart's (1968) double
precision rational approximation as given by West (2005); the tests compare it with the standard
library's ``math.erf``.
"""

from __future__ import annotations

import math
from statistics import NormalDist

import numpy as np
from numpy.typing import ArrayLike, NDArray

FAMILIES = ("gaussian", "student_t3", "lognormal")
LOGNORMAL_SIGMA = 0.5
_STD_NORMAL = NormalDist()


def norm_cdf(x: ArrayLike) -> NDArray[np.float64]:
    """Standard normal CDF, vectorised, absolute error below about 1e-14."""
    x = np.asarray(x, dtype=np.float64)
    a = np.abs(x)
    expo = np.exp(-0.5 * a * a)
    small = a < 7.07106781186547
    num = 3.52624965998911e-02 * a + 0.700383064443688
    for c in (6.37396220353165, 33.912866078383, 112.079291497871, 221.213596169931, 220.206867912376):
        num = num * a + c
    den = 8.83883476483184e-02 * a + 1.75566716318264
    for c in (16.064177579207, 86.7807322029461, 296.564248779674, 637.333633378831, 793.826512519948,
              440.413735824752):
        den = den * a + c
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        tail_small = expo * num / den
        b = a + 0.65
        b = a + 4.0 / b
        b = a + 3.0 / b
        b = a + 2.0 / b
        b = a + 1.0 / b
        tail_large = expo / b / 2.506628274631
    tail = np.where(small, tail_small, tail_large)
    tail = np.where(a > 37.0, 0.0, tail)
    out = np.where(x > 0, 1.0 - tail, tail)
    return out


def norm_ppf(p: float) -> float:
    """Standard normal quantile (scalar)."""
    if not 0.0 < p < 1.0:
        raise ValueError(f"norm_ppf requires 0 < p < 1, got {p!r}")
    return _STD_NORMAL.inv_cdf(p)


def _bisect(f, lo: float, hi: float, target: float, iters: int = 200) -> float:
    """Find x in [lo, hi] with f(x) = target for nondecreasing f."""
    if not f(lo) <= target <= f(hi):
        raise ValueError("target outside bracket")
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if f(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# --- Standardised latent families W (mean 0, variance 1) -------------------------------------------

def _lognormal_moments(sigma: float = LOGNORMAL_SIGMA) -> tuple[float, float]:
    m = math.exp(sigma * sigma / 2.0)
    sd = math.sqrt((math.exp(sigma * sigma) - 1.0) * math.exp(sigma * sigma))
    return m, sd


def family_cdf(family: str, w: float) -> float:
    """CDF of the standardised latent variable W of the given family (scalar)."""
    if family == "gaussian":
        return _STD_NORMAL.cdf(w)
    if family == "student_t3":
        # W = T / sqrt(3), T ~ Student t with 3 degrees of freedom.
        return 0.5 + (w / (1.0 + w * w) + math.atan(w)) / math.pi
    if family == "lognormal":
        m, sd = _lognormal_moments()
        level = m + sd * w
        if level <= 0.0:
            return 0.0
        return _STD_NORMAL.cdf(math.log(level) / LOGNORMAL_SIGMA)
    raise ValueError(f"unknown family {family!r}; expected one of {FAMILIES}")


def family_ppf(family: str, p: float) -> float:
    """Quantile of the standardised latent variable W (scalar)."""
    if not 0.0 < p < 1.0:
        raise ValueError(f"family_ppf requires 0 < p < 1, got {p!r}")
    if family == "gaussian":
        return norm_ppf(p)
    if family == "lognormal":
        m, sd = _lognormal_moments()
        return (math.exp(LOGNORMAL_SIGMA * norm_ppf(p)) - m) / sd
    if family == "student_t3":
        return _bisect(lambda w: family_cdf("student_t3", w), -1e6, 1e6, p)
    raise ValueError(f"unknown family {family!r}; expected one of {FAMILIES}")


def family_pdf(family: str, w: NDArray[np.float64]) -> NDArray[np.float64]:
    """Density of the standardised latent variable W (vectorised)."""
    w = np.asarray(w, dtype=np.float64)
    if family == "gaussian":
        return np.exp(-0.5 * w * w) / math.sqrt(2.0 * math.pi)
    if family == "student_t3":
        return 2.0 / (math.pi * (1.0 + w * w) ** 2)
    if family == "lognormal":
        m, sd = _lognormal_moments()
        level = m + sd * w
        out = np.zeros_like(w)
        pos = level > 0
        lv = level[pos]
        z = np.log(lv) / LOGNORMAL_SIGMA
        out[pos] = sd * np.exp(-0.5 * z * z) / (math.sqrt(2.0 * math.pi) * LOGNORMAL_SIGMA * lv)
        return out
    raise ValueError(f"unknown family {family!r}; expected one of {FAMILIES}")


def family_support(family: str) -> tuple[float, float]:
    """Integration range for W; the truncated mass is below 1e-6 for every family."""
    if family == "gaussian":
        return -12.0, 12.0
    if family == "student_t3":
        return -200.0, 200.0
    if family == "lognormal":
        m, sd = _lognormal_moments()
        return -m / sd, (math.exp(LOGNORMAL_SIGMA * 9.0) - m) / sd
    raise ValueError(f"unknown family {family!r}; expected one of {FAMILIES}")


def standardised_latent(family: str, z: NDArray[np.float64], w3: NDArray[np.float64]) -> NDArray[np.float64]:
    """Map common random numbers to a standardised latent draw W of the family.

    ``z`` has shape (n,), ``w3`` shape (n, 3); both are standard normal. Every family consumes the
    same draws so that cells differing only in family remain paired within a seed.
    """
    if family == "gaussian":
        return z.copy()
    if family == "student_t3":
        chi2 = np.sum(w3 * w3, axis=1)
        t = z / np.sqrt(chi2 / 3.0)
        return t / math.sqrt(3.0)
    if family == "lognormal":
        m, sd = _lognormal_moments()
        return (np.exp(LOGNORMAL_SIGMA * z) - m) / sd
    raise ValueError(f"unknown family {family!r}; expected one of {FAMILIES}")


def matched_mean(family: str, s: float, base_rate: float) -> float:
    """Latent mean mu such that P(mu + s * W > 0) = base_rate."""
    if s <= 0:
        raise ValueError("latent dispersion s must be positive")
    return -s * family_ppf(family, 1.0 - base_rate)


def base_rate(family: str, mu: float, s: float) -> float:
    """P(mu + s * W > 0)."""
    return 1.0 - family_cdf(family, -mu / s)


# --- Student t quantile for the t-interval ------------------------------------------------------

def t_cdf(x: float, df: int) -> float:
    """Student t CDF by numerical integration of the density (Simpson rule)."""
    if df < 1:
        raise ValueError("df must be at least 1")
    if x == 0.0:
        return 0.5
    logc = math.lgamma((df + 1) / 2.0) - math.lgamma(df / 2.0) - 0.5 * math.log(df * math.pi)
    a = abs(x)
    grid = np.linspace(0.0, a, 20001)
    dens = np.exp(logc - (df + 1) / 2.0 * np.log1p(grid * grid / df))
    h = grid[1] - grid[0]
    integral = h / 3.0 * (dens[0] + dens[-1] + 4.0 * dens[1:-1:2].sum() + 2.0 * dens[2:-1:2].sum())
    return 0.5 + integral if x > 0 else 0.5 - integral


def t_ppf(p: float, df: int) -> float:
    if not 0.5 <= p < 1.0:
        raise ValueError("t_ppf implemented for 0.5 <= p < 1")
    return _bisect(lambda v: t_cdf(v, df), 0.0, 1000.0, p, iters=80)
