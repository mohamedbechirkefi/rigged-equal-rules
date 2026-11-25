// SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
// The sandbox port against the Python engine. The fixture (scripts/make_demo_fixture.py) holds the
// engine's own numpy draws for two cells at n = 600 and the outputs of P0 to P3 and the metrics.
// Tolerance: counts exactly equal; every metric within 1e-9 absolute (floating-point summation order).
// A second check runs the port's own random numbers at the EXP-001 primary cell and compares the mean
// P0 EOG with the population value by numerical integration, within 3 standard errors.
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import {
  buildPopulation, capacityCount, fitPolicy, POLICIES, roundHalfEven, runCell, sandboxDraws, select, type Cell,
  type Draws,
} from "./engine";

const TOL = 1e-9;
const fx = JSON.parse(readFileSync("src/fixtures/engine_fixture.json", "utf8")) as {
  n: number; fit: Draws; eval: Draws;
  cases: { delta: number; rho: number; kappa: number; p_b: number; population_p0_eog: number;
    policies: Record<string, { selected_eval: number; fit_selected: number; tpr_a: number; tpr_b: number;
      utility_per_capita: number; gaps: Record<string, number> }> }[];
};

describe("port matches the Python engine on identical draws", () => {
  for (const c of fx.cases) {
    const cell: Cell = { delta: c.delta, rho: c.rho, kappa: c.kappa, p_b: c.p_b };
    it(`delta ${c.delta}, rho ${c.rho}: P0 to P3, counts exact, metrics within ${TOL}`, () => {
      const out = runCell(cell, fx.fit, fx.eval);
      const fit = buildPopulation(cell, fx.fit);
      for (const o of out) {
        const want = c.policies[o.policy];
        expect(o.ok, o.policy).toBe(true);
        if (!o.ok) continue;
        expect(o.metrics.selected).toBe(want.selected_eval);
        expect(select(fitPolicy(o.policy, fit, cell), fit).filter(Boolean).length).toBe(want.fit_selected);
        for (const k of ["sr_gap", "eog", "fpr_gap", "ppv_gap", "ece_gap"] as const) {
          expect(Math.abs((o.metrics[k] as number) - want.gaps[k]), `${o.policy} ${k}`).toBeLessThan(TOL);
        }
        expect(Math.abs((o.metrics.tpr_a as number) - want.tpr_a)).toBeLessThan(TOL);
        expect(Math.abs((o.metrics.tpr_b as number) - want.tpr_b)).toBeLessThan(TOL);
        expect(Math.abs((o.metrics.utility_per_capita as number) - want.utility_per_capita)).toBeLessThan(TOL);
      }
      expect(out.map((o) => o.policy)).toEqual([...POLICIES]);
    });
  }
});

describe("helpers", () => {
  it("rounds half to even like Python", () => {
    expect([0.5, 1.5, 2.5, 2.4, 2.6].map(roundHalfEven)).toEqual([0, 2, 2, 2, 3]);
    expect(capacityCount(0.3, 600)).toBe(180);
  });
  it("sandbox draws are deterministic per seed and differ across seeds", () => {
    expect(sandboxDraws(7, 0, 50)).toEqual(sandboxDraws(7, 0, 50));
    expect(sandboxDraws(7, 0, 50).z).not.toEqual(sandboxDraws(8, 0, 50).z);
    expect(sandboxDraws(7, 0, 50).z).not.toEqual(sandboxDraws(7, 1, 50).z);
  });
});

describe("the port's own random numbers", () => {
  it("P0 EOG at delta 0.5, rho 1 agrees with the population value within 3 SE (10 seeds, n 20,000)", () => {
    const c = fx.cases[0];
    const cell: Cell = { delta: c.delta, rho: c.rho, kappa: c.kappa, p_b: c.p_b };
    const vals: number[] = [];
    for (let s = 1; s <= 10; s++) {
      const p0 = runCell(cell, sandboxDraws(s, 0, 20000), sandboxDraws(s, 1, 20000))[0];
      if (!p0.ok) throw new Error(p0.reason);
      vals.push(p0.metrics.eog as number);
    }
    const mean = vals.reduce((a, b) => a + b, 0) / vals.length;
    const sd = Math.sqrt(vals.reduce((a, b) => a + (b - mean) ** 2, 0) / (vals.length - 1));
    const se = sd / Math.sqrt(vals.length);
    expect(Math.abs(mean - c.population_p0_eog)).toBeLessThan(3 * se);
  });
});
