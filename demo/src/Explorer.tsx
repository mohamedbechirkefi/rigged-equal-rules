// SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
// Fairness trade-off explorer and subgroup outcome charts (roadmap M5), drawn from the published
// results only: EXP-002 (simulated grid) and EXP-004 (real score). No visitor input changes a number.
import { useLayoutEffect, useRef, useState, type ReactNode } from "react";
import { domainOf, GapChart, SubgroupChart } from "./charts";
import { useReveal } from "./motion";
import { GAP_KEYS, type PolicyBlock, type Results } from "./results";

type Scenario = "synthetic" | "real";

const METRIC_HELP: Record<string, string> = {
  sr_gap: "selection rate, A minus B",
  eog: "true positive rate, A minus B (primary metric)",
  ppv_gap: "precision among the selected, A minus B",
  fpr_gap: "false positive rate, A minus B",
};

/** A segmented group whose pressed button carries a sliding indicator (transform only). */
function Seg({ label, children, dep }: { label: string; children: ReactNode; dep: string }) {
  const ref = useRef<HTMLDivElement | null>(null);
  const marker = useRef<HTMLSpanElement | null>(null);
  useLayoutEffect(() => {
    const wrap = ref.current, m = marker.current;
    if (!wrap || !m) return;
    const place = () => {
      const on = wrap.querySelector<HTMLButtonElement>('button[aria-pressed="true"]');
      if (!on) return;
      m.style.transform = `translate(${on.offsetLeft}px, ${on.offsetTop - 5}px) scaleX(${on.offsetWidth / 100})`;
    };
    place();
    const ro = new ResizeObserver(() => { m.classList.add("still"); place(); requestAnimationFrame(() => m.classList.remove("still")); });
    ro.observe(wrap);
    return () => ro.disconnect();
  }, [dep]);
  return (
    <div className="seg slide" role="group" aria-label={label} ref={ref}>
      <span className="seg-ind" aria-hidden="true" ref={marker} />
      {children}
    </div>
  );
}

export function Explorer({ r }: { r: Results }) {
  const ex = r.explorer;
  const [scenario, setScenario] = useState<Scenario>("synthetic");
  const [cellId, setCellId] = useState("d0.50-r1.00");
  const [realId, setRealId] = useState(r.real_score.cells[0].cell_id);

  const synthetic = ex.cells.find((c) => c.cell_id === cellId) ?? ex.cells[0];
  const real = r.real_score.cells.find((c) => c.cell_id === realId) ?? r.real_score.cells[0];
  const blocks: PolicyBlock[] = scenario === "synthetic" ? synthetic.policies : real.policies;
  const tol = scenario === "synthetic" ? ex.tolerance_pp : r.real_score.tolerance_pp;
  const domain = domainOf(blocks.flatMap((b) => GAP_KEYS.map((k) => b.gaps[k])), tol);
  const where = scenario === "synthetic"
    ? `EXP-002, cell ${synthetic.cell_id} (delta ${synthetic.delta}, rho ${synthetic.rho})`
    : `EXP-004, cell ${real.cell_id}: ${real.description}`;
  const p0 = (id: string) => ex.cells.find((c) => c.cell_id === id)!.policies[0].gaps.eog.display;
  const panelsRef = useReveal<HTMLDivElement>();
  const subRef = useReveal<HTMLDivElement>();

  return (
    <section id="explorer" aria-labelledby="h-explorer">
      <h2 id="h-explorer">Fairness trade-off explorer</h2>
      <p>
        Pick a scenario and a cell. Each panel shows one gap between Group A and Group B for the four rules, as
        a seed mean with its 95% bootstrap interval. The shaded band is the 2 pp tolerance used by the frozen
        rule. A rule meets a criterion when its gap sits inside the band.
      </p>
      <p>
        <span className="tag tag-measured">Measured</span>{" "}
        <span className="meta">
          {scenario === "synthetic" ? ex.label : r.real_score.label}; source <code>{scenario === "synthetic" ? ex.source : r.real_score.source}</code>
        </span>
      </p>

      <Seg label="Scenario" dep={scenario}>
        <button type="button" aria-pressed={scenario === "synthetic"} onClick={() => setScenario("synthetic")}>
          Synthetic grid (EXP-002, simulated)
        </button>
        <button type="button" aria-pressed={scenario === "real"} onClick={() => setScenario("real")}>
          Real score (EXP-004, UCI Adult)
        </button>
      </Seg>

      {scenario === "synthetic" ? (
        <div className="grid-picker">
          <p className="meta" id="grid-help">
            Rows: starting-distribution gap delta. Columns: noise ratio rho. Each button shows the measured P0
            (one raw threshold) EOG in pp with its interval.
          </p>
          <table className="picker" aria-describedby="grid-help">
            <thead>
              <tr>
                <th scope="col">delta \ rho</th>
                {ex.rhos.map((rho) => <th scope="col" key={rho}>{rho}</th>)}
              </tr>
            </thead>
            <tbody>
              {ex.deltas.map((d) => (
                <tr key={d}>
                  <th scope="row">{d}</th>
                  {ex.rhos.map((rho) => {
                    const c = ex.cells.find((x) => x.delta === d && x.rho === rho)!;
                    return (
                      <td key={rho}>
                        <button type="button" aria-pressed={c.cell_id === cellId} onClick={() => setCellId(c.cell_id)}
                          aria-label={`delta ${d}, rho ${rho}: P0 EOG ${p0(c.cell_id)} pp`}>
                          {p0(c.cell_id)}
                        </button>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <Seg label="EXP-004 cell" dep={realId}>
          {r.real_score.cells.map((c) => (
            <button type="button" key={c.cell_id} aria-pressed={c.cell_id === realId} onClick={() => setRealId(c.cell_id)}>
              {c.cell_id}
            </button>
          ))}
        </Seg>
      )}

      <h3 className="where">{where}</h3>
      <ul className="rules">
        {blocks.map((b) => <li key={b.policy}>{b.name}</li>)}
      </ul>
      <div className="panels" ref={panelsRef}>
        {ex.metrics.map((m) => (
          <GapChart key={m.key} title={`${m.label}: ${METRIC_HELP[m.key]}`} unit="pp" tol={tol} domain={domain}
            rows={blocks.map((b) => ({ label: b.policy, value: b.gaps[m.key] }))} />
        ))}
      </div>
      <p className="meta">
        Positive values mean Group B fares worse on that criterion. The EOG is one criterion among several; no
        metric here is presented as universal.
      </p>

      <p className="meta table-note">Gaps in pp, seed mean [95% bootstrap interval]. "All 3": SR, EO and PPV seed means within 2 pp.</p>
      <div className="table-scroll" role="region" aria-label="Gaps by rule, exact values" tabIndex={0}>
        <table className="values">
          <thead>
            <tr>
              <th scope="col">Rule</th>
              {ex.metrics.map((m) => <th scope="col" key={m.key}>{m.label}</th>)}
              <th scope="col">All 3 within 2 pp</th>
            </tr>
          </thead>
          <tbody>
            {blocks.map((b) => (
              <tr key={b.policy}>
                <th scope="row">{b.policy}</th>
                {GAP_KEYS.map((k) => <td key={k}>{b.gaps[k].display}</td>)}
                <td>{b.within_2pp_all_three ? "yes" : "no"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h3>Subgroup outcomes</h3>
      <div ref={subRef}><SubgroupChart blocks={blocks} /></div>
      <p className="meta">
        Plain-language reading: for each rule, the circle is the share of qualified Group A members who are
        selected and the square is the same share for Group B. The distance between them is the EOG. Group
        rates are seed means from the same summary table; the manuscript prints their difference, not the rates
        themselves.
      </p>
      <p className="meta table-note">Share of qualified members selected, % [95% bootstrap interval]; utility per capita relative to P0</p>
      <div className="table-scroll" role="region" aria-label="Subgroup outcomes, exact values" tabIndex={0}>
        <table className="values">
          <thead>
            <tr><th scope="col">Rule</th><th scope="col">Group A</th><th scope="col">Group B</th><th scope="col">EOG (pp)</th><th scope="col">Utility minus P0</th></tr>
          </thead>
          <tbody>
            {blocks.map((b) => (
              <tr key={b.policy}>
                <th scope="row">{b.policy}</th>
                <td>{b.tpr_a.display}</td>
                <td>{b.tpr_b.display}</td>
                <td>{b.gaps.eog.display}</td>
                <td>{b.utility_vs_p0 ? b.utility_vs_p0.display : "reference"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
