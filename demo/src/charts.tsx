// SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
// Hand-written SVG charts drawn from the exported results. Every number printed next to a chart
// comes from the export's display strings; the charts only position marks.
import { useEffect, useRef, useState } from "react";
import type { PolicyBlock, Value } from "./results";

/** Width of the chart's container in CSS pixels, so that SVG text keeps its real size at any width. */
function useWidth(fallback: number) {
  const ref = useRef<HTMLElement | null>(null);
  const [w, setW] = useState(fallback);
  useEffect(() => {
    const el = ref.current;
    if (!el || typeof ResizeObserver === "undefined") return;
    const ro = new ResizeObserver((entries) => {
      const cw = Math.floor(entries[0].contentRect.width);
      if (cw > 0) setW(cw);
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  return [ref, w] as const;
}

export interface Row {
  label: string;
  value: Value;
}

function niceTicks(lo: number, hi: number, target = 5): number[] {
  const span = hi - lo;
  const raw = span / target;
  const mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => span / s <= target + 1) ?? 10 * mag;
  const out: number[] = [];
  for (let t = Math.ceil(lo / step) * step; t <= hi + 1e-9; t += step) out.push(Number(t.toFixed(6)));
  return out;
}

export function domainOf(values: Value[], pad: number, clamp?: [number, number]): [number, number] {
  let lo = Math.min(...values.map((v) => v.ci_low), -pad);
  let hi = Math.max(...values.map((v) => v.ci_high), pad);
  const m = (hi - lo) * 0.06;
  lo -= m;
  hi += m;
  if (clamp) {
    lo = Math.max(lo, clamp[0]);
    hi = Math.min(hi, clamp[1]);
  }
  return [lo, hi];
}

const LEFT = 34;
const RIGHT = 12;
const ROW = 26;
const TOP = 8;
const AXIS = 30;

/** Dot-and-interval chart of one gap metric for each policy, with the +/- tolerance band. */
export function GapChart({ title, rows, domain, tol, unit }: {
  title: string; rows: Row[]; domain: [number, number]; tol: number; unit: string;
}) {
  const [ref, W] = useWidth(320);
  const h = TOP + rows.length * ROW + AXIS;
  const x = (v: number) => LEFT + ((v - domain[0]) / (domain[1] - domain[0])) * (W - LEFT - RIGHT);
  const ticks = niceTicks(domain[0], domain[1], W < 300 ? 3 : 5);
  const desc = `${title}: ` + rows.map((r) => `${r.label} ${r.value.display}`).join("; ") + ` ${unit}.`;
  return (
    <figure className="chart" ref={ref}>
      <figcaption className="chart-title">{title} <span className="meta">({unit})</span></figcaption>
      <svg viewBox={`0 0 ${W} ${h}`} role="img" aria-label={desc} preserveAspectRatio="xMidYMid meet">
        <rect className="band" x={x(-tol)} y={TOP - 4} width={x(tol) - x(-tol)} height={rows.length * ROW + 4} />
        <line className="zero" x1={x(0)} x2={x(0)} y1={TOP - 4} y2={TOP + rows.length * ROW} />
        {rows.map((r, i) => {
          const cy = TOP + i * ROW + ROW / 2;
          return (
            <g key={r.label}>
              <text className="lbl" x={4} y={cy + 4}>{r.label}</text>
              <line className="whisker" x1={x(r.value.ci_low)} x2={x(r.value.ci_high)} y1={cy} y2={cy} />
              <line className="whisker" x1={x(r.value.ci_low)} x2={x(r.value.ci_low)} y1={cy - 5} y2={cy + 5} />
              <line className="whisker" x1={x(r.value.ci_high)} x2={x(r.value.ci_high)} y1={cy - 5} y2={cy + 5} />
              <circle className="dot" cx={x(r.value.estimate)} cy={cy} r={4.5} />
            </g>
          );
        })}
        <line className="axis" x1={LEFT} x2={W - RIGHT} y1={TOP + rows.length * ROW + 2} y2={TOP + rows.length * ROW + 2} />
        {ticks.map((t) => (
          <g key={t}>
            <line className="axis" x1={x(t)} x2={x(t)} y1={TOP + rows.length * ROW + 2} y2={TOP + rows.length * ROW + 6} />
            <text className="tick" x={x(t)} y={TOP + rows.length * ROW + 20} textAnchor="middle">{t}</text>
          </g>
        ))}
      </svg>
    </figure>
  );
}

/** Subgroup outcomes: share of qualified members selected (TPR) in each group, per policy. */
export function SubgroupChart({ blocks }: { blocks: PolicyBlock[] }) {
  const values = blocks.flatMap((b) => [b.tpr_a, b.tpr_b]);
  const domain = domainOf(values, 0, [0, 100]);
  const [ref, width] = useWidth(640);
  const left = 40;
  const right = 14;
  const row = 34;
  const top = 10;
  const h = top + blocks.length * row + AXIS;
  const x = (v: number) => left + ((v - domain[0]) / (domain[1] - domain[0])) * (width - left - right);
  const ticks = niceTicks(domain[0], domain[1], width < 400 ? 4 : 6);
  const desc = "Share of qualified members selected, by policy: " +
    blocks.map((b) => `${b.policy} Group A ${b.tpr_a.display}, Group B ${b.tpr_b.display}`).join("; ") + ".";
  return (
    <figure className="chart wide" ref={ref}>
      <figcaption className="chart-title">
        Share of qualified members selected (true positive rate, %), with 95% intervals
      </figcaption>
      <p className="legend" aria-hidden="true">
        <span className="key key-a" /> Group A <span className="key key-b" /> Group B
      </p>
      <svg viewBox={`0 0 ${width} ${h}`} role="img" aria-label={desc}>
        {blocks.map((b, i) => {
          const cy = top + i * row + row / 2;
          return (
            <g key={b.policy}>
              <text className="lbl" x={4} y={cy + 4}>{b.policy}</text>
              <line className="link" x1={x(b.tpr_a.estimate)} x2={x(b.tpr_b.estimate)} y1={cy} y2={cy} />
              {([["a", b.tpr_a, -6], ["b", b.tpr_b, 6]] as const).map(([g, v, dy]) => (
                <g key={g} className={`grp-${g}`}>
                  <line className="whisker-g" x1={x(v.ci_low)} x2={x(v.ci_high)} y1={cy + dy} y2={cy + dy} />
                  {g === "a" ? (
                    <circle className="mark" cx={x(v.estimate)} cy={cy + dy} r={5} />
                  ) : (
                    <rect className="mark" x={x(v.estimate) - 4.5} y={cy + dy - 4.5} width={9} height={9} />
                  )}
                </g>
              ))}
            </g>
          );
        })}
        <line className="axis" x1={left} x2={width - right} y1={top + blocks.length * row + 2} y2={top + blocks.length * row + 2} />
        {ticks.map((t) => (
          <g key={t}>
            <line className="axis" x1={x(t)} x2={x(t)} y1={top + blocks.length * row + 2} y2={top + blocks.length * row + 6} />
            <text className="tick" x={x(t)} y={top + blocks.length * row + 20} textAnchor="middle">{t}</text>
          </g>
        ))}
      </svg>
    </figure>
  );
}
