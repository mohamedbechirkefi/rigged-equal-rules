// SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
// Sandbox settings, their bounds and their validation (shared by the page and the worker).
import type { Cell } from "./engine";

export interface SandboxParams extends Cell {
  seed: number;
  seeds: number;
  n: number;
}

export const LIMITS = { maxN: 20_000, minN: 1_000, maxSeeds: 10 };
export function checkParams(p: SandboxParams): string | null {
  const finite = [p.delta, p.rho, p.kappa, p.p_b, p.seed, p.seeds, p.n].every(Number.isFinite);
  if (!finite) return "every setting must be a number";
  if (p.n < LIMITS.minN || p.n > LIMITS.maxN || !Number.isInteger(p.n)) return "n must be an integer from 1,000 to 20,000";
  if (p.seeds < 1 || p.seeds > LIMITS.maxSeeds || !Number.isInteger(p.seeds)) return "seeds must be from 1 to 10";
  if (!Number.isInteger(p.seed) || p.seed < 1 || p.seed > 1_000_000) return "seed must be an integer from 1 to 1,000,000";
  if (p.delta < 0 || p.delta > 2) return "delta must lie in [0, 2]";
  if (p.rho < 0.5 || p.rho > 3) return "rho must lie in [0.5, 3]";
  if (p.kappa <= 0 || p.kappa >= 1) return "kappa must lie strictly between 0 and 1";
  if (p.p_b <= 0 || p.p_b >= 1) return "p_B must lie strictly between 0 and 1";
  return null;
}

