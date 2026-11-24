# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Group-wise confusion matrices and fairness metrics (protocol section 5).

Undefined metrics (zero denominators) are returned as None with a reason; they are never imputed.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

GROUP_METRICS = ("sr", "tpr", "fnr", "fpr", "ppv", "ece")
GAP_METRICS = ("sr_gap", "eog", "fpr_gap", "ppv_gap", "ece_gap")


@dataclass(frozen=True)
class Confusion:
    tp: int
    fp: int
    tn: int
    fn: int

    @property
    def n(self) -> int:
        return self.tp + self.fp + self.tn + self.fn

    @property
    def positives(self) -> int:
        return self.tp + self.fn

    @property
    def negatives(self) -> int:
        return self.fp + self.tn

    @property
    def selected(self) -> int:
        return self.tp + self.fp


def confusion(y: NDArray[np.bool_], sel: NDArray[np.bool_]) -> Confusion:
    if y.shape != sel.shape:
        raise ValueError("y and selection must have the same shape")
    y = y.astype(bool)
    sel = sel.astype(bool)
    tp = int(np.count_nonzero(y & sel))
    fp = int(np.count_nonzero(~y & sel))
    fn = int(np.count_nonzero(y & ~sel))
    tn = int(np.count_nonzero(~y & ~sel))
    return Confusion(tp, fp, tn, fn)


def ratio(num: float, den: float, name: str, undefined: dict[str, str]) -> float | None:
    """num / den, or None (with a recorded reason) when den == 0."""
    if den == 0:
        undefined[name] = f"zero denominator ({name})"
        return None
    return float(num) / float(den)


def expected_calibration_error(y: NDArray[np.bool_], score: NDArray[np.float64], bins: int) -> float | None:
    """ECE over equal-width bins of [0, 1]: sum_b (n_b / n) |mean(y_b) - mean(score_b)|. None if n == 0."""
    n = y.shape[0]
    if n == 0:
        return None
    if np.any((score < 0) | (score > 1)):
        raise ValueError("calibrated scores must lie in [0, 1]")
    idx = np.minimum((score * bins).astype(np.int64), bins - 1)
    cnt = np.bincount(idx, minlength=bins)
    ysum = np.bincount(idx, weights=y.astype(np.float64), minlength=bins)
    ssum = np.bincount(idx, weights=score, minlength=bins)
    nz = cnt > 0
    return float(np.sum(np.abs(ysum[nz] - ssum[nz])) / n)


def group_metrics(c: Confusion, ece: float | None, group: str, undefined: dict[str, str]) -> dict:
    u: dict[str, str] = {}
    tpr = ratio(c.tp, c.positives, "tpr", u)
    out = {
        "n": c.n, "positives": c.positives, "negatives": c.negatives, "selected": c.selected,
        "tp": c.tp, "fp": c.fp, "tn": c.tn, "fn": c.fn,
        "sr": ratio(c.selected, c.n, "sr", u),
        "tpr": tpr,
        "fnr": None if tpr is None else 1.0 - tpr,
        "fpr": ratio(c.fp, c.negatives, "fpr", u),
        "ppv": ratio(c.tp, c.selected, "ppv", u),
        "ece": ece,
    }
    if tpr is None:
        u["fnr"] = u["tpr"]
    if ece is None:
        u["ece"] = "zero denominator (ece: empty group)"
    for k, v in u.items():
        undefined[f"{group}.{k}"] = v
    return out


def gap(a: float | None, b: float | None, name: str, undefined: dict[str, str]) -> float | None:
    if a is None or b is None:
        undefined[name] = "undefined component (" + ", ".join(
            g for g, v in (("A", a), ("B", b)) if v is None) + ")"
        return None
    return a - b


def evaluate(y: NDArray[np.bool_], group_b: NDArray[np.bool_], sel: NDArray[np.bool_],
             calibrated: NDArray[np.float64], cost_ratio: float, ece_bins: int) -> dict:
    """All metrics of one run on the evaluation population."""
    undefined: dict[str, str] = {}
    groups = {}
    for g, mask in (("A", ~group_b), ("B", group_b)):
        c = confusion(y[mask], sel[mask])
        ece = expected_calibration_error(y[mask], calibrated[mask], ece_bins)
        groups[g] = group_metrics(c, ece, g, undefined)
    call = confusion(y, sel)
    n = call.n
    overall = {
        "n": n, "selected": call.selected, "tp": call.tp, "fp": call.fp, "tn": call.tn, "fn": call.fn,
        "sr": ratio(call.selected, n, "overall.sr", undefined),
        "utility_per_capita": ratio(call.tp - cost_ratio * call.fp, n, "overall.utility_per_capita", undefined),
        "accuracy": ratio(call.tp + call.tn, n, "overall.accuracy", undefined),
    }
    a, b = groups["A"], groups["B"]
    gaps = {
        "sr_gap": gap(a["sr"], b["sr"], "sr_gap", undefined),
        "eog": gap(a["tpr"], b["tpr"], "eog", undefined),
        "fpr_gap": gap(a["fpr"], b["fpr"], "fpr_gap", undefined),
        "ppv_gap": gap(a["ppv"], b["ppv"], "ppv_gap", undefined),
        "ece_gap": gap(a["ece"], b["ece"], "ece_gap", undefined),
    }
    return {"groups": groups, "overall": overall, "gaps": gaps, "undefined": undefined}
