// SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
// Visitor sandbox: runs the engine port in a Web Worker on the sandbox's own random numbers. Its output
// is labelled as sandbox output and never mixed with the published results. Nothing is stored or sent.
import { useEffect, useRef, useState } from "react";
import type { PolicySummary, WorkerReply, WorkerRequest } from "./sandbox.worker";
import { checkParams, LIMITS, type SandboxParams } from "./sandboxParams";

const DEFAULTS: SandboxParams = { delta: 0.5, rho: 1, kappa: 0.3, p_b: 0.5, seed: 1, seeds: 5, n: 5000 };
const PRESETS: { id: string; label: string; p: Partial<SandboxParams> }[] = [
  { id: "primary", label: "Unequal starting distributions (delta 0.5, rho 1)", p: { delta: 0.5, rho: 1 } },
  { id: "control", label: "Equal distributions (delta 0, rho 1)", p: { delta: 0, rho: 1 } },
  { id: "noise", label: "Noisier measurement of Group B (delta 0, rho 2)", p: { delta: 0, rho: 2 } },
  { id: "both", label: "Both (delta 1, rho 2)", p: { delta: 1, rho: 2 } },
];
const ROWS: [string, string, number, number][] = [
  ["sr_gap", "SR gap (pp)", 100, 2], ["eog", "EOG (pp)", 100, 2], ["ppv_gap", "PPV gap (pp)", 100, 2],
  ["fpr_gap", "FPR gap (pp)", 100, 2], ["tpr_a", "TPR, Group A (%)", 100, 1], ["tpr_b", "TPR, Group B (%)", 100, 1],
  ["utility_per_capita", "Utility per capita", 1, 4],
];

type Out = { kind: "idle" } | { kind: "running"; fraction: number } | { kind: "done"; params: SandboxParams; summary: PolicySummary[] }
  | { kind: "message"; text: string };

function NumberField({ id, label, value, min, max, step, onChange, help }: {
  id: string; label: string; value: number; min: number; max: number; step: number; help: string;
  onChange: (v: number) => void;
}) {
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <input id={id} type="number" min={min} max={max} step={step} value={value} aria-describedby={`${id}-h`}
        onChange={(e) => onChange(e.target.value === "" ? NaN : Number(e.target.value))} />
      <span id={`${id}-h`} className="meta">{help}</span>
    </div>
  );
}

export function Sandbox() {
  const worker = useRef<Worker | null>(null);
  const [p, setP] = useState<SandboxParams>(DEFAULTS);
  const [preset, setPreset] = useState("primary");
  const [out, setOut] = useState<Out>({ kind: "idle" });
  const [download, setDownload] = useState<string | null>(null);

  useEffect(() => {
    const w = new Worker(new URL("./sandbox.worker.ts", import.meta.url), { type: "module" });
    w.onmessage = (ev: MessageEvent<WorkerReply>) => {
      const m = ev.data;
      if (m.type === "progress") setOut({ kind: "running", fraction: m.fraction });
      if (m.type === "done") setOut({ kind: "done", params: m.params, summary: m.summary });
      if (m.type === "error") setOut({ kind: "message", text: `The sandbox could not run: ${m.message}.` });
      if (m.type === "cancelled") setOut({ kind: "message", text: "Sandbox run cancelled. No output." });
    };
    worker.current = w;
    return () => w.terminate();
  }, []);

  useEffect(() => {
    if (out.kind !== "done") {
      setDownload(null);
      return;
    }
    const blob = new Blob([JSON.stringify({ label: "RIGGED sandbox output, not a research result", ...out }, null, 1)],
      { type: "application/json" });
    const url = URL.createObjectURL(blob);
    setDownload(url);
    return () => URL.revokeObjectURL(url);
  }, [out]);

  const invalid = checkParams(p);
  const running = out.kind === "running";
  const set = (k: keyof SandboxParams) => (v: number) => setP((q) => ({ ...q, [k]: v }));
  const run = () => {
    if (invalid) return;
    setOut({ kind: "running", fraction: 0 });
    worker.current?.postMessage({ type: "run", params: p } satisfies WorkerRequest);
  };
  const cancel = () => worker.current?.postMessage({ type: "cancel" } satisfies WorkerRequest);
  const reset = () => {
    if (running) cancel();
    setP(DEFAULTS);
    setPreset("primary");
    setOut({ kind: "idle" });
  };
  const choosePreset = (id: string) => {
    setPreset(id);
    const pr = PRESETS.find((x) => x.id === id);
    if (pr) setP((q) => ({ ...q, ...pr.p }));
  };

  const fmt = (v: number | null, scale: number, d: number) => (v === null ? "undefined" : (v * scale).toFixed(d));
  const live =
    out.kind === "done"
      ? `Sandbox output ready: ${out.params.seeds} seed(s) from seed ${out.params.seed}, n ${out.params.n}. P0 EOG ${fmt(out.summary[0].mean.eog, 100, 2)} pp.`
      : out.kind === "message" ? out.text : "";

  return (
    <section id="sandbox" aria-labelledby="h-sandbox" className="sandbox">
      <h2 id="h-sandbox">Sandbox <span className="tag tag-sandbox">Sandbox output</span></h2>
      <p>
        The sandbox runs a port of the research engine in your browser: the Gaussian generator, the rules P0 to
        P3 and the metrics. On identical random draws it reproduces the Python engine (automated test, tolerance
        1e-9 on every metric). Its random numbers come from a different generator, so a sandbox seed does not
        reproduce a research seed, and its output is <strong>not a research result</strong>. It is not
        comparable to the published numbers above and is never mixed with them.
      </p>
      <p className="meta">
        Bounded: at most {LIMITS.maxSeeds} seeds of at most 20,000 individuals per population. Nothing you enter
        is stored or sent anywhere.
      </p>

      <div className="field wide">
        <label htmlFor="sb-preset">Scenario</label>
        <select id="sb-preset" value={preset} onChange={(e) => choosePreset(e.target.value)}>
          {PRESETS.map((x) => <option key={x.id} value={x.id}>{x.label}</option>)}
          <option value="custom">Custom (edit below)</option>
        </select>
      </div>
      <div className="controls">
        <NumberField id="sb-delta" label="delta" value={p.delta} min={0} max={2} step={0.05} onChange={(v) => { setPreset("custom"); set("delta")(v); }}
          help="Group B's latent mean is minus delta" />
        <NumberField id="sb-rho" label="rho" value={p.rho} min={0.5} max={3} step={0.1} onChange={(v) => { setPreset("custom"); set("rho")(v); }}
          help="Group B's noise SD is 0.5 rho" />
        <NumberField id="sb-kappa" label="kappa" value={p.kappa} min={0.05} max={0.95} step={0.05} onChange={set("kappa")}
          help="share selected" />
        <NumberField id="sb-pb" label="p_B" value={p.p_b} min={0.05} max={0.95} step={0.05} onChange={set("p_b")}
          help="share in Group B" />
        <NumberField id="sb-n" label="n" value={p.n} min={LIMITS.minN} max={LIMITS.maxN} step={1000} onChange={set("n")}
          help="per population" />
        <NumberField id="sb-seed" label="first seed" value={p.seed} min={1} max={1_000_000} step={1} onChange={set("seed")}
          help="sandbox seed" />
        <NumberField id="sb-seeds" label="seeds" value={p.seeds} min={1} max={LIMITS.maxSeeds} step={1} onChange={set("seeds")}
          help="1 to 10" />
      </div>
      <div className="controls buttons">
        <button type="button" className="primary" onClick={run} disabled={running || invalid !== null}>Run sandbox</button>
        <button type="button" onClick={cancel} disabled={!running}>Cancel</button>
        <button type="button" onClick={reset}>Reset</button>
      </div>
      {invalid && <p className="warn" role="status">Settings out of range: {invalid}.</p>}
      <div className={`run-rail${running ? " running" : ""}`} aria-hidden="true"><span /></div>
      {running && (
        <p className="meta">
          Working: <progress max={1} value={out.fraction} aria-label="Sandbox progress" /> {Math.round(out.fraction * 100)}%
        </p>
      )}
      <p aria-live="polite" className="sandbox-out">{live}</p>

      {out.kind === "idle" && <p className="meta">No sandbox output yet. Choose settings and press Run sandbox.</p>}
      {out.kind === "done" && (
        <>
          <p className="meta table-note">Sandbox output, not a research result: mean over {out.params.seeds} sandbox seed(s)
                {out.params.seeds > 1 ? ", with the SD across those seeds in brackets (not a confidence interval)" : ""}.
                Settings: delta {out.params.delta}, rho {out.params.rho}, kappa {out.params.kappa}, p_B {out.params.p_b}, n {out.params.n}.</p>
          <div className="table-scroll" role="region" aria-label="Sandbox output table" tabIndex={0}>
            <table className="sandbox-table values">
              <thead>
                <tr>
                  <th scope="col">Quantity</th>
                  {out.summary.map((s) => <th scope="col" key={s.policy}>{s.policy}</th>)}
                </tr>
              </thead>
              <tbody>
                {ROWS.map(([k, label, scale, d]) => (
                  <tr key={k}>
                    <th scope="row">{label}</th>
                    {out.summary.map((s) => (
                      <td key={s.policy}>
                        {fmt(s.mean[k], scale, d)}
                        {s.sd[k] !== null ? ` (SD ${fmt(s.sd[k], scale, d)})` : ""}
                      </td>
                    ))}
                  </tr>
                ))}
                <tr>
                  <th scope="row">Seeds fitted</th>
                  {out.summary.map((s) => <td key={s.policy}>{s.runs_ok} of {out.params.seeds}</td>)}
                </tr>
              </tbody>
            </table>
          </div>
          {out.summary.some((s) => s.not_fitted.length > 0) && (
            <ul className="meta">
              {out.summary.flatMap((s) => s.not_fitted.map((t) => <li key={s.policy + t}>{s.policy} could not be fitted ({t}).</li>))}
            </ul>
          )}
          {download && (
            <p><a href={download} download="rigged-sandbox-output.json">Save this sandbox output as JSON</a></p>
          )}
        </>
      )}
    </section>
  );
}
