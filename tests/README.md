<!-- SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0 -->
# tests/

Run with `scripts/rigged test` or `uv run --frozen pytest`.

| File | Covers |
|---|---|
| `test_numerics.py` | Normal CDF against `math.erfc`; quantile round trips; latent families standardised; matched base rates; Student t quantiles against tabulated values |
| `test_config.py` | Invalid inputs rejected; run IDs; config-hash stability |
| `test_generator.py` | Determinism; independent fitting and evaluation streams; common random numbers across cells; group counts; labels; extreme group shares |
| `test_policies.py` | Hand-computed threshold with ties; exact capacity (property test against a naive reference); nested selections as capacity rises; calibration golden example; P0 to P3 fitting properties; explicit failures on empty groups or no qualified members |
| `test_metrics.py` | Project-specific checks: confusion matrices (golden and differential), group counts, zero denominators (null with reason), threshold monotonicity of SR, TPR and FPR |
| `test_analytic.py` | Analytic P0 values against Gaussian closed forms; zero gaps for identical groups; simulation against population values (seeds 5000+, not confirmatory) |
| `test_stats.py` | Hand-computed summaries; determinism; missing and degenerate inputs |
| `test_schema_runner_cli.py` | Config to validated results and manifest; failures recorded; determinism; schema fails closed on malformed input; report generation; CLI refuses confirmatory runs while unfrozen; protocol guard states |
