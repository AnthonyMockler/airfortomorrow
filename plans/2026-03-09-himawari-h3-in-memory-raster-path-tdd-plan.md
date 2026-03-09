# Plan: Himawari H3 In-Memory Raster Path

- Status: Complete
- Owner: Codex
- Started: 2026-03-09
- Last Updated: 2026-03-09

## Feature Goal

Reduce the shared per-file Himawari H3 processing time by removing the temporary on-disk GeoTIFF step while preserving output equivalence against the checked-in representative artifact.

## Scope Guardrails

- Limit the change to the shared streaming H3 processor.
- Keep rasterio-based masking semantics intact.
- Use the existing representative single-file profiling contract as the correctness gate.
- Do not change `raster_to_dataframe(...)` behavior or its call contract.

## Red

- Use the existing representative-file contract as regression safety.
- Capture the current single-file timing baseline before the optimization:
  - `netcdf_to_tif`: `1.209s`
  - `processing_total`: `1.323s`
  - `full_total`: `7.132s`

## Green

- Refactor the per-file raster staging path to avoid writing a temporary GeoTIFF to disk.
- Preserve output layout and payload semantics.
- Re-run the targeted Docker pytest contract until it passes.

## Regression Safety

- `tests/test_himawari_h3_single_file_profile.py` must stay green.
- The live single-file test must still match the checked-in artifact on H3 keys, metadata columns, and AOD values.
- The named timing keys must still be emitted.

## Success Criteria

- The representative-file contract passes after the refactor.
- The live timing breakdown still points to valid major stages.
- The optimized path is at least directionally faster in `processing_total` than the baseline.

## Evidence to Capture

- Before/after targeted test command.
- Before/after timing comparison from the representative live run.
- Any codepath differences needed to preserve exact output.

## Notes and Findings

- Current baseline from the revised single-file contract:
  - `download`: `3.382s`
  - `boundary_creation`: `2.426s`
  - `netcdf_to_tif`: `1.209s`
  - `processing_total`: `1.323s`
  - `full_total`: `7.132s`
- Optimization hypothesis:
  - removing the write/reopen/delete GeoTIFF cycle should reduce the dominant repeatable per-file cost without changing the masked raster values that feed `raster_to_dataframe(...)`.

## Evidence Log

- Verification command:
  - `./scripts/run_tests.sh -- tests/test_himawari_h3_single_file_profile.py -q -s`
- Result after in-memory raster refactor:
  - `2 passed, 2 warnings in 7.75s`
- Before/after representative-file timings:
  - `netcdf_to_tif`: `1.209s` -> `0.875s`
  - `processing_total`: `1.323s` -> `0.962s`
  - `full_total`: `7.132s` -> `6.974s`
- Output-equivalence guardrail:
  - The live single-file test still matched the checked-in expected artifact on schema, row count, sorted `h3_08`, metadata columns, and `aod_value` within tight tolerance.
- Main finding:
  - Replacing the temporary on-disk GeoTIFF with an in-memory raster preserved output semantics and produced an approximately `27%` reduction in the shared per-file processing time on the representative file.

## Handoff

- If the in-memory raster path is green and faster, the next Himawari H3 target should be boundary reuse/caching inside the integrated pipeline run rather than further work on `raster_to_dataframe(...)`.
