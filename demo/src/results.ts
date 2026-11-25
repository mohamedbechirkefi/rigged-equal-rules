// SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
// Published results: loaded from public/data/results.json, which
// scripts/export_demo_data.py writes from committed results only.
// Validation fails closed: any missing or malformed field means no numbers are shown.

export const SCHEMA = "lab-demo-results";
export const SCHEMA_MAJOR = 1;

export interface Estimate {
  label: string;
  estimate: number;
  ci_low: number | null;
  ci_high: number | null;
  ci_level: number | null;
  unit: string;
  /** Exact text the manuscript prints for the estimate and interval; shown verbatim when present. */
  display: string | null;
  interval_display: string | null;
  /** measured, analytic (numerical integration) or descriptive (no resampling). */
  kind: string;
}

export interface Experiment {
  id: string;
  title: string;
  status: string;
  verdict: string;
  estimates: Estimate[];
  claim_ids: string[];
  report_path: string;
  notes: string[];
}

export interface Assumption {
  name: string;
  value: string;
  source: string;
}

export interface Source {
  path: string;
  sha256: string;
}

export interface Results {
  schema: string;
  schema_version: string;
  project: string;
  question: string;
  status_label: string;
  code_revision: string;
  sources: Source[];
  experiments: Experiment[];
  assumptions: Assumption[];
  limitations: string[];
  explorer: Explorer;
  real_score: RealScore;
  display_exceptions: Record<string, string>;
}

/** A value shown on the page: seed mean with its 95% percentile bootstrap interval and exact text. */
export interface Value {
  estimate: number;
  ci_low: number;
  ci_high: number;
  display: string;
}

export interface PolicyBlock {
  policy: string;
  name: string;
  gaps: Record<string, Value>;
  tpr_a: Value;
  tpr_b: Value;
  within_2pp_all_three: boolean;
  utility_vs_p0: Value | null;
}

export interface ExplorerCell {
  cell_id: string;
  delta: number;
  rho: number;
  policies: PolicyBlock[];
}

export interface Explorer {
  experiment_id: string;
  label: string;
  unit: string;
  tolerance_pp: number;
  source: string;
  metrics: { key: string; label: string }[];
  deltas: number[];
  rhos: number[];
  cells: ExplorerCell[];
}

export interface RealScore {
  experiment_id: string;
  label: string;
  unit: string;
  tolerance_pp: number;
  source: string;
  cells: { cell_id: string; description: string; policies: PolicyBlock[] }[];
}

export const GAP_KEYS = ["sr_gap", "eog", "ppv_gap", "fpr_gap"] as const;
export const POLICY_IDS = ["P0", "P1", "P2", "P3"] as const;

export class ResultsError extends Error {}

type Obj = Record<string, unknown>;

function obj(v: unknown, where: string): Obj {
  if (typeof v !== "object" || v === null || Array.isArray(v)) {
    throw new ResultsError(`${where}: expected an object`);
  }
  return v as Obj;
}

function str(o: Obj, k: string, where: string): string {
  const v = o[k];
  if (typeof v !== "string" || v.length === 0) {
    throw new ResultsError(`${where}.${k}: expected a non-empty string`);
  }
  return v;
}

function num(o: Obj, k: string, where: string, nullable = false): number | null {
  const v = o[k];
  if (nullable && v === null) return null;
  if (typeof v !== "number" || !Number.isFinite(v)) {
    throw new ResultsError(`${where}.${k}: expected a finite number`);
  }
  return v;
}

function arr(o: Obj, k: string, where: string): unknown[] {
  const v = o[k];
  if (!Array.isArray(v)) throw new ResultsError(`${where}.${k}: expected an array`);
  return v;
}

function strArr(o: Obj, k: string, where: string): string[] {
  return arr(o, k, where).map((v, i) => {
    if (typeof v !== "string") throw new ResultsError(`${where}.${k}[${i}]: expected a string`);
    return v;
  });
}

function estimate(v: unknown, where: string): Estimate {
  const o = obj(v, where);
  const e: Estimate = {
    label: str(o, "label", where),
    estimate: num(o, "estimate", where) as number,
    ci_low: num(o, "ci_low", where, true),
    ci_high: num(o, "ci_high", where, true),
    ci_level: num(o, "ci_level", where, true),
    unit: typeof o.unit === "string" ? o.unit : "",
    display: typeof o.display === "string" ? o.display : null,
    interval_display: typeof o.interval_display === "string" ? o.interval_display : null,
    kind: str(o, "kind", where),
  };
  if (!["measured", "analytic", "descriptive"].includes(e.kind)) {
    throw new ResultsError(`${where}.kind: unknown kind ${e.kind}`);
  }
  if (e.display === null) throw new ResultsError(`${where}.display: expected the manuscript text`);
  if ((e.ci_low === null) !== (e.interval_display === null)) {
    throw new ResultsError(`${where}: interval and interval_display must be present together`);
  }
  if ((e.ci_low === null) !== (e.ci_high === null)) {
    throw new ResultsError(`${where}: interval must have both bounds or neither`);
  }
  if (e.ci_low !== null && e.ci_high !== null && e.ci_low > e.ci_high) {
    throw new ResultsError(`${where}: ci_low exceeds ci_high`);
  }
  return e;
}

export function validateResults(raw: unknown): Results {
  const o = obj(raw, "results");
  if (o.schema !== SCHEMA) throw new ResultsError(`results.schema: expected "${SCHEMA}"`);
  const version = str(o, "schema_version", "results");
  if (Number(version.split(".")[0]) !== SCHEMA_MAJOR) {
    throw new ResultsError(`results.schema_version: unsupported major version ${version}`);
  }
  const experiments = arr(o, "experiments", "results").map((v, i) => {
    const w = `experiments[${i}]`;
    const e = obj(v, w);
    return {
      id: str(e, "id", w),
      title: str(e, "title", w),
      status: str(e, "status", w),
      verdict: str(e, "verdict", w),
      estimates: arr(e, "estimates", w).map((x, j) => estimate(x, `${w}.estimates[${j}]`)),
      claim_ids: strArr(e, "claim_ids", w),
      report_path: str(e, "report_path", w),
      notes: strArr(e, "notes", w),
    };
  });
  if (experiments.length === 0) throw new ResultsError("results.experiments: empty");
  return {
    schema: SCHEMA,
    schema_version: version,
    project: str(o, "project", "results"),
    question: str(o, "question", "results"),
    status_label: str(o, "status_label", "results"),
    code_revision: str(o, "code_revision", "results"),
    sources: arr(o, "sources", "results").map((v, i) => {
      const s = obj(v, `sources[${i}]`);
      const sha = str(s, "sha256", `sources[${i}]`);
      if (!/^[0-9a-f]{64}$/.test(sha)) throw new ResultsError(`sources[${i}].sha256: not a sha256`);
      return { path: str(s, "path", `sources[${i}]`), sha256: sha };
    }),
    experiments,
    assumptions: arr(o, "assumptions", "results").map((v, i) => {
      const a = obj(v, `assumptions[${i}]`);
      return {
        name: str(a, "name", `assumptions[${i}]`),
        value: str(a, "value", `assumptions[${i}]`),
        source: str(a, "source", `assumptions[${i}]`),
      };
    }),
    limitations: strArr(o, "limitations", "results"),
    explorer: explorer(o.explorer),
    real_score: realScore(o.real_score),
    display_exceptions: exceptions(o.display_exceptions),
  };
}

function bool(o: Obj, k: string, where: string): boolean {
  if (typeof o[k] !== "boolean") throw new ResultsError(`${where}.${k}: expected a boolean`);
  return o[k] as boolean;
}

function value(v: unknown, where: string): Value {
  const o = obj(v, where);
  const x = {
    estimate: num(o, "estimate", where) as number,
    ci_low: num(o, "ci_low", where) as number,
    ci_high: num(o, "ci_high", where) as number,
    display: str(o, "display", where),
  };
  if (x.ci_low > x.ci_high) throw new ResultsError(`${where}: ci_low exceeds ci_high`);
  if (x.estimate < x.ci_low - 1e-9 || x.estimate > x.ci_high + 1e-9) {
    throw new ResultsError(`${where}: estimate outside its interval`);
  }
  return x;
}

function policies(v: unknown, where: string): PolicyBlock[] {
  const list = (Array.isArray(v) ? v : (() => { throw new ResultsError(`${where}: expected an array`); })()).map(
    (p, i) => {
      const w = `${where}[${i}]`;
      const o = obj(p, w);
      const g = obj(o.gaps, `${w}.gaps`);
      const gaps: Record<string, Value> = {};
      for (const k of GAP_KEYS) gaps[k] = value(g[k], `${w}.gaps.${k}`);
      const policy = str(o, "policy", w);
      const util = o.utility_vs_p0 === null ? null : value(o.utility_vs_p0, `${w}.utility_vs_p0`);
      if ((policy === "P0") !== (util === null)) throw new ResultsError(`${w}.utility_vs_p0: null only for P0`);
      return {
        policy, name: str(o, "name", w), gaps,
        tpr_a: value(o.tpr_a, `${w}.tpr_a`), tpr_b: value(o.tpr_b, `${w}.tpr_b`),
        within_2pp_all_three: bool(o, "within_2pp_all_three", w), utility_vs_p0: util,
      };
    },
  );
  if (list.map((p) => p.policy).join() !== POLICY_IDS.join()) {
    throw new ResultsError(`${where}: expected policies ${POLICY_IDS.join(", ")} in order`);
  }
  return list;
}

function explorer(v: unknown): Explorer {
  const w = "explorer";
  const o = obj(v, w);
  const deltas = arr(o, "deltas", w).map((d, i) => num({ d }, "d", `${w}.deltas[${i}]`) as number);
  const rhos = arr(o, "rhos", w).map((d, i) => num({ d }, "d", `${w}.rhos[${i}]`) as number);
  const cells = arr(o, "cells", w).map((c, i) => {
    const cw = `${w}.cells[${i}]`;
    const co = obj(c, cw);
    return { cell_id: str(co, "cell_id", cw), delta: num(co, "delta", cw) as number, rho: num(co, "rho", cw) as number,
             policies: policies(co.policies, `${cw}.policies`) };
  });
  if (deltas.length === 0 || rhos.length === 0 || cells.length !== deltas.length * rhos.length) {
    throw new ResultsError(`${w}.cells: expected one cell per delta and rho`);
  }
  for (const d of deltas) for (const r of rhos) {
    if (!cells.some((c) => c.delta === d && c.rho === r)) throw new ResultsError(`${w}: missing cell ${d}, ${r}`);
  }
  const metrics = arr(o, "metrics", w).map((m, i) => {
    const mo = obj(m, `${w}.metrics[${i}]`);
    return { key: str(mo, "key", `${w}.metrics[${i}]`), label: str(mo, "label", `${w}.metrics[${i}]`) };
  });
  if (metrics.map((m) => m.key).join() !== GAP_KEYS.join()) throw new ResultsError(`${w}.metrics: unexpected keys`);
  return { experiment_id: str(o, "experiment_id", w), label: str(o, "label", w), unit: str(o, "unit", w),
           tolerance_pp: num(o, "tolerance_pp", w) as number, source: str(o, "source", w), metrics, deltas, rhos, cells };
}

function realScore(v: unknown): RealScore {
  const w = "real_score";
  const o = obj(v, w);
  const cells = arr(o, "cells", w).map((c, i) => {
    const cw = `${w}.cells[${i}]`;
    const co = obj(c, cw);
    return { cell_id: str(co, "cell_id", cw), description: str(co, "description", cw),
             policies: policies(co.policies, `${cw}.policies`) };
  });
  if (cells.length === 0) throw new ResultsError(`${w}.cells: empty`);
  return { experiment_id: str(o, "experiment_id", w), label: str(o, "label", w), unit: str(o, "unit", w),
           tolerance_pp: num(o, "tolerance_pp", w) as number, source: str(o, "source", w), cells };
}

function exceptions(v: unknown): Record<string, string> {
  const o = obj(v, "display_exceptions");
  const out: Record<string, string> = {};
  for (const k of Object.keys(o)) out[k] = str(o, k, "display_exceptions");
  return out;
}

export async function loadResults(url = "./data/results.json"): Promise<Results> {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new ResultsError(`could not load ${url} (HTTP ${res.status})`);
  let raw: unknown;
  try {
    raw = await res.json();
  } catch {
    throw new ResultsError(`${url} is not valid JSON`);
  }
  return validateResults(raw);
}

/** Formats a number for display without inventing precision. */
export function fmt(x: number, digits = 3): string {
  if (Number.isInteger(x)) return x.toString();
  return Number(x.toPrecision(digits)).toString();
}

export function fmtEstimate(e: Estimate, digits = 3): string {
  return e.display ?? `${fmt(e.estimate, digits)}${e.unit ? " " + e.unit : ""}`;
}

export function fmtInterval(e: Estimate, digits = 3): string {
  if (e.interval_display !== null) return e.interval_display;
  if (e.ci_low === null || e.ci_high === null) return "no interval";
  const level = e.ci_level === null ? "" : `${Math.round(e.ci_level * 100)}% `;
  return `${level}[${fmt(e.ci_low, digits)}, ${fmt(e.ci_high, digits)}]`;
}
