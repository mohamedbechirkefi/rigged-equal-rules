# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Experimental matrices from research/protocol.md and the experiment protocols (amended before freeze).

Registered experiments (EXP-001 to EXP-003) use the confirmatory seeds 0 to 19. Exploratory matrices
(SMOKE, SIZING, DEGEN) are labelled exploratory; SIZING and DEGEN use seeds disjoint from the
confirmatory seeds so that no confirmatory seed is evaluated before the freeze.
"""

from __future__ import annotations

from dataclasses import dataclass

from .config import CellConfig, RunSpec
from .numerics import matched_mean, norm_cdf

CONFIRMATORY_SEEDS = tuple(range(20))
EXPLORATORY_SEED_BASE = 1000


@dataclass(frozen=True)
class Matrix:
    matrix_id: str
    experiment_id: str
    label: str  # "exploratory" or "confirmatory"
    description: str
    cells: tuple[CellConfig, ...]
    policies_by_cell: dict
    seeds: tuple[int, ...]
    n: int
    contrasts: tuple[tuple[str, str], ...] = ()  # (treatment cell, control cell) pairs, P0

    def runs(self) -> list[RunSpec]:
        out = []
        for seed in self.seeds:
            for cell in self.cells:
                for pol in self.policies_by_cell[cell.cell_id]:
                    out.append(RunSpec(self.experiment_id, cell, pol, seed, self.n))
        return out


def gaussian_cell(delta: float, rho: float, **kw) -> CellConfig:
    cid = kw.pop("cell_id", f"d{delta:.2f}-r{rho:.2f}")
    return CellConfig(cell_id=cid, mu_a=0.0, mu_b=-delta, sigma_a=0.5, sigma_b=0.5 * rho, **kw)


EXP12_DELTAS = (0.0, 0.25, 0.5, 1.0)
EXP12_RHOS = (1.0, 1.5, 2.0)


def exp001(n: int = 20_000, seeds=CONFIRMATORY_SEEDS) -> Matrix:
    cells = tuple(gaussian_cell(d, r) for d in EXP12_DELTAS for r in EXP12_RHOS)
    return Matrix("EXP-001", "EXP-001", "confirmatory", "EXP-001 full matrix (P0, 12 cells)", cells,
                  {c.cell_id: ("P0",) for c in cells}, tuple(seeds), n,
                  contrasts=(("d0.50-r1.00", "d0.00-r1.00"),))


def exp002(n: int = 20_000, seeds=CONFIRMATORY_SEEDS) -> Matrix:
    cells = tuple(gaussian_cell(d, r) for d in EXP12_DELTAS for r in EXP12_RHOS)
    return Matrix("EXP-002", "EXP-002", "confirmatory", "EXP-002 full matrix (P0 to P3, 12 cells)", cells,
                  {c.cell_id: ("P0", "P1", "P2", "P3") for c in cells}, tuple(seeds), n,
                  contrasts=(("d0.50-r1.00", "d0.00-r1.00"),))


def exp003_cells() -> list[tuple[CellConfig, tuple[str, ...]]]:
    pi_gap = float(norm_cdf(-0.5))
    out = []
    for sb in (0.5, 1.0, 2.0):  # Grid A: equal base rates
        out.append((CellConfig(cell_id=f"A-sB{sb:g}", s_b=sb, mu_b=0.0), ("P0", "P3")))
    for sb in (0.5, 1.0, 2.0):  # Grid B: fixed base-rate gap
        out.append((CellConfig(cell_id=f"B-sB{sb:g}", s_b=sb, mu_b=-0.5 * sb), ("P0", "P3")))
    for fam in ("gaussian", "student_t3", "lognormal"):  # Grid C: shape, matched base rates
        out.append((CellConfig(cell_id=f"C-{fam}", family=fam, mu_a=matched_mean(fam, 1.0, 0.5),
                               mu_b=matched_mean(fam, 1.0, pi_gap)), ("P0",)))
    for kappa in (0.1, 0.3, 0.5):  # Grid D: operating point
        for pb in (0.2, 0.5):
            out.append((gaussian_cell(0.5, 1.0, cell_id=f"D-k{kappa:g}-pB{pb:g}", kappa=kappa, p_b=pb), ("P0",)))
    return out


def exp003(n: int = 20_000, seeds=CONFIRMATORY_SEEDS) -> Matrix:
    cp = exp003_cells()
    return Matrix("EXP-003", "EXP-003", "confirmatory", "EXP-003 sensitivity grids A to D",
                  tuple(c for c, _ in cp), {c.cell_id: p for c, p in cp}, tuple(seeds), n)


ADULT_POOL_N = 16_281  # kept rows of adult.test (data/ingestion_report.json)
EXP004_P3_TOLERANCE = 30  # protocol section 13, round 2 (tied real scores); ratified in round 3 and on 2026-11-25
EXP004_PARTITIONS = ("hours", "hours-random")  # protocol section 13, amendment of 2026-11-25 (A25-1 to A25-3)
EXP004_CONTRASTS = (("R-hours", "R-hours-random"),)  # primary contrast only


def exp004(n: int = ADULT_POOL_N, seeds=CONFIRMATORY_SEEDS) -> Matrix:
    """EXP-004: second test on the UCI Adult score distribution, P0 to P3 (protocol section 13, 2026-11-25).

    Primary contrast R-hours vs R-hours-random. No protected attribute is used.
    """
    cells = tuple(CellConfig(cell_id=f"R-{part}", data_source=f"ADULT-R1:{part}", p3_tolerance=EXP004_P3_TOLERANCE)
                  for part in EXP004_PARTITIONS)
    return Matrix("EXP-004", "EXP-004", "confirmatory", "EXP-004 second test on a real score distribution (UCI Adult)",
                  cells, {c.cell_id: ("P0", "P1", "P2", "P3") for c in cells}, tuple(seeds), n,
                  contrasts=EXP004_CONTRASTS)


def smoke() -> Matrix:
    """Protocol section 9 smoke matrix: delta in {0, 0.5}, rho = 1, P0 to P3, seeds 1000 to 1002, n = 2,000."""
    cells = (gaussian_cell(0.0, 1.0), gaussian_cell(0.5, 1.0))
    return Matrix("SMOKE", "SMOKE", "exploratory", "Protocol smoke matrix (exploratory)", cells,
                  {c.cell_id: ("P0", "P1", "P2", "P3") for c in cells},
                  tuple(range(EXPLORATORY_SEED_BASE, EXPLORATORY_SEED_BASE + 3)), 2_000,
                  contrasts=(("d0.50-r1.00", "d0.00-r1.00"),))


def sizing(n_seeds: int = 20) -> Matrix:
    """Exploratory sizing run at full n on seeds disjoint from the confirmatory seeds.

    Measures runtime per run and the per-seed spread for the primary contrast and every policy, plus
    the non-Gaussian and extreme cells whose runtime and stability are least certain.
    """
    cells = [gaussian_cell(0.0, 1.0), gaussian_cell(0.5, 1.0), gaussian_cell(1.0, 2.0)]
    pols = {c.cell_id: ("P0", "P1", "P2", "P3") for c in cells}
    for c, _ in exp003_cells():
        if c.cell_id in ("C-student_t3", "C-lognormal", "D-k0.1-pB0.2", "B-sB2"):
            cells.append(c)
            pols[c.cell_id] = ("P0", "P3")
    seeds = tuple(range(EXPLORATORY_SEED_BASE, EXPLORATORY_SEED_BASE + n_seeds))
    return Matrix("SIZING", "SIZING", "exploratory", "Exploratory sizing run at n = 20,000 (seeds 1000+)",
                  tuple(cells), pols, seeds, 20_000, contrasts=(("d0.50-r1.00", "d0.00-r1.00"),))


def degenerate() -> Matrix:
    """Exploratory probe of degenerate operating points (tiny groups, extreme capacity and gaps)."""
    cells = (
        gaussian_cell(3.0, 1.0, cell_id="G-tinyB", p_b=0.02),
        gaussian_cell(4.0, 1.0, cell_id="G-noqualB", p_b=0.1),
        gaussian_cell(0.5, 1.0, cell_id="G-k0", kappa=0.0),
        gaussian_cell(0.5, 1.0, cell_id="G-k1", kappa=1.0),
        gaussian_cell(0.5, 1.0, cell_id="G-pB0", p_b=0.0),
        CellConfig(cell_id="G-noiseless", mu_b=-0.5, sigma_a=0.0, sigma_b=0.0),
    )
    seeds = tuple(range(EXPLORATORY_SEED_BASE + 500, EXPLORATORY_SEED_BASE + 505))
    return Matrix("DEGEN", "DEGEN", "exploratory", "Exploratory degenerate-case probe (n = 60)", cells,
                  {c.cell_id: ("P0", "P1", "P2", "P3") for c in cells}, seeds, 60)


REGISTERED = {"EXP-001": exp001, "EXP-002": exp002, "EXP-003": exp003, "EXP-004": exp004}
EXPLORATORY = {"SMOKE": smoke, "SIZING": sizing, "DEGEN": degenerate}


def matrix_config(matrix: Matrix) -> dict:
    """Canonical, JSON-serialisable description of a matrix: the confirmatory config that is frozen.

    It lists every cell (with its policies), the seeds, n, the contrasts and the config hash of every
    planned run, so any change to the code that builds the matrix changes this document.
    """
    runs = matrix.runs()
    doc = {
        "config_schema": "rigged.matrix_config/1.0.0",
        "experiment_id": matrix.experiment_id, "matrix_id": matrix.matrix_id, "label": matrix.label,
        "description": matrix.description, "n": matrix.n, "seeds": list(matrix.seeds),
        "contrasts": [list(c) for c in matrix.contrasts],
        "cells": [{"cell": c.to_dict(), "policies": list(matrix.policies_by_cell[c.cell_id])} for c in matrix.cells],
        "run_count": len(runs),
        "run_config_hashes": {r.run_id: r.config_hash() for r in runs},
    }
    if any(c.is_real for c in matrix.cells):
        import json

        from .config import real_data_identity
        ident = real_data_identity()
        from .environment import REPO_ROOT
        doc["data"] = ident
        doc["score_model"] = json.loads((REPO_ROOT / ident["score_model"]).read_text(encoding="utf-8"))
        from .adult import GROUP_B_HOURS_BELOW
        doc["group_b"] = {"hours": f"hours_per_week < {GROUP_B_HOURS_BELOW:g} (protocol section 13, amendment of "
                                   "2026-11-25, A25-1)",
                          "random": "hours labels permuted by the seed's row-index permutation"}
    return doc
