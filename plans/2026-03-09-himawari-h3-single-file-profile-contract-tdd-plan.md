# Plan: Himawari H3 Single-File Profiling Contract

- Status: Complete
- Owner: Codex
- Started: 2026-03-09
- Last Updated: 2026-03-09

## Feature Goal

Create a targeted Docker-runnable pytest contract for one representative Himawari raw file that measures the shared H3 streaming substeps and protects the resulting parquet output with a checked-in artifact.

## Scope Guardrails

- Use one real historical Himawari NetCDF file only.
- Exercise the shared streaming H3 processor directly, not the full integrated pipeline.
- Keep the test isolated enough to run via `./scripts/run_tests.sh -- ...`.
- Treat `raster_to_dataframe(...)` as a timed black box, not an optimization target in this slice.
- Use output-contract checks that allow internal refactors but catch important semantic drift.

## Red

- Add targeted pytest coverage that expects:
  - a representative-file metadata artifact,
  - a profiling helper that returns named step timings,
  - and semantic equality with a checked-in expected H3 artifact.
- Run the smallest targeted pytest command and capture the initial failure.

## Green

- Add the profiling helper and representative single-file test support.
- Check in the representative artifact and metadata.
- Re-run the targeted pytest command until it passes in Docker.

## Regression Safety

- The contract must verify schema, row count, sorted H3 keys, and AOD values against the expected artifact.
- The contract must assert that timing output includes the named major stages so later optimization work can compare runs consistently.
- The test should skip cleanly when Himawari FTP credentials are unavailable.

## Success Criteria

- One-command Docker test exists for a representative Himawari single-file run.
- The test reports per-stage timings for the shared streaming H3 path.
- The output matches the checked-in expected artifact on the important fields.
- The chosen representative file is documented and justified.

## Evidence to Capture

- RED pytest command and failure signal.
- GREEN pytest command and pass result.
- Representative file chosen and why.
- Observed timing breakdown from the passing run.

## Notes and Findings

- Candidate representative source selected from current THA H3 outputs:
  - `2025-01-03 09:00` produced `417,964` H3 rows with mean AOD about `0.25`, stddev about `0.096`, and max about `0.683`.
  - This looks materially more representative than sparse outputs in the ~`29k` row range.
- The shared processing target is `src/data_processors/process_himawari_h3_streaming.py`, not the historical/realtime file-collection branches.

## Evidence Log

- RED command:
  - `./scripts/run_tests.sh -- tests/test_himawari_h3_single_file_profile.py -q`
- RED failure signal:
  - `ImportError: cannot import name 'profile_single_file_streaming' from 'src.data_processors.process_himawari_h3_streaming'`
- GREEN command:
  - `./scripts/run_tests.sh -- tests/test_himawari_h3_single_file_profile.py -q -s`
- GREEN result:
  - `2 passed, 2 warnings in 8.00s`
- Checked-in artifacts:
  - `tests/artifacts/himawari_single_file/representative_file.json`
  - `tests/artifacts/himawari_single_file/expected_h3_output.parquet`
- Live single-file timing breakdown for `2025-01-03 09:00` / `THA`:
  - `download`: `3.382s`
  - `boundary_creation`: `2.426s`
  - `netcdf_to_tif`: `1.209s`
  - `mask`: `0.005s`
  - `raster_to_dataframe`: `0.064s`
  - `polars_conversion`: `0.008s`
  - `write_parquet`: `0.027s`
  - `cleanup`: `0.001s`
  - `processing_total`: `1.323s`
  - `full_total`: `7.132s`
- Main finding:
  - For this representative file, the dominant repeatable H3-stage cost is NetCDF-to-TIF conversion, not `raster_to_dataframe(...)`.
  - Boundary creation is slower than the H3 conversion itself, but it is a one-time per-run setup cost rather than a per-file loop cost.
  - The contract now mirrors the production `month/day` output layout and compares float payloads with tight tolerance while keeping exact checks for keys and metadata columns.

## Handoff

- After this slice is green, use the timing breakdown to decide whether the next optimization should target:
  - NetCDF to TIF conversion,
  - raster masking,
  - pandas-to-Polars conversion,
  - parquet writing,
  - or outer-loop parallelization.
