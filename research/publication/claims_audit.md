<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# Claims audit

Status: M4 complete (2026-11-25). Full record: `evidence_audit.md`. Second review pass: `review_pass_2.md`.

Checklist per claim (one row in `../claims_register.csv`, CLM-001 to CLM-030):

- [x] Each numerical claim maps to its experiment ID, run IDs, config hash, result path and figure or table ID (columns of the register; `artifact_manifest.json`).
- [x] Each number is re-derived from the raw output, with denominator, unit, precision and sample count checked (evidence audit, sections 1 and 3).
- [x] Uncertainty is stated at the seed level (95% percentile bootstrap over 20 seeds; the EXP-004 fixed-pool caveat is stated).
- [x] Each external claim maps to a source actually opened, with access date. At M4 all were abstract-only and marked so (CLM-020 to CLM-025). M6 (2026-11-25): for CLM-020 to CLM-024 the full text was opened and the cited passage checked; CLM-021 and CLM-022 were narrowed (evidence audit, section 9).
- [x] Scope is stated (synthetic generator, abstract groups; one non-protected partition of one file). There is no protected-group or real-decision claim.
- [x] No fairness metric is presented as universal.
- [x] The second review pass challenged the preferred hypothesis (`review_pass_2.md`).

Claims removed or qualified in M4:

- CLM-012: "contradiction of the synthetic mechanism" narrowed to "contradiction of the base-rate prediction".
- CLM-004 and CLM-016: P1 results qualified as dependent on the 20-bin map (JRN-0015).
- CLM-009 and CLM-011: the DEC-019 status updated to the owner's decision (DEC-021).
- Exploratory claims (CLM-018, CLM-019) are labelled EXPLORATORY in their text.
- Manuscript statements without a row: none found. The abstract's closing sentence is supported by CLM-006, CLM-007, CLM-012 and CLM-017.
