# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Population (infinite-n) values for policy P0 by numerical integration (protocol section 7).

For group g: P(X > t, Y = 1) = integral over q > 0 of f_Q(q) * (1 - Phi((t - q) / sigma_g)) dq, with
Q = mu_g + s_g W. The population threshold t* solves (1 - p_B) P(X_A > t) + p_B P(X_B > t) = kappa.
This is an implementation check, not a hypothesis test.
"""

from __future__ import annotations

import numpy as np

from .config import CellConfig
from .numerics import family_pdf, family_support, norm_cdf

_GRID = 40_001


def _exceed(family: str, mu: float, s: float, sigma: float, t: float) -> tuple[float, float]:
    """Return (P(X > t, Y = 1), P(X > t, Y = 0)) for one group."""
    lo, hi = family_support(family)
    w0 = -mu / s  # Y = 1 iff W > w0
    out = []
    for a, b in ((max(w0, lo), hi), (lo, min(w0, hi))):
        if b <= a:
            out.append(0.0)
            continue
        w = np.linspace(a, b, _GRID)
        q = mu + s * w
        if sigma > 0:
            pass_prob = 1.0 - norm_cdf((t - q) / sigma)
        else:
            pass_prob = (q > t).astype(np.float64)
        f = family_pdf(family, w) * pass_prob
        out.append(float(np.trapezoid(f, w)))
    return out[0], out[1]


def _group_params(cell: CellConfig, g: str) -> tuple[float, float, float]:
    return (cell.mu_a, cell.s_a, cell.sigma_a) if g == "A" else (cell.mu_b, cell.s_b, cell.sigma_b)


def overall_rate(cell: CellConfig, t: float) -> float:
    tot = 0.0
    for g, share in (("A", 1.0 - cell.p_b), ("B", cell.p_b)):
        if share == 0:
            continue
        pos, neg = _exceed(cell.family, *_group_params(cell, g), t)
        tot += share * (pos + neg)
    return tot


def population_threshold(cell: CellConfig, iters: int = 80) -> float:
    if not 0.0 < cell.kappa < 1.0:
        raise ValueError("population threshold requires 0 < kappa < 1")
    lo, hi = -60.0, 60.0
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if overall_rate(cell, mid) > cell.kappa:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def p0_population_metrics(cell: CellConfig) -> dict:
    """Population SR, TPR, FPR, PPV per group and the gaps under P0 at the population threshold."""
    t = population_threshold(cell)
    out = {"threshold": t, "groups": {}}
    for g in ("A", "B"):
        mu, s, sigma = _group_params(cell, g)
        pos, neg = _exceed(cell.family, mu, s, sigma, t)
        br = cell.base_rate_a if g == "A" else cell.base_rate_b
        out["groups"][g] = {
            "base_rate": br,
            "sr": pos + neg,
            "tpr": pos / br if br > 0 else None,
            "fpr": neg / (1 - br) if br < 1 else None,
            "ppv": pos / (pos + neg) if pos + neg > 0 else None,
        }
    ga, gb = out["groups"]["A"], out["groups"]["B"]
    out["eog"] = ga["tpr"] - gb["tpr"]
    out["sr_gap"] = ga["sr"] - gb["sr"]
    out["fpr_gap"] = ga["fpr"] - gb["fpr"]
    out["ppv_gap"] = ga["ppv"] - gb["ppv"]
    return out
