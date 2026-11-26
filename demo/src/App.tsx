// SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
import { useEffect, useState } from "react";
import { Explorer } from "./Explorer";
import { HeroRule } from "./Hero";
import { useCountUp } from "./motion";
import { fmtEstimate, fmtInterval, loadResults, ResultsError, type Experiment, type Results } from "./results";
import { Sandbox } from "./Sandbox";

type State = { kind: "loading" } | { kind: "error"; message: string } | { kind: "ready"; results: Results };

const KIND_LABEL: Record<string, string> = {
  measured: "measured",
  analytic: "population value (numerical integration)",
  descriptive: "descriptive, no resampling",
};

export function App() {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    loadResults()
      .then((results) => setState({ kind: "ready", results }))
      .catch((e: unknown) =>
        setState({ kind: "error", message: e instanceof ResultsError ? e.message : "results could not be loaded" }),
      );
  }, []);

  useSectionSpy(state.kind === "ready");

  return (
    <>
      <a className="skip" href="#main">Skip to content</a>
      <header className="bar">
        <div className="bar-in">
          <a className="brand" href="#top" aria-label="Rigged, back to the top">
            <img src="./brand/rigged-mark.svg" alt="" width="30" height="30" /><span>Rigged</span>
          </a>
          <nav aria-label="Sections">
            <a href="#overview">Overview</a>
            <a href="#explorer">Explorer</a>
            <a href="#results">Results</a>
            <a href="#assumptions">Assumptions</a>
            <a href="#method">Method and limitations</a>
            <a href="#sandbox">Sandbox</a>
          </nav>
        </div>
      </header>
      <div className="desk" id="top">
        <article className="letter hero-letter" aria-labelledby="h-question">
          <div className="letterhead">
            <p className="lh-title">Results letter</p>
            <p>A pre-registered simulation study with one real-score test</p>
          </div>
          <h1 id="h-question"><span className="re">Re:</span> Can equal rules yield unequal outcomes under different starting distributions?</h1>
          {state.kind === "ready" ? <Answer r={state.results} /> : (
            <p className="answer">{state.kind === "error" ? "The published results file failed validation, so no measured answer is shown." : "Loading the measured answer."}</p>
          )}
          <HeroRule />
          <p className="postscript">
            <strong>P.S. Claims boundary.</strong> Groups A and B are abstract groups, never protected groups. Nothing
            here is a claim about real hiring or any real selection decision, about workers or about the people in
            the data. The EOG is one criterion among several; no fairness metric is presented as universal.
          </p>
        </article>
      </div>
      <main id="main" className="wrap">
        {state.kind === "loading" && <p role="status">Loading the published results.</p>}
        {state.kind === "error" && (
          <div role="alert" className="panel error">
            <h2>Results unavailable</h2>
            <p>The published results file failed validation, so no numbers are shown.</p>
            <p><code>{state.message}</code></p>
          </div>
        )}
        {state.kind === "ready" && <Published r={state.results} />}
        <Sandbox />
      </main>
      <footer className="site">
        <div className="wrap foot-grid">
          <div className="foot-brand">
            <img src="./brand/rigged-lockup-reversed.svg" alt="Rigged" width="170" height="45" />
            <p>Author: Mohamed Bechir Kefi, independent researcher.</p>
          </div>
          <div>
            <p>
              Repository:{" "}
              <a href="https://github.com/mohamedbechirkefi/rigged-equal-rules">github.com/mohamedbechirkefi/rigged-equal-rules</a>.
              Manuscript:{" "}
              <a href="https://github.com/mohamedbechirkefi/rigged-equal-rules/blob/main/research/paper/manuscript.md">research/paper/manuscript.md</a>.
              More studies: <a href="https://labs.kefimohamedbechir.workers.dev">the labs index</a>.
            </p>
            <p>Licence: RIGGED Source-Available Non-Commercial Research License v1.0.</p>
            <p>An AI system (Claude, Anthropic) was used as a research and development assistant; it is not an author.</p>
            <p>Runs offline after the first load. No data about visitors is collected, stored or sent anywhere.</p>
            <p className="credits">Type: Libre Caslon Text (Pablo Impallari, Rodrigo Fuenzalida) and Barlow Semi Condensed (Jeremy Tribby), both under the SIL Open Font License, served from this site.</p>
          </div>
        </div>
      </footer>
    </>
  );
}

/** Marks the nav link of the section in view. */
function useSectionSpy(ready: boolean) {
  useEffect(() => {
    if (!ready || typeof IntersectionObserver === "undefined") return;
    const links = [...document.querySelectorAll<HTMLAnchorElement>("header.bar nav a")];
    const io = new IntersectionObserver((entries) => {
      for (const en of entries) if (en.isIntersecting) for (const a of links) a.classList.toggle("here", a.getAttribute("href") === `#${en.target.id}`);
    }, { rootMargin: "-45% 0px -50% 0px" });
    for (const a of links) { const t = document.querySelector(a.getAttribute("href") ?? ""); if (t) io.observe(t); }
    return () => io.disconnect();
  }, [ready]);
}

function Answer({ r }: { r: Results }) {
  const e1 = r.experiments.find((e) => e.id === "EXP-001")!.estimates[0];
  const e4 = r.experiments.find((e) => e.id === "EXP-004")!.estimates[0];
  return (
    <p className="answer">
      Inside the model, yes. Under one common threshold, when Group B starts half a standard deviation lower, the
      equal-opportunity gap rises by <strong>{fmtEstimate(e1)}</strong> {fmtInterval(e1)} against an
      equal-distribution control. On a real score the same base-rate prediction failed, with the sign
      reversed: <strong>{fmtEstimate(e4)}</strong> {fmtInterval(e4)}.
    </p>
  );
}

function Figure({ text }: { text: string }) {
  const ref = useCountUp<HTMLParagraphElement>(text);
  return <p className="big" ref={ref}>{text}</p>;
}

function stamp(e: Experiment): string {
  if (e.id.startsWith("JRN")) return "Exploratory";
  if (/disconfirmed|rejected|reversal/i.test(e.verdict)) return "Against the base-rate reading";
  return "Supported";
}

function verdictClass(e: Experiment): string {
  if (e.id.startsWith("JRN")) return "v-exploratory";
  if (/disconfirmed|rejected|reversal/i.test(e.verdict)) return "v-against";
  return "v-for";
}

function Published({ r }: { r: Results }) {
  const byId = (id: string) => r.experiments.find((e) => e.id === id)!;
  const e1 = byId("EXP-001").estimates[0];
  const e4 = byId("EXP-004").estimates[0];
  return (
    <>
      <section id="overview" aria-labelledby="h-overview">
        <h2 id="h-overview">Overview</h2>
        <p className="status-label"><strong>Status:</strong> {r.status_label}</p>
        <p>
          Two abstract groups, A and B, face the same decision rules. Their latent qualification differs in
          location (the starting distribution) and their scores differ in measurement noise. Four rules select
          30% of each population, and the primary metric is the equal-opportunity gap (EOG): the share of
          qualified Group A members selected minus the same share for Group B.
        </p>
        <div className="keyfinds">
          <div className="keyfind">
            <p className="tag tag-measured">Measured, simulated</p>
            <Figure text={fmtEstimate(e1)} />
            <p>{fmtInterval(e1)} (95% bootstrap). Rise in the EOG under one common threshold when Group B starts half
              a standard deviation lower (EXP-001). Supported, and implied by the model.</p>
          </div>
          <div className="keyfind">
            <p className="tag tag-measured">Measured, real data</p>
            <Figure text={fmtEstimate(e4)} />
            <p>{fmtInterval(e4)} (95% bootstrap). The same prediction on a real score (EXP-004, Group B is
              hours-per-week below 40): disconfirmed, with the sign reversed.</p>
          </div>
        </div>
        <p>
          The base rate alone does not fix the sign or size of the gap (EXP-003 and EXP-004). What remains is a
          near-definitional statement: under one common rule, the gap follows where each group's qualified members
          sit relative to the cutoff.
        </p>
      </section>

      <Explorer r={r} />

      <section id="results" aria-labelledby="h-results">
        <h2 id="h-results">Published results</h2>
        <p className="note">
          Every number below is the exact text printed in the manuscript, from the committed results at revision{" "}
          <code>{r.code_revision.slice(0, 7)}</code>. Confirmatory experiments, contradictions and exploratory checks
          are shown with the same weight. Intervals are 95% percentile bootstrap intervals over 20 seeds.
        </p>
        {r.experiments.map((e) => (
          <article key={e.id} className={`panel letter-panel ${verdictClass(e)}`} aria-labelledby={`h-${e.id}`}>
            <div className="panel-head">
              <h3 id={`h-${e.id}`}>
                {e.id}: {e.title}
              </h3>
              <p className={`stamp ${verdictClass(e)}`}>{stamp(e)}</p>
            </div>
            <p>
              <span className="badge">{e.status}</span>
            </p>
            <p className="verdict"><strong>Verdict under the frozen rule:</strong> {e.verdict}</p>
            {e.estimates.length > 0 && (
              <div id={`est-${e.id}`} className="table-scroll" role="region" aria-label={`${e.id} estimates`} tabIndex={0}>
                <table>
                  <thead>
                    <tr>
                      <th scope="col">Quantity</th>
                      <th scope="col">Estimate</th>
                      <th scope="col">95% interval</th>
                      <th scope="col">Kind</th>
                    </tr>
                  </thead>
                  <tbody>
                    {e.estimates.map((x) => (
                      <tr key={x.label}>
                        <th scope="row">{x.label}</th>
                        <td>{fmtEstimate(x)}</td>
                        <td>{x.interval_display ?? "no interval (not a sampled quantity)"}</td>
                        <td>{KIND_LABEL[x.kind]}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            {e.notes.map((n, i) => (
              <p key={i} className="note">{n}</p>
            ))}
            <p className="meta">
              Report: <code>{e.report_path}</code>
              {e.claim_ids.length > 0 && <>. Claims: {e.claim_ids.join(", ")}</>}
            </p>
          </article>
        ))}
      </section>

      <section id="assumptions" aria-labelledby="h-assumptions">
        <h2 id="h-assumptions">Assumptions <span className="tag tag-assumption">Model assumptions</span></h2>
        <p className="note">These are the generator and analysis settings fixed by the frozen protocols. They are assumptions, not results.</p>
        <dl className="assumptions">
          {r.assumptions.map((a) => (
            <div key={a.name}>
              <dt>{a.name}</dt>
              <dd>
                {a.value} <span className="meta">({a.source})</span>
              </dd>
            </div>
          ))}
        </dl>
      </section>

      <section id="method" aria-labelledby="h-method">
        <h2 id="h-method">Method and limitations</h2>
        <p>
          Four experiments were registered and their protocols frozen by the owner before any confirmatory run.
          Each seed draws a fitting and an evaluation population; rules are fitted on the first and measured on the
          second, with common random numbers across cells and rules. P0 is one raw threshold (the baseline). P1 is
          one threshold on a within-group calibrated score. P2 equalises selection rates. P3 equalises true positive
          rates. Every directional hypothesis compares the 95% interval with a smallest effect of 2 pp. EXP-004
          applies the same rules to a frozen four-feature logistic score on the UCI Adult test file (Becker and
          Kohavi 1996, CC BY 4.0); no protected attribute is a group, input, stratifier or covariate.
        </p>
        <h3>Limitations</h3>
        <ul>
          {r.limitations.map((l, i) => (
            <li key={i}>{l}</li>
          ))}
        </ul>
        <details>
          <summary>Source files and hashes</summary>
          <ul className="meta">
            {r.sources.map((s) => (
              <li key={s.path}>
                <code>{s.path}</code> <code>{s.sha256.slice(0, 12)}</code>
              </li>
            ))}
          </ul>
        </details>
      </section>
    </>
  );
}
