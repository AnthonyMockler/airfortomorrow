# Decision: Himawari Realtime Critical-Path Speedups

## Decision
Prioritize Himawari realtime performance improvements on three low-risk, high-impact areas:
1. Add thread-based realtime FTP download concurrency (not process-based).
2. Optimize per-file performance in `process_single_file_streaming` without adding parallel file processing.
3. Cache geoBoundary country files in IDW interpolation and reuse cached files when present.

## Why
- Current bounded quickstart-like runs show Himawari is now the dominant wall-time pipeline.
- Existing logs show OpenAQ is no longer the critical path in test-bounded runs, while Himawari runs for 10-15 minutes.
- Existing H3 streaming processing is intentionally sequential to limit memory pressure; optimizing inner per-file work is safer than parallelizing file-level H3 processing.
- IDW currently fetches boundaries from remote URLs each run, with retry sleeps on transient network errors; this is avoidable by local caching.

## Change Scope
- `src/data_collectors/himawari_aod.py`
  - Realtime download concurrency using threads and bounded worker count.
  - Keep existing external behavior and output paths.
- `scripts/run_himawari_integrated_pipeline.sh`
  - Surface new download-worker control flag and pass it through.
- `src/himawari_integrated_pipeline.py`
  - Accept/passthrough download worker setting to collector command.
- `src/data_processors/process_himawari_h3_streaming.py`
  - Improve per-file processing efficiency in `process_single_file_streaming` only.
- `src/data_processors/himawari_idw_interpolator.py`
  - Add boundary file caching and cache-first loading behavior.
- Behave coverage under `features/contracts/` and `features/steps/`.

## Non-Goals
- Do not remove or alter the realtime 168-hour extension behavior used for model rolling-window expectations.
- Do not introduce speculative skipping of NetCDF files based on predicted no-data outcomes.
- Do not parallelize H3 file processing across NetCDF files.
- Do not change output schema/file naming contracts for Himawari H3, daily aggregated, or interpolated outputs.
