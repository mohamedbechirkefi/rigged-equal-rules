// SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
// Hero illustration: two score distributions on a measuring rule and one cut line that slides into
// place. It is an illustration, not study data: the curves are drawn shapes, the rule has no numerals,
// and it reads no result file. Motion: Web Animations API on transform, opacity and clip-path only;
// with reduced motion the final frame is shown at once.
import { useEffect, useRef } from "react";
import { prefersReducedMotion } from "./motion";

const W = 720;
const H = 250;
const BASE = 176; // baseline of the curves, top edge of the rule
const X0 = 40;
const X1 = W - 40;
const SIGMA = 74;
const MU_A = 400;
const MU_B = 330; // Group B starts lower: an illustrative shift, not a study value
const CUT = 470; // illustrative cut position
const PEAK = 118;

function curve(mu: number): string {
  const pts: string[] = [];
  for (let x = X0; x <= X1; x += 6) {
    const y = BASE - PEAK * Math.exp(-0.5 * ((x - mu) / SIGMA) ** 2);
    pts.push(`${x},${y.toFixed(1)}`);
  }
  return pts.join(" ");
}
const lineD = (mu: number) => `M${curve(mu).split(" ").join(" L")}`;
const areaD = (mu: number) => `M${X0},${BASE} L${curve(mu).split(" ").join(" L")} L${X1},${BASE} Z`;
const ticks = Array.from({ length: Math.floor((X1 - X0) / 16) + 1 }, (_, i) => X0 + i * 16);

export function HeroRule() {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const replayRef = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    const svg = svgRef.current;
    const replay = replayRef.current;
    if (!svg || !replay) return;
    const q = <T extends Element>(sel: string) => [...svg.querySelectorAll<T>(sel)];
    const anims: Animation[] = [];
    const ease = "cubic-bezier(0.23, 1, 0.32, 1)";
    const clipFrom = "inset(0 0 0 100%)";
    // clip-path insets are relative to the fill's own box, which spans X0 to X1
    const clipTo = `inset(0 0 0 ${(((CUT - X0) / (X1 - X0)) * 100).toFixed(2)}%)`;

    const finalFrame = () => {
      anims.forEach((a) => a.cancel());
      anims.length = 0;
      for (const el of q<SVGElement>(".hr-curve, .hr-key, .hr-sel-label")) el.style.opacity = "1";
      for (const el of q<SVGElement>(".hr-curve")) el.style.transform = "none";
      for (const el of q<SVGElement>(".hr-fill")) el.style.clipPath = clipTo;
      const cut = svg.querySelector<SVGElement>(".hr-cut");
      if (cut) cut.style.transform = "translateX(0px)";
    };
    const play = () => {
      anims.forEach((a) => a.cancel());
      anims.length = 0;
      const add = (el: Element, k: Keyframe[], o: KeyframeAnimationOptions) => anims.push(el.animate(k, { fill: "both", ...o }));
      q(".hr-curve").forEach((el, i) =>
        add(el, [{ opacity: 0, transform: "scaleY(0.2)" }, { opacity: 1, transform: "scaleY(1)" }], { duration: 700, delay: 150 + i * 80, easing: ease }));
      q(".hr-key").forEach((el, i) => add(el, [{ opacity: 0 }, { opacity: 1 }], { duration: 300, delay: 700 + i * 60, easing: ease }));
      const cut = svg.querySelector(".hr-cut");
      if (cut) add(cut, [{ transform: `translateX(${X1 - CUT + 30}px)` }, { transform: "translateX(0px)" }], { duration: 1500, delay: 1000, easing: ease });
      q(".hr-fill").forEach((el) => add(el, [{ clipPath: clipFrom }, { clipPath: clipTo }], { duration: 1500, delay: 1000, easing: ease }));
      q(".hr-sel-label").forEach((el) => add(el, [{ opacity: 0 }, { opacity: 1 }], { duration: 320, delay: 2300, easing: ease }));
    };
    const onReplay = () => (prefersReducedMotion() ? finalFrame() : play());
    replay.addEventListener("click", onReplay);
    if (prefersReducedMotion()) finalFrame();
    else play();
    return () => {
      replay.removeEventListener("click", onReplay);
      anims.forEach((a) => a.cancel());
    };
  }, []);

  return (
    <figure className="hero-rule">
      <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} role="img"
        aria-label="Illustration, not study data: two score distributions on a measuring rule. Group A's curve sits to the right of Group B's. One cut line is applied to both, and only the part of each curve to the right of the line is selected, a larger share of Group A than of Group B.">
        <g className="hr-fill hr-a"><path d={areaD(MU_A)} /></g>
        <g className="hr-fill hr-b"><path d={areaD(MU_B)} /></g>
        <path className="hr-curve hr-a" d={lineD(MU_A)} />
        <path className="hr-curve hr-b" d={lineD(MU_B)} />
        <g className="hr-key hr-a" transform={`translate(${MU_A - 36} ${BASE - PEAK - 14})`}>
          <circle r={7} /><text x={14} y={5} className="long">Group A</text><text x={14} y={8} className="short">A</text>
        </g>
        <g className="hr-key hr-b" transform={`translate(${MU_B - 112} ${BASE - PEAK - 14})`}>
          <rect x={-7} y={-7} width={14} height={14} /><text x={14} y={5} className="long">Group B</text><text x={14} y={8} className="short">B</text>
        </g>
        <g className="hr-rule">
          <rect x={X0 - 14} y={BASE} width={X1 - X0 + 28} height={40} rx={5} />
          {ticks.map((t, i) => <line key={t} x1={t} x2={t} y1={BASE} y2={BASE + (i % 5 === 0 ? 18 : 10)} />)}
          <text x={X0} y={BASE + 33} className="long">lower score</text>
          <text x={X1} y={BASE + 33} textAnchor="end" className="long">higher score</text>
          <text x={X0} y={BASE + 66} className="short">lower</text>
          <text x={X1} y={BASE + 66} textAnchor="end" className="short">higher</text>
        </g>
        <g className="hr-cut">
          <line x1={CUT} x2={CUT} y1={22} y2={BASE + 40} />
          <text className="hr-sel-label long" x={CUT + 12} y={34}>selected, one rule for both</text>
          <text className="hr-sel-label short" x={CUT + 14} y={44}>selected</text>
        </g>
      </svg>
      <div className="hero-rule-foot">
        <span className="illus-tag">Illustration, not study data</span>
        <button type="button" ref={replayRef} className="ghost">Replay illustration</button>
      </div>
    </figure>
  );
}
