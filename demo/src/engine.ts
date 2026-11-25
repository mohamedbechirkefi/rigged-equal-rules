// SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
// Port of the RIGGED engine for the sandbox: the Gaussian generator (SYN-001 build_population),
// policies P0 to P3 (src/rigged/policies.py) and the metrics (src/rigged/metrics.py), with the
// runner's group-blind calibration for the ECE metric (src/rigged/runner.py).
// Given the same standard draws, it reproduces the Python engine (engine.test.ts, fixture from
// scripts/make_demo_fixture.py). Its own random numbers come from mulberry32 and Box-Muller, not
// numpy's PCG64, so a sandbox seed does not reproduce a research seed.

export interface Draws {
  group_u: number[];
  z: number[];
  noise: number[];
  tie_u: number[];
}

export interface Cell {
  delta: number; // mu_A = 0, mu_B = -delta
  rho: number; // sigma_A = 0.5, sigma_B = 0.5 rho
  kappa: number;
  p_b: number;
}

export interface Population {
  group_b: boolean[];
  y: boolean[];
  x: number[];
  tie_u: number[];
}

export const SIGMA_A = 0.5;
export const CALIBRATION_BINS = 20;
export const ECE_BINS = 10;
export const COST_RATIO = 1;
export const P3_TOLERANCE = 10;
export const POLICIES = ["P0", "P1", "P2", "P3"] as const;
export type Policy = (typeof POLICIES)[number];

export class FitError extends Error {}

export function buildPopulation(cell: Cell, d: Draws): Population {
  const n = d.z.length;
  const group_b = new Array<boolean>(n);
  const y = new Array<boolean>(n);
  const x = new Array<number>(n);
  for (let i = 0; i < n; i++) {
    const b = d.group_u[i] < cell.p_b;
    const mu = b ? -cell.delta : 0;
    const sigma = b ? SIGMA_A * cell.rho : SIGMA_A;
    const q = mu + 1 * d.z[i];
    group_b[i] = b;
    y[i] = q > 0;
    x[i] = q + sigma * d.noise[i];
  }
  return { group_b, y, x, tie_u: d.tie_u.slice() };
}

/** Python's round(): round half to even. */
export function roundHalfEven(v: number): number {
  const f = Math.floor(v);
  const diff = v - f;
  if (diff > 0.5) return f + 1;
  if (diff < 0.5) return f;
  return f % 2 === 0 ? f : f + 1;
}

export function capacityCount(kappa: number, n: number): number {
  return roundHalfEven(kappa * n);
}

export interface Threshold {
  t: number;
  gamma: number;
}

const selects = (th: Threshold, s: number, u: number) => s > th.t || (s === th.t && u < th.gamma);

export function fitThreshold(scores: number[], tie_u: number[], k: number): Threshold {
  const n = scores.length;
  if (n === 0) throw new FitError("cannot fit a threshold on an empty set");
  if (k < 0 || k > n) throw new RangeError(`k must lie in [0, ${n}]`);
  if (k === 0) return { t: Infinity, gamma: 0 };
  const order = scores.slice().sort((a, b) => b - a);
  const v = order[k - 1];
  let above = 0;
  const tied: number[] = [];
  for (let i = 0; i < n; i++) {
    if (scores[i] > v) above++;
    else if (scores[i] === v) tied.push(tie_u[i]);
  }
  tied.sort((a, b) => a - b);
  const m = k - above;
  if (m === tied.length) return { t: v, gamma: 1 };
  let gamma = 0.5 * (tied[m - 1] + tied[m]);
  if (!(tied[m - 1] < gamma && gamma <= tied[m])) {
    if (!(tied[m - 1] < tied[m])) throw new FitError("tie uniforms collide");
    gamma = tied[m];
  }
  return { t: v, gamma };
}

/** numpy.quantile, default "linear" method, on a sorted array. */
function quantileSorted(a: number[], q: number): number {
  const n = a.length;
  const vi = n * q + (1 + q * (1 - 1 - 1)) - 1; // numpy _compute_virtual_index, alpha = beta = 1
  const lo = Math.floor(vi);
  const hi = Math.min(lo + 1, n - 1);
  const t = vi - lo;
  const x0 = a[lo];
  const x1 = a[hi];
  const diff = x1 - x0;
  return t >= 0.5 ? x1 - diff * (1 - t) : x0 + diff * t;
}

/** Number of edges <= v (numpy.searchsorted side="right"). */
function searchRight(edges: number[], v: number): number {
  let lo = 0;
  let hi = edges.length;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (edges[mid] <= v) lo = mid + 1;
    else hi = mid;
  }
  return lo;
}

export interface CalibrationMap {
  edges: number[];
  rate: number[];
}

export function fitCalibration(x: number[], y: boolean[], bins: number): CalibrationMap {
  if (x.length === 0) throw new FitError("cannot fit a calibration map on an empty set");
  const sorted = x.slice().sort((a, b) => a - b);
  const raw: number[] = [];
  for (let i = 1; i < bins; i++) raw.push(quantileSorted(sorted, i / bins));
  raw.sort((a, b) => a - b);
  const edges = raw.filter((v, i) => i === 0 || v !== raw[i - 1]);
  const nb = edges.length + 1;
  const count = new Array<number>(nb).fill(0);
  const pos = new Array<number>(nb).fill(0);
  let ysum = 0;
  for (let i = 0; i < x.length; i++) {
    const b = searchRight(edges, x[i]);
    count[b]++;
    if (y[i]) pos[b] += 1;
    if (y[i]) ysum++;
  }
  const fallback = ysum / x.length;
  return { edges, rate: count.map((c, b) => (c > 0 ? pos[b] / c : fallback)) };
}

export const applyCalibration = (m: CalibrationMap, v: number) => m.rate[searchRight(m.edges, v)];

export interface Fitted {
  policy: Policy;
  thresholds: { A: Threshold; B: Threshold };
  calibration: { A: CalibrationMap; B: CalibrationMap } | null;
}

function subset<T>(arr: T[], mask: boolean[], want: boolean): T[] {
  const out: T[] = [];
  for (let i = 0; i < arr.length; i++) if (mask[i] === want) out.push(arr[i]);
  return out;
}

function requireGroups(pop: Population, policy: string, needPositive = false) {
  for (const want of [false, true]) {
    const g = want ? "B" : "A";
    let n = 0;
    let pos = 0;
    for (let i = 0; i < pop.x.length; i++) {
      if (pop.group_b[i] === want) {
        n++;
        if (pop.y[i]) pos++;
      }
    }
    if (n === 0) throw new FitError(`${policy}: group ${g} is empty in the fitting population`);
    if (needPositive && pos === 0) throw new FitError(`${policy}: group ${g} has no qualified member`);
  }
}

export function policyScores(fp: Fitted, pop: Population): number[] {
  if (fp.calibration === null) return pop.x;
  const cal = fp.calibration;
  return pop.x.map((v, i) => applyCalibration(pop.group_b[i] ? cal.B : cal.A, v));
}

export function select(fp: Fitted, pop: Population): boolean[] {
  const s = policyScores(fp, pop);
  return s.map((v, i) => selects(pop.group_b[i] ? fp.thresholds.B : fp.thresholds.A, v, pop.tie_u[i]));
}

export function fitPolicy(policy: Policy, fit: Population, cell: Cell): Fitted {
  const n = fit.x.length;
  const k = capacityCount(cell.kappa, n);
  if (policy === "P0") {
    const th = fitThreshold(fit.x, fit.tie_u, k);
    return { policy, thresholds: { A: th, B: th }, calibration: null };
  }
  if (policy === "P1") {
    requireGroups(fit, "P1");
    const cal = {
      A: fitCalibration(subset(fit.x, fit.group_b, false), subset(fit.y, fit.group_b, false), CALIBRATION_BINS),
      B: fitCalibration(subset(fit.x, fit.group_b, true), subset(fit.y, fit.group_b, true), CALIBRATION_BINS),
    };
    const fp: Fitted = { policy, thresholds: { A: { t: 0, gamma: 0 }, B: { t: 0, gamma: 0 } }, calibration: cal };
    const th = fitThreshold(policyScores(fp, fit), fit.tie_u, k);
    fp.thresholds = { A: th, B: th };
    return fp;
  }
  if (policy === "P2") {
    requireGroups(fit, "P2");
    const th = (want: boolean) => {
      const xs = subset(fit.x, fit.group_b, want);
      return fitThreshold(xs, subset(fit.tie_u, fit.group_b, want), capacityCount(cell.kappa, xs.length));
    };
    return { policy, thresholds: { A: th(false), B: th(true) }, calibration: null };
  }
  // P3: equal TPR on the fitting population, overall count as close to k as possible (bisection).
  requireGroups(fit, "P3", true);
  const groups = [false, true].map((want) => {
    const xg = subset(fit.x, fit.group_b, want);
    const posDesc: number[] = [];
    for (let i = 0; i < n; i++) if (fit.group_b[i] === want && fit.y[i]) posDesc.push(fit.x[i]);
    posDesc.sort((a, b) => b - a);
    return { xg, posDesc };
  });
  const at = (tau: number) => {
    let total = 0;
    const ths = groups.map(({ xg, posDesc }) => {
      const j = roundHalfEven(tau * posDesc.length);
      const th: Threshold = j === 0 ? { t: Infinity, gamma: 0 } : { t: posDesc[j - 1], gamma: 1 };
      for (const v of xg) if (v >= th.t) total++;
      return th;
    });
    return { ths, total };
  };
  let lo = 0;
  let hi = 1;
  for (let i = 0; i < 64; i++) {
    const mid = 0.5 * (lo + hi);
    if (at(mid).total < k) lo = mid;
    else hi = mid;
  }
  const a = at(lo);
  const b = at(hi);
  const key = (c: { total: number }) => [Math.abs(c.total - k), c.total];
  const [ka, kb] = [key(a), key(b)];
  const best = ka[0] < kb[0] || (ka[0] === kb[0] && ka[1] <= kb[1]) ? a : b;
  if (Math.abs(best.total - k) > P3_TOLERANCE) {
    throw new FitError(`P3: fitting count ${best.total} misses the target ${k} by more than ${P3_TOLERANCE}`);
  }
  return { policy, thresholds: { A: best.ths[0], B: best.ths[1] }, calibration: null };
}

export interface Metrics {
  sr_gap: number | null;
  eog: number | null;
  fpr_gap: number | null;
  ppv_gap: number | null;
  ece_gap: number | null;
  tpr_a: number | null;
  tpr_b: number | null;
  utility_per_capita: number | null;
  selected: number;
}

const ratio = (a: number, b: number) => (b === 0 ? null : a / b);
const gap = (a: number | null, b: number | null) => (a === null || b === null ? null : a - b);

function ece(y: boolean[], score: number[], bins: number): number | null {
  const n = y.length;
  if (n === 0) return null;
  const cnt = new Array<number>(bins).fill(0);
  const ys = new Array<number>(bins).fill(0);
  const ss = new Array<number>(bins).fill(0);
  for (let i = 0; i < n; i++) {
    const b = Math.min(Math.floor(score[i] * bins), bins - 1);
    cnt[b]++;
    ys[b] += y[i] ? 1 : 0;
    ss[b] += score[i];
  }
  let tot = 0;
  for (let b = 0; b < bins; b++) if (cnt[b] > 0) tot += Math.abs(ys[b] - ss[b]);
  return tot / n;
}

export function evaluate(ev: Population, sel: boolean[], calibrated: number[]): Metrics {
  const g = [false, true].map((want) => {
    let tp = 0, fp = 0, tn = 0, fn = 0;
    const yy: boolean[] = [];
    const sc: number[] = [];
    for (let i = 0; i < ev.x.length; i++) {
      if (ev.group_b[i] !== want) continue;
      const y = ev.y[i], s = sel[i];
      if (y && s) tp++;
      else if (!y && s) fp++;
      else if (y && !s) fn++;
      else tn++;
      yy.push(y);
      sc.push(calibrated[i]);
    }
    const n = tp + fp + tn + fn;
    return { tp, fp, sr: ratio(tp + fp, n), tpr: ratio(tp, tp + fn), fpr: ratio(fp, fp + tn),
             ppv: ratio(tp, tp + fp), ece: ece(yy, sc, ECE_BINS) };
  });
  const [A, B] = g;
  const tp = A.tp + B.tp, fp = A.fp + B.fp;
  return {
    sr_gap: gap(A.sr, B.sr), eog: gap(A.tpr, B.tpr), fpr_gap: gap(A.fpr, B.fpr), ppv_gap: gap(A.ppv, B.ppv),
    ece_gap: gap(A.ece, B.ece), tpr_a: A.tpr, tpr_b: B.tpr,
    utility_per_capita: ratio(tp - COST_RATIO * fp, ev.x.length), selected: tp + fp,
  };
}

export type RunOutcome = { policy: Policy; ok: true; metrics: Metrics } | { policy: Policy; ok: false; reason: string };

/** One seed of one cell: fit every policy on the fitting population, evaluate on the evaluation one. */
export function runCell(cell: Cell, dFit: Draws, dEval: Draws): RunOutcome[] {
  const fit = buildPopulation(cell, dFit);
  const ev = buildPopulation(cell, dEval);
  const cal = fitCalibration(fit.x, fit.y, CALIBRATION_BINS);
  const calibrated = ev.x.map((v) => applyCalibration(cal, v));
  return POLICIES.map((p) => {
    try {
      const fp = fitPolicy(p, fit, cell);
      return { policy: p, ok: true as const, metrics: evaluate(ev, select(fp, ev), calibrated) };
    } catch (e) {
      if (e instanceof FitError) return { policy: p, ok: false as const, reason: e.message };
      throw e;
    }
  });
}

// --- The sandbox's own random numbers (not numpy's) ---------------------------------------------

export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function normals(u: () => number, n: number): number[] {
  const out = new Array<number>(n);
  for (let i = 0; i < n; i += 2) {
    let u1 = u();
    while (u1 === 0) u1 = u();
    const r = Math.sqrt(-2 * Math.log(u1));
    const th = 2 * Math.PI * u();
    out[i] = r * Math.cos(th);
    if (i + 1 < n) out[i + 1] = r * Math.sin(th);
  }
  return out;
}

/** Standard draws of one population for a sandbox seed and stream (0 fitting, 1 evaluation). */
export function sandboxDraws(seed: number, stream: 0 | 1, n: number): Draws {
  const u = mulberry32(Math.imul(seed, 2654435761) ^ (stream === 0 ? 0x9e3779b9 : 0x85ebca6b));
  const group_u = Array.from({ length: n }, () => u());
  const z = normals(u, n);
  const noise = normals(u, n);
  const tie_u = Array.from({ length: n }, () => u());
  return { group_u, z, noise, tie_u };
}
