# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Synthetic two-group population generator with common random numbers (SYN-001).

For individual i in group g: Q_i = mu_g + s_g * W_i (W standardised, of the cell's family),
Y_i = 1[Q_i > 0], X_i = Q_i + sigma_g * U_i. Group B if the group uniform is below p_B.

Within a seed, every cell and policy uses the same standard draws (common random numbers). The fitting
and evaluation populations come from separate, independent RNG streams of the same seed.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .config import CellConfig
from .numerics import standardised_latent

STREAM_FIT = 0
STREAM_EVAL = 1


@dataclass(frozen=True)
class Draws:
    """Standard draws for one population; independent of every cell parameter."""

    group_u: NDArray[np.float64]  # uniform [0, 1)
    z: NDArray[np.float64]  # standard normal, latent
    w3: NDArray[np.float64]  # standard normal (n, 3), used by the Student t family
    noise: NDArray[np.float64]  # standard normal, measurement noise
    tie_u: NDArray[np.float64]  # uniform [0, 1), threshold tie-breaking

    @property
    def n(self) -> int:
        return int(self.z.shape[0])


@dataclass(frozen=True)
class Population:
    group_b: NDArray[np.bool_]  # True for Group B
    q: NDArray[np.float64]  # latent qualification
    y: NDArray[np.bool_]  # explicit qualification label
    x: NDArray[np.float64]  # observed score
    tie_u: NDArray[np.float64]

    @property
    def n(self) -> int:
        return int(self.x.shape[0])


def draw(seed: int, stream: int, n: int) -> Draws:
    """Draw the standard random numbers of one population. Order of draws is fixed and versioned."""
    if n < 1:
        raise ValueError("n must be positive")
    if seed < 0 or stream not in (STREAM_FIT, STREAM_EVAL):
        raise ValueError("invalid seed or stream")
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence([seed, stream])))
    group_u = rng.random(n)
    z = rng.standard_normal(n)
    w3 = rng.standard_normal((n, 3))
    noise = rng.standard_normal(n)
    tie_u = rng.random(n)
    return Draws(group_u=group_u, z=z, w3=w3, noise=noise, tie_u=tie_u)


def build_population(cell: CellConfig, d: Draws) -> Population:
    """Transform standard draws into a population for the given cell. Pure function."""
    group_b = d.group_u < cell.p_b
    w = standardised_latent(cell.family, d.z, d.w3)
    mu = np.where(group_b, cell.mu_b, cell.mu_a)
    s = np.where(group_b, cell.s_b, cell.s_a)
    sigma = np.where(group_b, cell.sigma_b, cell.sigma_a)
    q = mu + s * w
    y = q > 0.0
    x = q + sigma * d.noise
    return Population(group_b=group_b, q=q, y=y, x=x, tie_u=d.tie_u)


def populations(cell: CellConfig, seed: int, n: int) -> tuple[Population, Population]:
    """Fitting and evaluation populations of one seed."""
    return build_population(cell, draw(seed, STREAM_FIT, n)), build_population(cell, draw(seed, STREAM_EVAL, n))
