# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Seed-level uncertainty (protocol section 7): the seed is the independent unit."""

from __future__ import annotations

import math

import numpy as np

from .numerics import t_ppf

BOOTSTRAP_SEED = 20261124
BOOTSTRAP_RESAMPLES = 10_000


def summarise(values: list[float], resamples: int = BOOTSTRAP_RESAMPLES, seed: int = BOOTSTRAP_SEED) -> dict:
    """Mean, SD, percentile-bootstrap 95% interval over seeds, bootstrap SE and t-interval."""
    v = np.asarray([x for x in values if x is not None], dtype=np.float64)
    k = int(v.shape[0])
    out = {"n_seeds": k, "n_missing": len(values) - k, "mean": None, "sd": None, "boot_lo": None,
           "boot_hi": None, "boot_se": None, "t_lo": None, "t_hi": None, "standardised": None}
    if k == 0:
        return out
    mean = float(v.mean())
    out["mean"] = mean
    if k < 2:
        return out
    sd = float(v.std(ddof=1))
    out["sd"] = sd
    rng = np.random.Generator(np.random.PCG64(seed))
    idx = rng.integers(0, k, size=(resamples, k))
    means = v[idx].mean(axis=1)
    out["boot_lo"], out["boot_hi"] = (float(x) for x in np.percentile(means, [2.5, 97.5]))
    out["boot_se"] = float(means.std(ddof=1))
    half = t_ppf(0.975, k - 1) * sd / math.sqrt(k)
    out["t_lo"], out["t_hi"] = mean - half, mean + half
    out["standardised"] = mean / sd if sd > 0 else None
    return out
