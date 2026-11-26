<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# CLAUDE.md: how every session works in RIGGED

RIGGED is a small, reproducible simulation study of algorithmic fairness: can equal rules yield unequal outcomes under different starting distributions? `master_prompt.md` is the authority. Never edit it. If this file and the master prompt conflict, the master prompt wins; record the conflict in `progress.md`.

## 1. Reading order (before modifying anything)

1. `master_prompt.md` (in full at the first session of any new contributor; sections 1 to 11 thereafter as needed).
2. `roadmap.md`: milestones, current status, blockers.
3. `progress.md`: the latest entries and the stated next action.
4. `research/protocol.md`: the project protocol (status: DRAFT until the owner freezes it).
5. `research/claims_register.csv`: what may and may not be claimed.

Then run `git status`, inspect existing files, and never overwrite the owner's changes. State the current milestone and the next bounded task before working.

## 2. Mandatory requirements (master prompt section 11, extended milestones 11.6)

- Maintain the publication tree of 11.1: `research/experiment_registry.csv`, `research/protocol.md`, `research/claims_register.csv`, `research/paper/` (manuscript.md canonical, manuscript.tex and manuscript.pdf generated), `research/experiments/EXP-NNN/` (protocol.md, report.md, config.json, run_manifest.json, metrics.csv, figures/, reproduction.md), `research/publication/` (artifact_manifest.json, claims_audit.md, reproducibility_report.md, author_review.md, release_checklist.md).
- Stable identifiers: EXP-NNN for experiments, RUN-EXP-NNN-<cell>-<policy>-s<seed> for runs, FIG-NNN for figures, CLM-NNN for claims.
- Register every experiment before confirmatory execution; a seed is a run, not a new experiment.
- Each experiment gets a protocol (11.2) before it runs and a standalone report (11.3) after it runs, including failed, null, abandoned and exploratory experiments.
- One integrated manuscript (11.4), built from the experiment reports. Markdown is canonical; LaTeX and PDF are generated with the zero-cost toolchain (section 5 below).
- Evidence pipeline (11.5): tables and figures are generated once from versioned results and reused everywhere; a manifest maps each number to experiment, run IDs, result path, generator script, config hash and code revision. A second review pass challenges the preferred hypothesis.
- Milestone gates (11.6):
  - M0/M1: registry, manuscript skeleton, experiment protocols, zero-cost toolchain confirmed; confirmatory protocols frozen by the owner before execution.
  - M2: versioned output schemas, run manifests and report generators built alongside the core algorithms.
  - M3: individual reports written as experiments finish; failures and deviations recorded; provenance captured at run time.
  - M4: experiment reports and evidence audit finished; cross-experiment synthesis in the manuscript, including contradictory results and sensitivity analysis.
  - M5: demo, paper, reports and articles use identical verified results, labels and scope.
  - M6: PDFs compiled and visually inspected; references, links, equations, figures and metadata verified; smoke results reproduced in a clean clone; owner review checklist completed.
- The publication gate holds only when every registered experiment has a truthful standalone report, the manuscript is complete, artifacts are traceable and blockers are disclosed.

## 3. Rules (all sessions)

### Gates
- Never push, add a remote, create a GitHub repository or publish anything (G-PUBLIC).
- No paid service of any kind. No paid API, inference, dataset, compute, hosting or domain.
- Never freeze a protocol: freezing is the owner's decision (G-FREEZE). Until the owner freezes a protocol, every run is exploratory and labelled so.
- No confirmatory experiment before the owner has frozen its protocol. Small exploratory smoke checks are allowed and labelled exploratory.

### Scope
- Work only inside this repository. Tools outside it are used read-only: `../.tools/` (uv, typst, pypdf, pillow, pandoc; paths relative to the repository) and the Node installation in the research root's `helix/.tools/node/bin` (never modify that folder).
- Do not touch any other folder under the research root.
- Never kill processes you did not start. Never delete anything you did not create in the current session.

### Truthfulness
- Never fabricate results, citations, test counts or PDFs.
- Record the commands you ran and their actual outputs in `progress.md`.
- Anything not verified is labelled unverified. Cite a source as read only if it was actually opened, with URL or DOI and access date.
- Simulated results are labelled simulated. Groups are abstract synthetic groups (Group A, Group B), never protected groups. No real hiring or lending decision is claimed. No fairness metric is presented as universal.

### Files and style
- New text and code files start with `SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0` as a comment where the format allows. JSON and CSV are covered by `NOTICE.md`.
- English. No em dashes. Plain, formal register.
- No e-mail address, personal identifier or secret in any committed file (git author metadata excepted).
- Refer to the owner as "the owner" (they/them).
- The licence files (`LICENSE`, `NOTICE.md`, `LICENSE_HISTORY.md`, `CLA.md`, `CODEOWNERS`, `cla.yml`) are the owner's decision; do not change them. Development commands may be appended to `CONTRIBUTING.md`.

### Commits
- Local commits only, with the owner's git identity passed per command (`git -c user.name=<owner login> -c user.email=<owner address> commit`; the values are given in the session brief and are not stored here), message ending with a blank line then `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Run `git status` before and after.

## 4. Session end

Update `progress.md` (dated entry: decisions, commands, actual results, failures, changed files, risks, next action) and `roadmap.md` (statuses, blockers). Append decisions to `research/decision_log.md`. Never mark incomplete work done.

## 5. Toolchain (zero cost, decision DEC-002)

- Python 3.12.1 at `/usr/local/bin/python3`; dependencies locked with `../.tools/py/bin/uv lock` (`uv.lock`).
- No TeX distribution. PDFs: pandoc (`../.tools/pandoc`) converts Markdown to Typst; the `typst` Python package (`../.tools/py/bin/python`) compiles it. `manuscript.tex` is generated from Markdown with pandoc but is not compiled locally.
- Commands are recorded in `CONTRIBUTING.md` (development section) and `scripts/`.
