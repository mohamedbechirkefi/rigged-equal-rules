// SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
// Motion helpers. Every effect is skipped under prefers-reduced-motion, and every count-up ends on the
// exact display string from the results file.
import { useEffect, useRef } from "react";

export const prefersReducedMotion = () =>
  typeof window !== "undefined" && typeof window.matchMedia === "function" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/** Adds "in" to the element once it is scrolled into view (CSS does the transition). */
export function useReveal<T extends HTMLElement>() {
  const ref = useRef<T | null>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (prefersReducedMotion() || typeof IntersectionObserver === "undefined") { el.classList.add("in"); return; }
    el.classList.add("reveal");
    const io = new IntersectionObserver((es) => {
      if (es.some((e) => e.isIntersecting)) { el.classList.add("in"); io.disconnect(); }
    }, { rootMargin: "0px 0px -8% 0px" });
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return ref;
}

/** Counts a figure like "6.59 pp" or "-7.45 pp" up from zero once, when in view. */
export function useCountUp<T extends HTMLElement>(text: string) {
  const ref = useRef<T | null>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.textContent = text;
    const m = /^(-?\d+)\.(\d+)(.*)$/.exec(text);
    if (!m || prefersReducedMotion() || typeof IntersectionObserver === "undefined") return;
    const target = Number(`${m[1]}.${m[2]}`), dp = m[2].length, suffix = m[3];
    let raf = 0, timer = 0;
    const io = new IntersectionObserver((es) => {
      if (!es.some((e) => e.isIntersecting)) return;
      io.disconnect();
      const t0 = performance.now(), dur = 900;
      const tick = (now: number) => {
        const k = Math.min(1, (now - t0) / dur), e = 1 - (1 - k) ** 3;
        el.textContent = k < 1 ? `${(target * e).toFixed(dp)}${suffix}` : text;
        if (k < 1) raf = requestAnimationFrame(tick);
      };
      raf = requestAnimationFrame(tick);
      timer = window.setTimeout(() => { cancelAnimationFrame(raf); el.textContent = text; }, dur + 200);
    });
    io.observe(el);
    return () => { io.disconnect(); cancelAnimationFrame(raf); clearTimeout(timer); el.textContent = text; };
  }, [text]);
  return ref;
}
