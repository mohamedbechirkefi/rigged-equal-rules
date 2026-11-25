<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# demo/

Static interactive page for RIGGED (M5): the published results, a fairness trade-off explorer and subgroup outcome charts, the assumptions, the method and limitations, and a sandbox. Built from the shared lab template (TypeScript, React and Vite, pinned versions, `package-lock.json`).

- **Published results** come only from `public/data/results.json`, written by `scripts/export_demo_data.py` from committed tables (schema `lab-demo-results` 1.0.0, extended with `explorer`, `real_score` and `display_exceptions`). The page validates the file and fails closed: any malformed field shows an error panel and no numbers. Every displayed number is the manuscript's own text (6.59 pp [6.20, 6.97] for EXP-001, -7.45 pp [-8.75, -6.05] for EXP-004), checked by `tests/test_demo_export.py`.
- **Explorer**: the 12 EXP-002 cells (simulated) and the two EXP-004 cells (real data), four gap panels with the 2 pp band, and Group A and Group B true positive rates, all with 95% bootstrap intervals.
- **Sandbox**: `src/engine.ts` ports the Gaussian generator, the rules P0 to P3 and the metrics; `src/engine.test.ts` checks it against a fixture from the Python engine (`scripts/make_demo_fixture.py`) on identical draws, with counts exactly equal and every metric within 1e-9. The sandbox draws its own random numbers (mulberry32 and Box-Muller), so its output does not reproduce research seeds; it is labelled "Sandbox output" and is not a research result. Bounded to 10 seeds of 20,000 individuals, cancellable, in a Web Worker.
- **Privacy and offline**: no request leaves the page's origin, nothing about visitors is collected or stored, and the page works offline after the first load.

Commands (Node 22; from this folder):

```
npm ci && npm run build && npm run preview
npm test                                        # vitest: validator and engine port
node tools/a11y_check.mjs dist --screenshots <dir>   # offline and accessibility check
```

Demo URL: `<demo URL, not yet published>`.
