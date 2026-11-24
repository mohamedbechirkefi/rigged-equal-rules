# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Decision rules P0 to P3. Every rule is fitted on the fitting population only and then applied,
unchanged, to the evaluation population.

A threshold is a pair (t, gamma): an individual with score s and tie uniform u is selected when
s > t, or s == t and u < gamma. On the fitting population, gamma makes the number selected equal the
target exactly (seeded tie-breaking, protocol section 3).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from .config import CellConfig
from .generator import Population


class PolicyFitError(RuntimeError):
    """A policy cannot be fitted (for example a group is empty or has no qualified member)."""


@dataclass(frozen=True)
class Threshold:
    t: float
    gamma: float

    def select(self, scores: NDArray[np.float64], tie_u: NDArray[np.float64]) -> NDArray[np.bool_]:
        return (scores > self.t) | ((scores == self.t) & (tie_u < self.gamma))


def fit_threshold(scores: NDArray[np.float64], tie_u: NDArray[np.float64], k: int) -> Threshold:
    """Randomised threshold that selects exactly k of the given scores."""
    n = scores.shape[0]
    if n == 0:
        raise PolicyFitError("cannot fit a threshold on an empty set")
    if not 0 <= k <= n:
        raise ValueError(f"k must lie in [0, {n}], got {k}")
    order = np.sort(scores)[::-1]
    if k == 0:
        return Threshold(float(np.inf), 0.0)  # selects nobody, on any population
    v = order[k - 1]
    above = int(np.count_nonzero(scores > v))
    tied = np.sort(tie_u[scores == v])
    m = k - above  # number of tied individuals to select, 1 <= m <= len(tied)
    if m == tied.shape[0]:
        gamma = 1.0
    else:
        gamma = float(0.5 * (tied[m - 1] + tied[m]))
        if not tied[m - 1] < gamma <= tied[m]:  # identical tie uniforms: probability zero
            raise PolicyFitError("tie uniforms collide; cannot break ties exactly")
    return Threshold(float(v), gamma)


def capacity_count(kappa: float, n: int) -> int:
    """Number selected at capacity kappa: round half to even of kappa * n."""
    return int(round(kappa * n))


@dataclass(frozen=True)
class CalibrationMap:
    """Quantile-bin calibration map r(x) ~ P(Y = 1 | X = x), fitted on one set of (x, y)."""

    inner_edges: NDArray[np.float64]
    bin_rate: NDArray[np.float64]
    bin_count: NDArray[np.int64]

    def __call__(self, x: NDArray[np.float64]) -> NDArray[np.float64]:
        return self.bin_rate[np.searchsorted(self.inner_edges, x, side="right")]


def fit_calibration(x: NDArray[np.float64], y: NDArray[np.bool_], bins: int) -> CalibrationMap:
    if x.shape[0] == 0:
        raise PolicyFitError("cannot fit a calibration map on an empty set")
    qs = np.arange(1, bins) / bins
    inner = np.unique(np.quantile(x, qs)) if bins > 1 else np.empty(0)
    idx = np.searchsorted(inner, x, side="right")
    nb = inner.shape[0] + 1
    count = np.bincount(idx, minlength=nb).astype(np.int64)
    pos = np.bincount(idx, weights=y.astype(np.float64), minlength=nb)
    fallback = float(y.mean())
    with np.errstate(divide="ignore", invalid="ignore"):
        rate = np.where(count > 0, pos / np.maximum(count, 1), fallback)
    return CalibrationMap(inner_edges=inner, bin_rate=rate, bin_count=count)


@dataclass
class FittedPolicy:
    """A fitted policy: per-group score transform and threshold, plus fitting diagnostics."""

    policy: str
    thresholds: dict[str, Threshold]
    calibration: dict[str, CalibrationMap] | None = None
    diagnostics: dict = field(default_factory=dict)

    def scores(self, pop: Population) -> NDArray[np.float64]:
        if self.calibration is None:
            return pop.x
        s = np.empty_like(pop.x)
        for g, mask in (("A", ~pop.group_b), ("B", pop.group_b)):
            if np.any(mask):
                s[mask] = self.calibration[g](pop.x[mask])
        return s

    def select(self, pop: Population) -> NDArray[np.bool_]:
        s = self.scores(pop)
        out = np.zeros(pop.n, dtype=bool)
        for g, mask in (("A", ~pop.group_b), ("B", pop.group_b)):
            out[mask] = self.thresholds[g].select(s[mask], pop.tie_u[mask])
        return out

    def to_dict(self) -> dict:
        d = {
            "policy": self.policy,
            "thresholds": {g: {"t": (None if np.isinf(th.t) else th.t), "gamma": th.gamma,
                               "selects_none": bool(np.isinf(th.t))} for g, th in self.thresholds.items()},
            "diagnostics": self.diagnostics,
        }
        if self.calibration is not None:
            d["calibration_min_bin_count"] = {g: int(c.bin_count.min()) for g, c in self.calibration.items()}
        return d


def _require_groups(pop: Population, policy: str, need_positive: bool = False) -> None:
    for g, mask in (("A", ~pop.group_b), ("B", pop.group_b)):
        if not np.any(mask):
            raise PolicyFitError(f"{policy}: group {g} is empty in the fitting population")
        if need_positive and not np.any(pop.y[mask]):
            raise PolicyFitError(f"{policy}: group {g} has no qualified member in the fitting population")


def fit_p0(fit: Population, cell: CellConfig) -> FittedPolicy:
    """P0, baseline: one common threshold on the raw score, overall rate kappa."""
    th = fit_threshold(fit.x, fit.tie_u, capacity_count(cell.kappa, fit.n))
    return FittedPolicy("P0", {"A": th, "B": th})


def fit_p1(fit: Population, cell: CellConfig) -> FittedPolicy:
    """P1: within-group calibration maps (quantile bins), one common threshold on the calibrated score."""
    _require_groups(fit, "P1")
    cal = {}
    for g, mask in (("A", ~fit.group_b), ("B", fit.group_b)):
        cal[g] = fit_calibration(fit.x[mask], fit.y[mask], cell.calibration_bins)
    fp = FittedPolicy("P1", {}, calibration=cal)
    s = fp.scores(fit)
    th = fit_threshold(s, fit.tie_u, capacity_count(cell.kappa, fit.n))
    fp.thresholds = {"A": th, "B": th}
    return fp


def fit_p2(fit: Population, cell: CellConfig) -> FittedPolicy:
    """P2: selection-rate parity; group-specific thresholds, each group's rate equals kappa."""
    _require_groups(fit, "P2")
    ths = {}
    for g, mask in (("A", ~fit.group_b), ("B", fit.group_b)):
        ng = int(mask.sum())
        ths[g] = fit_threshold(fit.x[mask], fit.tie_u[mask], capacity_count(cell.kappa, ng))
    return FittedPolicy("P2", ths)


def _tpr_threshold(x_pos_desc: NDArray[np.float64], j: int) -> Threshold:
    """Threshold selecting X >= the j-th largest qualified score (j = 0 selects nobody)."""
    if j == 0:
        return Threshold(float(np.inf), 0.0)
    return Threshold(float(x_pos_desc[j - 1]), 1.0)


def fit_p3(fit: Population, cell: CellConfig, iters: int = 64) -> FittedPolicy:
    """P3: equal opportunity; group thresholds with equal TPR on the fitting population, overall rate
    as close to kappa as the finite population allows (bisection on the common TPR)."""
    _require_groups(fit, "P3", need_positive=True)
    k = capacity_count(cell.kappa, fit.n)
    groups = {}
    for g, mask in (("A", ~fit.group_b), ("B", fit.group_b)):
        xg = fit.x[mask]
        pos_desc = np.sort(fit.x[mask & fit.y])[::-1]
        groups[g] = (xg, pos_desc)

    def at(tau: float) -> tuple[dict[str, Threshold], int]:
        ths, total = {}, 0
        for g, (xg, pos_desc) in groups.items():
            j = int(round(tau * pos_desc.shape[0]))
            th = _tpr_threshold(pos_desc, j)
            ths[g] = th
            total += int(np.count_nonzero(xg >= th.t))
        return ths, total

    lo, hi = 0.0, 1.0
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if at(mid)[1] < k:
            lo = mid
        else:
            hi = mid
    cand = [at(lo), at(hi)]
    ths, total = min(cand, key=lambda c: (abs(c[1] - k), c[1]))
    tprs = {}
    for g, (xg, pos_desc) in groups.items():
        tprs[g] = float(np.count_nonzero(pos_desc >= ths[g].t) / pos_desc.shape[0])
    diag = {"fit_selected": total, "fit_target": k, "fit_tpr_a": tprs["A"], "fit_tpr_b": tprs["B"],
            "fit_tpr_gap": tprs["A"] - tprs["B"]}
    return FittedPolicy("P3", ths, diagnostics=diag)


FITTERS = {"P0": fit_p0, "P1": fit_p1, "P2": fit_p2, "P3": fit_p3}


def fit_policy(policy: str, fit: Population, cell: CellConfig) -> FittedPolicy:
    if policy not in FITTERS:
        raise ValueError(f"unknown policy {policy!r}")
    fp = FITTERS[policy](fit, cell)
    sel = fp.select(fit)
    fp.diagnostics.setdefault("fit_selected", int(sel.sum()))
    fp.diagnostics.setdefault("fit_target", capacity_count(cell.kappa, fit.n))
    return fp
