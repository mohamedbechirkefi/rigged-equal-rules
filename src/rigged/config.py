# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Typed, validated configuration objects and canonical hashing.

Units: every latent and observed quantity is in standard-deviation units of the latent qualification
of Group A (s_A = 1 in the primary model). Rates (kappa, p_B, base rates) are proportions in [0, 1].
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass

from . import GENERATOR_VERSION
from .numerics import FAMILIES, base_rate

POLICIES = ("P0", "P1", "P2", "P3")


class ConfigError(ValueError):
    """Raised when a configuration is invalid."""


@dataclass(frozen=True)
class CellConfig:
    """One cell of an experimental matrix: the generator and operating-point parameters."""

    cell_id: str
    family: str = "gaussian"
    mu_a: float = 0.0
    mu_b: float = 0.0
    s_a: float = 1.0
    s_b: float = 1.0
    sigma_a: float = 0.5
    sigma_b: float = 0.5
    kappa: float = 0.30
    p_b: float = 0.5
    cost_ratio: float = 1.0
    calibration_bins: int = 20
    ece_bins: int = 10
    note: str = ""

    def __post_init__(self) -> None:
        if not self.cell_id or not isinstance(self.cell_id, str):
            raise ConfigError("cell_id must be a non-empty string")
        if self.family not in FAMILIES:
            raise ConfigError(f"family must be one of {FAMILIES}, got {self.family!r}")
        for name in ("mu_a", "mu_b", "s_a", "s_b", "sigma_a", "sigma_b", "kappa", "p_b", "cost_ratio"):
            v = getattr(self, name)
            if not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v):
                raise ConfigError(f"{name} must be a finite number, got {v!r}")
        if self.s_a <= 0 or self.s_b <= 0:
            raise ConfigError("latent dispersions s_a, s_b must be positive")
        if self.sigma_a < 0 or self.sigma_b < 0:
            raise ConfigError("measurement-noise SDs sigma_a, sigma_b must be non-negative")
        if not 0.0 <= self.kappa <= 1.0:
            raise ConfigError("kappa (capacity) must lie in [0, 1]")
        if not 0.0 <= self.p_b <= 1.0:
            raise ConfigError("p_b (share of group B) must lie in [0, 1]")
        if self.cost_ratio < 0:
            raise ConfigError("cost_ratio must be non-negative")
        if not isinstance(self.calibration_bins, int) or self.calibration_bins < 1:
            raise ConfigError("calibration_bins must be a positive integer")
        if not isinstance(self.ece_bins, int) or self.ece_bins < 1:
            raise ConfigError("ece_bins must be a positive integer")

    @property
    def base_rate_a(self) -> float:
        return base_rate(self.family, self.mu_a, self.s_a)

    @property
    def base_rate_b(self) -> float:
        return base_rate(self.family, self.mu_b, self.s_b)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["base_rate_a"] = self.base_rate_a
        d["base_rate_b"] = self.base_rate_b
        return d


@dataclass(frozen=True)
class RunSpec:
    """One run: a cell, a policy, a seed and a population size (fitting and evaluation each)."""

    experiment_id: str
    cell: CellConfig
    policy: str
    seed: int
    n: int

    def __post_init__(self) -> None:
        if self.policy not in POLICIES:
            raise ConfigError(f"policy must be one of {POLICIES}, got {self.policy!r}")
        if not isinstance(self.seed, int) or isinstance(self.seed, bool) or self.seed < 0:
            raise ConfigError("seed must be a non-negative integer")
        if not isinstance(self.n, int) or isinstance(self.n, bool) or self.n < 1:
            raise ConfigError("n must be a positive integer")

    @property
    def run_id(self) -> str:
        return f"RUN-{self.experiment_id}-{self.cell.cell_id}-{self.policy}-s{self.seed}"

    def to_dict(self) -> dict:
        return {
            "experiment_id": self.experiment_id,
            "cell": self.cell.to_dict(),
            "policy": self.policy,
            "seed": self.seed,
            "n": self.n,
            "generator_version": GENERATOR_VERSION,
        }

    def config_hash(self) -> str:
        return canonical_hash(self.to_dict())


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def canonical_hash(obj) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()
