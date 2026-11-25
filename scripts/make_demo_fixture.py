# SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
"""Write the sandbox test fixture demo/src/fixtures/engine_fixture.json from the Python engine.

TEST FIXTURE, NOT A RESULT. It records, for two small Gaussian cells (n = 600 per population,
exploratory seed 1000), the engine's own standard draws and the outputs of policies P0 to P3 and of
the metrics, exactly as src/rigged/runner.py computes them. The JavaScript port in
demo/src/engine.ts is fed the same draws and must reproduce every output (vitest,
demo/src/engine.test.ts). The fixture also records the P0 population EOG by numerical integration
for the statistical check of the port's own random-number generator. Compute: well under a second,
one process. No timestamps; deterministic.

Usage: PYTHONPATH=src .venv/bin/python scripts/make_demo_fixture.py
"""

from __future__ import annotations

import json
from pathlib import Path

from rigged.analytic import p0_population_metrics
from rigged.config import CellConfig
from rigged.generator import STREAM_EVAL, STREAM_FIT, build_population, draw
from rigged.metrics import evaluate
from rigged.policies import fit_calibration, fit_policy

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "demo" / "src" / "fixtures" / "engine_fixture.json"
N = 600
SEED = 1000


def cell(delta: float, rho: float) -> CellConfig:
    return CellConfig(cell_id=f"d{delta:.2f}-r{rho:.2f}", mu_a=0.0, mu_b=-delta, sigma_a=0.5, sigma_b=0.5 * rho)


def draws_dict(d) -> dict:
    return {"group_u": d.group_u.tolist(), "z": d.z.tolist(), "noise": d.noise.tolist(), "tie_u": d.tie_u.tolist()}


def main() -> int:
    d_fit, d_eval = draw(SEED, STREAM_FIT, N), draw(SEED, STREAM_EVAL, N)
    cases = []
    for delta, rho in ((0.5, 1.0), (1.0, 2.0)):
        c = cell(delta, rho)
        fit, ev = build_population(c, d_fit), build_population(c, d_eval)
        cal = fit_calibration(fit.x, fit.y, c.calibration_bins)
        policies = {}
        for p in ("P0", "P1", "P2", "P3"):
            fp = fit_policy(p, fit, c)
            sel = fp.select(ev)
            m = evaluate(ev.y, ev.group_b, sel, cal(ev.x), c.cost_ratio, c.ece_bins)
            policies[p] = {"selected_eval": int(sel.sum()), "fit_selected": int(fp.select(fit).sum()),
                           "gaps": m["gaps"], "tpr_a": m["groups"]["A"]["tpr"], "tpr_b": m["groups"]["B"]["tpr"],
                           "utility_per_capita": m["overall"]["utility_per_capita"]}
        cases.append({"delta": delta, "rho": rho, "kappa": c.kappa, "p_b": c.p_b,
                      "population_p0_eog": p0_population_metrics(c)["eog"], "policies": policies})
    fixture = {"label": "test fixture, not a result", "generator": "rigged.generator.draw (numpy PCG64)",
               "seed": SEED, "n": N, "fit": draws_dict(d_fit), "eval": draws_dict(d_eval), "cases": cases}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(fixture, separators=(",", ":"), allow_nan=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
