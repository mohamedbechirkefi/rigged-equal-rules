// SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
// Bounded, cancellable sandbox: runs the engine port (engine.ts) on the sandbox's own random
// numbers. At most 10 seeds of at most 20,000 individuals per population.
import { POLICIES, runCell, sandboxDraws, type Policy } from "./engine";
import { checkParams, type SandboxParams } from "./sandboxParams";

export type { SandboxParams };

export interface PolicySummary {
  policy: Policy;
  runs_ok: number;
  not_fitted: string[];
  mean: Record<string, number | null>;
  sd: Record<string, number | null>;
}

export type WorkerRequest = { type: "run"; params: SandboxParams } | { type: "cancel" };
export type WorkerReply =
  | { type: "progress"; fraction: number }
  | { type: "done"; params: SandboxParams; summary: PolicySummary[] }
  | { type: "cancelled" }
  | { type: "error"; message: string };

const KEYS = ["sr_gap", "eog", "ppv_gap", "fpr_gap", "tpr_a", "tpr_b", "utility_per_capita"] as const;
let cancelled = false;

function stats(xs: number[]): [number | null, number | null] {
  if (xs.length === 0) return [null, null];
  const m = xs.reduce((a, b) => a + b, 0) / xs.length;
  if (xs.length < 2) return [m, null];
  return [m, Math.sqrt(xs.reduce((a, b) => a + (b - m) ** 2, 0) / (xs.length - 1))];
}

async function simulate(p: SandboxParams): Promise<PolicySummary[] | null> {
  const per: Record<string, Record<string, number[]>> = {};
  const notFitted: Record<string, string[]> = {};
  for (const pol of POLICIES) {
    per[pol] = Object.fromEntries(KEYS.map((k) => [k, [] as number[]]));
    notFitted[pol] = [];
  }
  for (let i = 0; i < p.seeds; i++) {
    await new Promise((r) => setTimeout(r, 0)); // let a cancel message in
    if (cancelled) return null;
    const s = p.seed + i;
    const out = runCell(p, sandboxDraws(s, 0, p.n), sandboxDraws(s, 1, p.n));
    for (const o of out) {
      if (!o.ok) {
        notFitted[o.policy].push(`seed ${s}: ${o.reason}`);
        continue;
      }
      for (const k of KEYS) {
        const v = o.metrics[k];
        if (v !== null) per[o.policy][k].push(v);
      }
    }
    postMessage({ type: "progress", fraction: (i + 1) / p.seeds } satisfies WorkerReply);
  }
  return POLICIES.map((pol) => {
    const mean: Record<string, number | null> = {};
    const sd: Record<string, number | null> = {};
    for (const k of KEYS) [mean[k], sd[k]] = stats(per[pol][k]);
    return { policy: pol, runs_ok: p.seeds - notFitted[pol].length, not_fitted: notFitted[pol], mean, sd };
  });
}

onmessage = async (ev: MessageEvent<WorkerRequest>) => {
  const m = ev.data;
  if (m.type === "cancel") {
    cancelled = true;
    return;
  }
  cancelled = false;
  try {
    const bad = checkParams(m.params);
    if (bad) throw new Error(bad);
    const summary = await simulate(m.params);
    postMessage((summary === null ? { type: "cancelled" } : { type: "done", params: m.params, summary }) satisfies WorkerReply);
  } catch (e) {
    postMessage({ type: "error", message: e instanceof Error ? e.message : String(e) } satisfies WorkerReply);
  }
};
