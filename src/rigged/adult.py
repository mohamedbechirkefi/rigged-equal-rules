# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""UCI Adult ingestion, score model and EXP-004 populations (protocol section 13, rounds 2 and 3).

Everything here is a pure function of its inputs except ``load_archive`` (reads the committed zip).
The score model is fitted once on ``adult.data`` (``fit_logistic``); the fitted values are frozen in
``research/experiments/EXP-004/config.json`` and only applied afterwards (``score``).
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from .environment import REPO_ROOT
from .generator import Population

ARCHIVE = REPO_ROOT / "data" / "raw" / "adult.zip"
ARCHIVE_SHA256 = "7537312dd56c2b98035880805ce99e68183a30ee468aa5329d6df0fbb3cc21bb"
COLUMNS = ("age", "workclass", "fnlwgt", "education", "education_num", "marital_status", "occupation",
           "relationship", "race", "sex", "capital_gain", "capital_loss", "hours_per_week", "native_country",
           "income")
USED_NUMERIC = ("age", "education_num", "capital_gain", "capital_loss", "hours_per_week")
FEATURES = ("age", "education_num", "log1p_capital_gain", "log1p_capital_loss")
LABELS = {"<=50K": False, ">50K": True}
GROUP_B_HOURS_BELOW = 40.0
SEX_VALUES = ("Male", "Female")
# Group B of R-sex: the sex value with the lower base rate on adult.data (protocol section 13, round 3,
# R3-1; JRN-0007: Female 0.1095, Male 0.3057). Training file only.
GROUP_B_SEX = "Female"
PARTITIONS = ("sex", "sex-random", "hours", "hours-random")
STREAM_REAL = 2


class AdultSchemaError(ValueError):
    """The input does not follow the Adult schema (for example an empty file)."""


@dataclass(frozen=True)
class AdultTable:
    """Processed rows: the used numeric columns and the label, one array per column."""

    age: NDArray[np.float64]
    education_num: NDArray[np.float64]
    capital_gain: NDArray[np.float64]
    capital_loss: NDArray[np.float64]
    hours_per_week: NDArray[np.float64]
    y: NDArray[np.bool_]
    sex: tuple[str, ...] | None = None  # recorded sex value of each kept row (round 3, R3-2)

    @property
    def n(self) -> int:
        return int(self.y.shape[0])


def parse_adult(text: str) -> tuple[AdultTable, dict]:
    """Parse one Adult file (``adult.data`` or ``adult.test``) into a table and an ingestion report.

    Comment lines (``|``) and blank lines are skipped. A row is excluded if it does not have 15 fields,
    if a used numeric column is missing or not numeric, or if the label is not ``<=50K`` / ``>50K``
    (a trailing ``.`` is removed). ``?`` in unused columns is counted, never imputed. A kept row whose
    ``sex`` is neither ``Male`` nor ``Female`` raises ``AdultSchemaError`` (round 3, R3-2): not an exclusion.
    """
    cols: dict[str, list[float]] = {c: [] for c in USED_NUMERIC}
    ys: list[bool] = []
    sexes: list[str] = []
    missing = {c: 0 for c in COLUMNS}
    excl = {"wrong_field_count": 0, "used_numeric_missing_or_invalid": 0, "invalid_label": 0}
    read = 0
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("|"):
            continue
        read += 1
        fields = [f.strip() for f in s.split(",")]
        if len(fields) != len(COLUMNS):
            excl["wrong_field_count"] += 1
            continue
        row = dict(zip(COLUMNS, fields))
        for c in COLUMNS:
            if row[c] == "?":
                missing[c] += 1
        vals = {}
        ok = True
        for c in USED_NUMERIC:
            try:
                v = float(row[c])
            except ValueError:
                ok = False
                break
            if not np.isfinite(v):
                ok = False
                break
            vals[c] = v
        if not ok:
            excl["used_numeric_missing_or_invalid"] += 1
            continue
        label = row["income"].rstrip(".")
        if label not in LABELS:
            excl["invalid_label"] += 1
            continue
        if row["sex"] not in SEX_VALUES:
            raise AdultSchemaError(f"kept row with sex {row['sex']!r} (neither Male nor Female)")
        for c in USED_NUMERIC:
            cols[c].append(vals[c])
        ys.append(LABELS[label])
        sexes.append(row["sex"])
    if read == 0:
        raise AdultSchemaError("no data rows")
    table = AdultTable(**{c: np.asarray(cols[c], dtype=np.float64) for c in USED_NUMERIC},
                       y=np.asarray(ys, dtype=bool), sex=tuple(sexes))
    report = {"rows_read": read, "rows_kept": table.n, "excluded": excl,
              "excluded_total": sum(excl.values()), "missing_by_column": missing}
    return table, report


def load_archive(path: Path = ARCHIVE) -> dict[str, str]:
    """Text of ``adult.data`` and ``adult.test`` from the committed archive."""
    with zipfile.ZipFile(path) as zf:
        return {name: zf.read(name).decode("utf-8") for name in ("adult.data", "adult.test")}


def raw_features(t: AdultTable) -> NDArray[np.float64]:
    """Unstandardised feature matrix in the order of FEATURES."""
    return np.column_stack([t.age, t.education_num, np.log1p(t.capital_gain), np.log1p(t.capital_loss)])


def fit_logistic(t: AdultTable, tol: float = 1e-10, max_iter: int = 100) -> dict:
    """Unpenalised logistic regression by Newton-Raphson on standardised features (protocol section 13)."""
    f = raw_features(t)
    mean = f.mean(axis=0)
    sd = f.std(axis=0)
    if np.any(sd <= 0):
        raise AdultSchemaError("a feature has zero variance")
    z = np.column_stack([np.ones(t.n), (f - mean) / sd])
    y = t.y.astype(np.float64)
    beta = np.zeros(z.shape[1])
    converged = False
    it = 0
    for it in range(1, max_iter + 1):
        eta = z @ beta
        p = 1.0 / (1.0 + np.exp(-eta))
        w = p * (1.0 - p)
        grad = z.T @ (y - p)
        hess = (z * w[:, None]).T @ z
        step = np.linalg.solve(hess, grad)
        beta = beta + step
        if float(np.max(np.abs(step))) < tol:
            converged = True
            break
    if not converged:
        raise RuntimeError("logistic fit did not converge")
    eta = z @ beta
    ll = float(np.sum(y * eta - np.logaddexp(0.0, eta)))
    return {"features": list(FEATURES), "standardisation": "training-file mean and population SD",
            "mean": [float(v) for v in mean], "sd": [float(v) for v in sd],
            "intercept": float(beta[0]), "coefficients": [float(v) for v in beta[1:]],
            "iterations": it, "converged": converged, "n_train": t.n,
            "train_log_likelihood": ll, "train_mean_log_loss": -ll / t.n}


def score(t: AdultTable, model: dict) -> NDArray[np.float64]:
    """Fitted log-odds for each row, using frozen model values."""
    f = (raw_features(t) - np.asarray(model["mean"])) / np.asarray(model["sd"])
    return model["intercept"] + f @ np.asarray(model["coefficients"])


def group_b_hours(t: AdultTable) -> NDArray[np.bool_]:
    """Group B of cell R-hours: hours-per-week below 40."""
    return t.hours_per_week < GROUP_B_HOURS_BELOW


def group_b_sex(t: AdultTable) -> NDArray[np.bool_]:
    """Group B of cell R-sex: recorded sex equal to GROUP_B_SEX (protocol section 13, round 3)."""
    if t.sex is None:
        raise AdultSchemaError("table has no sex column")
    return np.asarray([v == GROUP_B_SEX for v in t.sex], dtype=bool)


def sex_base_rates(t: AdultTable) -> dict:
    """Count and base rate P(Y = 1) per sex value: the R3-1 rule, applied to adult.data only."""
    if t.sex is None:
        raise AdultSchemaError("table has no sex column")
    sex = np.asarray(t.sex)
    out = {}
    for v in SEX_VALUES:
        m = sex == v
        n = int(m.sum())
        out[v] = {"n": n, "positives": int(t.y[m].sum()), "base_rate": float(t.y[m].mean()) if n else None}
    return out


def lower_base_rate_value(rates: dict) -> str:
    """The sex value with the lower base rate (R3-1); a tie is an error, not a choice."""
    a, b = (rates[v]["base_rate"] for v in SEX_VALUES)
    if a is None or b is None or a == b:
        raise AdultSchemaError("base rates undefined or tied; Group B cannot be set by the rule")
    return SEX_VALUES[0] if a < b else SEX_VALUES[1]


def real_populations(x: NDArray[np.float64], y: NDArray[np.bool_], group_b: NDArray[np.bool_], seed: int,
                     permute: bool) -> tuple[Population, Population]:
    """Fitting and evaluation populations of one seed (EXP-004 design, protocol section 13).

    Draw order (fixed): pool permutation, tie uniforms, row-index permutation. With ``permute`` the
    group labels are permuted by that index permutation (random cells; same group sizes); otherwise
    the observed labels are used.
    """
    if not isinstance(permute, bool):
        raise ValueError(f"permute must be a bool, got {permute!r}")
    n = int(x.shape[0])
    if not (y.shape[0] == n and group_b.shape[0] == n) or n < 2:
        raise ValueError("x, y and group_b must have the same length (at least 2)")
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence([seed, STREAM_REAL])))
    perm = rng.permutation(n)
    tie_u = rng.random(n)
    gperm = rng.permutation(n)
    g = group_b[gperm] if permute else group_b
    half = n // 2
    out = []
    for idx in (perm[:half], perm[half:]):
        out.append(Population(group_b=g[idx], q=np.full(idx.shape[0], np.nan), y=y[idx], x=x[idx],
                              tie_u=tie_u[idx]))
    return out[0], out[1]


SCORE_MODEL = REPO_ROOT / "research" / "experiments" / "EXP-004" / "score_model.json"
_POOL_CACHE: dict = {}


def load_pool(archive: Path = ARCHIVE, model_path: Path = SCORE_MODEL) -> tuple[NDArray[np.float64], NDArray[np.bool_],
                                                                                 dict[str, NDArray[np.bool_]]]:
    """EXP-004 pool: score, label and Group B indicators ("sex", "hours") of every kept ``adult.test`` row (cached)."""
    import hashlib
    import json

    key = (str(archive), str(model_path))
    if key not in _POOL_CACHE:
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        if digest != ARCHIVE_SHA256:
            raise AdultSchemaError(f"archive SHA-256 {digest} differs from the recorded {ARCHIVE_SHA256}")
        model = json.loads(model_path.read_text(encoding="utf-8"))
        table, _ = parse_adult(load_archive(archive)["adult.test"])
        _POOL_CACHE[key] = (score(table, model), table.y, {"sex": group_b_sex(table), "hours": group_b_hours(table)})
    return _POOL_CACHE[key]


def real_run_populations(data_source: str, seed: int) -> tuple[Population, Population]:
    """Populations of one EXP-004 run from its cell's data source ("ADULT-R1:<partition>", PARTITIONS)."""
    prefix, _, partition = data_source.partition(":")
    if prefix != "ADULT-R1" or partition not in PARTITIONS:
        raise ValueError(f"unknown data source {data_source!r}")
    attribute, _, rnd = partition.partition("-")
    x, y, groups = load_pool()
    return real_populations(x, y, groups[attribute], seed, rnd == "random")
