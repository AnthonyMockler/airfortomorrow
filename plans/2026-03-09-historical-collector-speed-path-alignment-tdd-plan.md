# Plan: Historical Collector Speed Path Alignment

- Status: In Progress
- Owner: Codex
- Active Agent: Codex (GPT-5)
- Started: 2026-03-09
- Last Updated: 2026-03-09
- Scope Note: Map the slow historical collectors against the prior realtime speedups, identify where historical diverges, and stage the next implementation slices against the bounded historical Behave baseline.

## Feature Goal

Reduce bounded historical collection wall time for the slow collectors without changing user-visible wrapper behavior or artifact contracts.

## Scope Guardrails

- Use the existing historical Behave contract as the main correctness gate for speed work.
- Preserve wrapper entrypoints and output naming unless a later change is explicitly versioned.
- Respect real source differences: historical archive/S3 flows do not need to be forced into the same codepath as realtime API flows.
- Prefer orchestration, retry, download, and materialization improvements before deeper algorithm changes.
- Stage the work in collector-sized slices so we can measure before/after timings with the same bounded commands.

## Red

1. Reproduce the current bounded historical collector timings from `features/contracts/historical_collection_contract.feature`.
2. For each slow collector, trace the wrapper entrypoint to the actual mode-specific implementation and compare that path to the prior realtime optimization work.
3. Where shared files are touched, re-run the relevant realtime contract coverage after the change so shared-path regressions show up immediately.

## Green

1. OpenAQ historical:
   - Consolidate duplicate historical entrypoints around one archive download path.
   - Push date-window filtering earlier so bounded historical runs do not pay for avoidable full-year materialization.
2. Himawari historical:
   - Reuse the realtime threaded day-level FTP download pattern for historical day batches.
   - Ensure `--download-workers` actually reaches the historical collector path.
3. ERA5 historical:
   - Remove historical-only fixed pacing where shared adaptive retry/backoff already exists.
   - Fix wrapper behavior that overrides explicit IDW CLI settings before the Python pipeline sees them.

## Regression Safety

- Keep `features/contracts/historical_collection_contract.feature` green for Air Quality, FIRMS, Himawari, and ERA5 historical slices.
- If OpenAQ shared collector logic changes, re-run `features/contracts/openaq_realtime_contract.feature`.
- If Himawari shared collector/integrated-path logic changes, re-run the existing Himawari realtime contract coverage that shipped with the realtime speedup work.
- If ERA5 shared collector or wrapper logic changes, re-run the existing ERA5 realtime coverage and compare bounded timing evidence.
- Continue requiring fresh artifacts from the current run so stale files cannot hide regressions.

## Success Criteria

- We can state clearly, per collector, whether the historical path fully uses, partially uses, or bypasses the prior realtime improvements.
- The first optimization slice is chosen from measured historical runtime and path divergence, not guesswork.
- Historical behavior stays contract-safe under the bounded real-data Behave scenarios.
- Before/after timing evidence is recorded for each optimization slice with the same bounded command profile.
- Shared-path changes do not regress the already-improved realtime workflows.

## Evidence to Capture

- Historical bounded timing baseline from the historical Behave contract:
  - Air Quality historical: `33m26.354s`
  - Himawari historical: `17m2.378s`
  - ERA5 historical: `6m13.479s`
  - FIRMS historical: `1m20.449s`
- Prior realtime optimization references:
  - OpenAQ: commit `f2aeeba` and `decisions/2026-03-07-openaq-realtime-rate-limit-consolidation.md`
  - ERA5: commit `ed12f5b` and `decisions/2026-03-07-era5-realtime-performance-bottlenecks.md`
  - Himawari: commit `8332d3f` and `decisions/2026-03-07-himawari-realtime-critical-path-speedups.md`
- Source entrypoints and mode branches that prove path alignment or divergence.
- Before/after command timings and log-file references for each optimization pass.

## Notes and Findings

### Historical vs Realtime Alignment Matrix

- OpenAQ / Air Quality historical:
  - Realtime optimized path:
    - `scripts/collect_openaq_realtime.sh` runs `python -m src.data_processors.openaq_realtime_client`.
    - Commit `f2aeeba` only touched realtime OpenAQ files and contracts.
  - Historical path actually used today:
    - `scripts/collect_openaq_historical.sh` runs `src/data_processors/s3_historical_data.py`.
    - `src/air_quality_integrated_pipeline.py` imports `src.data_processors.s3_historical_data.main` in historical mode.
    - `src/collect_openaq_data.py` still exposes another historical path through `OpenAQCollector.collect(..., mode="historical")`.
    - `src/data_collectors/openaq_collector.py` contains its own `collect_historical_data()` S3/archive implementation.
  - Conclusion:
    - Historical OpenAQ does not use the realtime rate-aware gateway improvements.
    - Historical OpenAQ is fragmented across multiple archive-oriented entrypoints and should be consolidated before tuning.
  - Existing runtime evidence:
    - The bounded Air Quality historical Behave run took `33m26.354s`.
    - Prior evidence already showed the current path materializes many `location_<id>_<year>.parquet` files before downstream date filtering.

- ERA5 historical:
  - Realtime optimization reference:
    - Commit `ed12f5b` updated `src/data_collectors/era5_meteorological_idw.py`.
  - Shared implementation today:
    - Both realtime and historical run through `src/data_collectors/era5_meteorological_idw.py`.
    - Historical `collect_historical_data()` uses the shared `_make_rate_limited_request()` and `_execute_request_with_backoff()` helpers.
  - Historical-only bottlenecks still present:
    - `collect_historical_data()` processes dates sequentially and sleeps for 2 seconds between dates.
    - Historical output filenames are hardcoded as `THA_LAO`.
    - `scripts/run_era5_idw_pipeline.sh` overwrites explicit `--idw-rings` / `--idw-weight-power` values with config-derived values before invoking the Python pipeline, even though `src/era5_integrated_pipeline_idw.py` respects explicit CLI overrides once it receives them.
  - Conclusion:
    - Historical ERA5 partially uses the realtime-era shared improvements, but it still has historical-specific orchestration costs worth optimizing in place.

- Himawari historical:
  - Realtime optimization reference:
    - Commit `8332d3f` added realtime FTP download concurrency and shared H3/IDW improvements.
  - Shared improvements already used by historical:
    - Historical and realtime both go through the same integrated Python pipeline for cache-based H3 processing.
    - The shared H3 streaming and IDW/cache changes live in files touched by the realtime speedup commit, so historical already benefits from those downstream improvements.
  - Historical-only divergence:
    - `src/data_collectors/himawari_aod.py` keeps a sequential `download_historical_files()` loop.
    - Realtime has a separate threaded `download_realtime_files()` path with per-day batch workers.
    - The shell wrapper accepts `--download-workers` for both modes, but `src/himawari_integrated_pipeline.py` only forwards `--download-workers` to the collector in realtime mode.
  - Conclusion:
    - Historical Himawari partially uses the realtime improvements.
    - The missing piece is the historical download path, plus the integrated-path flag forwarding needed to enable it.

### Recommended Work Order

1. OpenAQ historical / Air Quality historical
   - Highest measured runtime and the largest path divergence from prior realtime work.
   - Separate and duplicated historical implementations are likely hiding the fastest safe win.
2. Himawari historical
   - Clear missing reuse of a proven realtime optimization pattern.
   - The wrapper and collector already have enough plumbing to make this an isolated follow-up slice.
3. ERA5 historical
   - Already partially aligned with the shared retry/backoff work, so the remaining wins are narrower and lower risk.

User-directed execution order update:
- Although OpenAQ remains the largest measured bottleneck, the next implementation slice has been redirected to Himawari first in order to build a shared downloader that can serve both historical and realtime paths with narrower test loops.
- Completed first slice:
  - Himawari shared downloader plan/executor landed with downloader-only test coverage.
  - Historical month discovery now filters month directories to the requested range instead of scanning all available months.
  - Narrow downloader-only live coverage passed in `1m13.340s`.
  - The bounded historical integrated Himawari workflow still passed but latest runtime was `29m40.319s`, so full-pipeline speedup is not yet confirmed.

### Merge vs Separate-Path Recommendation

- OpenAQ:
  - Do not merge historical into the realtime API client.
  - Do merge the duplicate historical archive entrypoints into one maintained historical downloader/selector path.
- Himawari:
  - Merge the download orchestration pattern, not necessarily every helper signature.
  - The target is one concurrency strategy that can serve both realtime and historical day batches.
- ERA5:
  - Keep one collector file with shared request policy.
  - Remove or parameterize historical-only pacing rather than splitting the file further.

### Himawari H3 Static Path Analysis

- Shared codepath:
  - `src/himawari_integrated_pipeline.py` invokes `src/data_processors/process_himawari_h3_streaming.py` for both historical and realtime when `--keep-originals` is not set.
  - The realtime branch only adds `realtime <hours>` CLI arguments before calling the same streaming processor.
  - Inside `process_himawari_h3_streaming.py`, both modes converge on the same `process_single_file_streaming(...)` function and the same sequential per-file loop.
- Remaining mode-specific divergence:
  - Historical uses `collect_netcdf_files(..., data_type="historical")`, which walks month/day directories in sorted order and skips whole dates when interpolated outputs already exist.
  - Realtime uses `collect_all_downloaded_netcdf_files(...)`, which gathers all downloaded `.nc` files, sorts them by parsed filename datetime, and skips whole dates when realtime interpolated outputs already exist.
  - This means file selection differs by mode, but the expensive raster/H3 work is shared.
- Static likely hotspots in shared H3 indexing:
  - `netcdf_to_tif_cache(...)` opens every NetCDF with xarray and writes a temporary GeoTIFF with rasterio for every file.
  - `mask(src, boundaries_countries.geometry, crop=True)` clips every temporary raster against the country boundary for every file.
  - `raster_to_dataframe(...)` performs the raster-to-H3 conversion per file and is the most likely CPU-heavy step in the loop.
  - The pipeline converts the H3 result from pandas to Polars before writing parquet, so there is an extra in-memory dataframe conversion on every file.
  - The main loop is explicitly sequential (`Processing {len(all_netcdf_files)} files sequentially...`), so no per-file H3 work is parallelized today.
- Static likely non-dominant costs:
  - Country boundary creation happens once per run, not once per file.
  - Historical vs realtime file enumeration differs, but that cost should be small relative to the per-file NetCDF/TIF/mask/H3 path now that the download-side month filtering has been reduced.
- Next measurement step:
  - Profile `process_single_file_streaming(...)` against one real Himawari NetCDF file to separate NetCDF read, TIF write, mask, raster-to-H3 conversion, pandas→Polars conversion, and parquet write time.

### Himawari H3 Single-File Profile Findings

- Focused profiling contract:
  - `tests/test_himawari_h3_single_file_profile.py` now downloads one representative historical Himawari file and compares the produced H3 parquet against a checked-in expected artifact.
  - Representative source: `2025-01-03 09:00` for `THA`.
- Measured timing breakdown from the green Docker run:
  - `download`: `3.643s`
  - `boundary_creation`: `4.338s`
  - `netcdf_to_tif`: `2.004s`
  - `mask`: `0.009s`
  - `raster_to_dataframe`: `0.122s`
  - `polars_conversion`: `0.009s`
  - `write_parquet`: `0.030s`
  - `total` per-file processing after setup/download: `2.185s`
- Interpretation:
  - The dominant repeatable cost inside the shared H3 loop is NetCDF-to-TIF conversion.
  - `raster_to_dataframe(...)` is not a leading bottleneck on the representative file and should be treated as a timed black box, not the first optimization target.
  - Boundary creation is slower than H3 conversion itself, but it is a one-time run cost rather than a per-file loop cost.

### Himawari H3 In-Memory Raster Optimization

- Optimization applied:
  - The shared streaming processor now stages the NetCDF raster in a rasterio `MemoryFile` instead of writing and reopening a temporary GeoTIFF on disk.
  - Rasterio-based masking and downstream H3 conversion are unchanged, so the semantic processing path stays aligned with the old implementation.
- Verification:
  - `./scripts/run_tests.sh -- tests/test_himawari_h3_single_file_profile.py -q -s`
  - Result: `2 passed, 2 warnings in 7.75s`
- Before/after representative-file timings:
  - `netcdf_to_tif`: `1.209s` -> `0.875s`
  - `processing_total`: `1.323s` -> `0.962s`
  - `full_total`: `7.132s` -> `6.974s`
- Output safety:
  - The representative-file contract still matched the checked-in expected artifact on schema, row count, sorted H3 keys, metadata columns, and `aod_value` payload.
- Conclusion:
  - The first safe H3 optimization win was eliminating temporary GeoTIFF disk I/O.
  - The next likely Himawari H3 target is boundary reuse/caching or multi-file orchestration rather than `raster_to_dataframe(...)`.

## Handoff

- Immediate next investigation slice: Himawari H3 indexing profiling on a single real NetCDF file.
- Focused execution plan completed: `plans/2026-03-09-himawari-shared-downloader-tdd-plan.md`
- After the H3 profiling slice, choose between reducing the NetCDF→TIF→mask→H3 conversion cost or parallelizing the per-file H3 processing loop before returning to OpenAQ historical consolidation and ERA5 historical pacing cleanup.
