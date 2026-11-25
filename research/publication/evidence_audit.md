<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# Evidence audit (master prompt 11.5), M4

| Field | Value |
|---|---|
| Date | 2026-11-25 |
| Scope | `research/paper/manuscript.md`, `research/paper/supplementary.md`, the four experiment reports, `research/claims_register.csv`, `research/paper/references.bib` |
| Commands | `PYTHONPATH=src .venv/bin/python scripts/m4_evidence_audit.py` (raw-output checks and number trace); `python3 scripts/build_artifact_manifest.py`; `python3 scripts/build_supplementary.py` |
| Outputs | `evidence_audit_output.json`, `number_trace.csv`, `artifact_manifest.json` (this folder) |
| Code under audit | `src/` and `tests/` unchanged since the provenance revision b455d59 (`git diff --stat b455d59 HEAD -- src tests` is empty) |

## 1. Raw outputs against tables (part A)

For each experiment the script re-reads `results/EXP-NNN/results.json`. It checks per-run identities and re-derives every summary and contrast value with its own implementation of the frozen interval method. That method is the mean, a percentile bootstrap over seeds (10,000 resamples, PCG64 seed 20261124) and a t-interval.

The per-run identities are:
- group sizes sum to the evaluation n;
- tp + fn = positives and fp + tn = negatives;
- selected = tp + fp;
- TPR, FPR, PPV and SR equal their count ratios to 1e-12;
- each gap equals A minus B;
- utility equals (TP - c FP)/n.

| Experiment | Runs (ok) | Identity violations | Summary values re-derived | Largest deviation | Contrast values re-derived | Largest deviation | SHA256SUMS |
|---|---|---|---|---|---|---|---|
| EXP-001 | 240 (240) | 0 | 432 | 4.98e-11 | 24 | 3.83e-11 | all match |
| EXP-002 | 960 (960) | 0 | 1,728 | 4.98e-11 | 96 | 4.63e-11 | all match |
| EXP-003 | 420 (420) | 0 | 756 | 5.00e-11 | 0 (no contrast table rows) | not applicable | all match |
| EXP-004 | 160 (160) | 0 | 288 | 4.83e-11 | 96 | 4.93e-11 | all match |

The deviations are at the 10-significant-digit precision of the CSV files. Denominators were checked as follows:
- every summary row has 20 seeds and 0 missing values;
- every EXP-001 to EXP-003 run has n = 20,000 per population;
- every EXP-004 run evaluates on 8,141 rows (the fitting half is 8,140 rows by construction, floor(16,281 / 2)).

The units are proportions in the files and pp (x 100) in the documents. Precision is two decimals for gaps and four or five for utility per capita.

## 2. Provenance and hashes

- In every experiment, every run's `config_hash` in `results.json` equals its entry in `provenance.json` and appears in the frozen `research/experiments/EXP-NNN/config.json`.
- The experiment protocol SHA-256 and the config SHA-256 in `provenance.json` equal the current files.
- The guard reports all four protocols frozen.
- `export-configs --check` reports that all four configs match the code.
- The figure, `metrics.csv` and `run_manifest.json` copies in `research/experiments/EXP-NNN/` are byte-identical to `results/EXP-NNN/`.
- **Finding (disclosed, not changed):** `research/freeze.json` was modified after the runs. The M3 commit appended the `m3_deviations` and `m3_provenance_revision` records. Its SHA-256 at run time (`f13466cd...` in `provenance.json`) therefore differs from the current file (`c3471f69...`). The diff against b455d59 is additions only; no frozen hash changed.

## 3. Number trace (part B)

Every number with a decimal point in the audited documents (final run after the second-pass revisions and the report addenda) was looked up among the values of the committed tables. The lookup used the raw values and the values times 100, at the precision shown. Results are in `number_trace.csv`.

| Document | Decimal numbers | Unmatched | Unmatched items, reviewed by hand |
|---|---|---|---|
| manuscript.md | 441 | 10 | 8 are DOI or arXiv identifiers. 7.67 is a difference of two XTAB-001 columns (29.91 minus 22.25, unrounded 7.667), verified by hand. |
| supplementary.md | 993 | 0 | |
| EXP-001 report | 108 | 1 | 71.7 MiB peak RSS = 75,202,560 bytes in `run_manifest.json` (unit conversion), verified. |
| EXP-002 report | 139 | 0 | |
| EXP-003 report | 141 | 0 | |
| EXP-004 report | 178 | 0 | |
| claims_register.csv | 172 | 1 | DOI 10.24432. |

**Limitation of the trace.** A match shows that the number exists in a committed table, not that it is the right cell. The headline numbers were therefore also checked against their exact row by hand: every number in the abstract, Tables 1 to 6 and CLM-001 to CLM-030. Integers were checked by hand: run counts, 48 of 48, 56 of 60, 60 of 60, 5 of 12, 1,780 = 240 + 960 + 420 + 160, 32,561 and 16,281 rows (`data/ingestion_report.json`), 8,140 and 8,141.

## 4. Mismatches found and fixed

| ID | Where | Found | Fix |
|---|---|---|---|
| AUD-1 | EXP-001 report, section 9 | The exploratory SIZING contrast was given as 6.31 pp. The committed value is 0.06304582915 (6.30 pp; freeze record 6.305). 6.31 is the analytic population value. | Corrected to 6.30 with a note. |
| AUD-2 | EXP-003 report | The status and sections 6, 9 and 10 still said DEC-019 was open for the owner. | Updated to the owner's decision of 2026-11-25 (DEC-021). |
| AUD-3 | `experiment_registry.csv` | Status "report pending (coordinator)" for all four experiments, but the reports exist. | Status updated. |
| AUD-4 | `references.bib` | The header said full texts were "to be read in M1", but they were never read. The dataset entry becker1996 was cited but missing. | Header states abstract-level only; becker1996 added. |
| AUD-5 | EXP-004 report and CLM-012 | The reversal was called a "contradiction of the synthetic mechanism". The data test only the base-rate prediction (second review pass, R3). | CLM-012 and the manuscript say "contradiction of the base-rate prediction". The frozen verdict and the report's verdict line are unchanged. |
| AUD-6 | EXP-002 report and CLM-004 | "P1 brings PPV parity within 2 pp" holds only for the 20-bin map: 2.10 pp with the exact posterior (JRN-0015). | Qualified in the manuscript and in the CLM-004 and CLM-016 limitations. |

## 5. External claims

| Source | What was read | Claims resting on it | Status |
|---|---|---|---|
| kleinberg2016 | arXiv abstract page, 2026-11-24 | CLM-020 | abstract only |
| chouldechova2017 | arXiv abstract page, 2026-11-24 | CLM-020 | abstract only |
| corbettdavies2017 | arXiv abstract page, 2026-11-24 (KDD DOI not resolved) | CLM-021 | abstract only |
| pleiss2017 | arXiv abstract page, 2026-11-24 | CLM-022 | abstract only |
| hardt2016 | arXiv abstract page, 2026-11-24 | CLM-023 | abstract only; the exact definition is not checked |
| liu2018 | arXiv abstract page, 2026-11-24 | CLM-024 | abstract only |
| barocas2023 | book home page, 2026-11-24 | framing only, no claim | home page only |
| becker1996 | UCI dataset page, 2026-11-24 | CLM-025 (licence, DOI) | dataset page read |
| ding2021 | folktables README only | not cited in the manuscript | paper unverified |

Every statement in manuscript section 2 was compared with the abstract summary recorded in `research/literature_review.md`, and none goes beyond it. The manuscript labels every reference "abstract only" or names the page that was checked. No source was read in full; this is stated in sections 2 and 7.

## 6. Contradictions, leakage and missing runs

- **Contradictions between documents:** AUD-2, AUD-3 and AUD-5 are fixed. The EXP-004 report's section 8 offered "a hypothesis for M4, not a finding". The manuscript keeps that status: JRN-0016 is exploratory and post hoc.
- **Leakage:** none found in the confirmatory pipeline. The EXP-004 score was fitted on `adult.data` only. Thresholds are fitted on the fitting half and metrics computed on the evaluation half. JRN-0007 (by sex, training file) enters no analysis. JRN-0016 uses the test pool, is exploratory, and changes no verdict.
- **Missing failed runs:** no confirmatory run failed. Every exploratory matrix is listed in manuscript section 4.7.
- **Unsupported causal statements:** none remain. EXP-004 statements are descriptive, and the manuscript says the descriptions establish no cause.

## 7. Strength and scope of evidence per conclusion

| Conclusion | Strength | Scope |
|---|---|---|
| EXP-001 H1 | Strong for the model (margin of 4.20 pp above the 2 pp boundary; analytic agreement) | Simulated Gaussian model; known in advance |
| EXP-002 H1, H2 | Strong for the model; verdict robust to the tolerance and to P1's binning | Simulated; consistent with theory known from abstracts |
| EXP-003 H0 rejected, H2 | Strong (effects of 19 to 23 pp at equal base rates; analytic agreement in grids A and B) | Simulated; H2 known in advance |
| EXP-003 H3, H4 | Sign only; H4 carries the DEC-019 limitation | Simulated; one parameterisation per family |
| EXP-004 H1-real disconfirmed | Strong for this pool (upper bound -6.05 pp) | One partition, one score, one fixed pool; tests the base-rate prediction only |
| EXP-004 exploratory account | Descriptive, post hoc | Same file; no cause |

## 8. Gate

Every numerical claim in the manuscript maps to a claim row (CLM-001 to CLM-019, CLM-025 to CLM-030), which gives a result ID, a config hash and a table or figure. Every table and figure maps to an artifact manifest entry. Every external claim maps to a source that was opened, marked abstract-only where that applies (CLM-020 to CLM-025). The M4 gate holds, subject to the owner's review of the manuscript text, which is an M6 item.
