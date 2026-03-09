# Plan: Himawari Shared Downloader

- Status: Complete
- Owner: Codex
- Active Agent: Codex (GPT-5)
- Started: 2026-03-09
- Last Updated: 2026-03-09
- Scope Note: Replace the duplicated Himawari historical/realtime downloader implementations with one shared engine, and protect the change with downloader-only tests rather than full-pipeline runs.

## Feature Goal

Create a fast Himawari downloader that serves both historical and realtime codepaths while preserving current file layout, skip semantics, and CLI behavior.

## Scope Guardrails

- Keep separate discovery semantics for historical date ranges and realtime lookback windows.
- Preserve the raw download directory layout: `data/raw/himawari/YYYYMM/DD/*.nc`.
- Preserve current skip precedence unless a later decision explicitly changes it:
  - interpolated day output skip first
  - H3-file skip next
  - existing raw-file skip last
  - `--force-download` only bypasses the existing raw-file skip
- Parallelize at the day-batch level with dedicated FTP connections, not file-level fanout.
- Do not widen this slice into H3 processing, aggregation, or interpolation changes.

## Red

1. Add a focused `pytest` module for the downloader seam and capture the initial RED failure.
2. Add a downloader-only Behave contract for historical and realtime collector entrypoints and capture RED for the missing assertions/helpers.
3. Add a targeted test for historical `--download-workers` passthrough in the integrated Python path and capture RED.

## Green

1. Introduce a shared internal batch model.
   - One batch represents one day directory and the specific hourly files to download from it.
   - Historical batches usually contain all hourly files for a day.
   - Realtime batches may contain only a subset of hours from a day.
2. Extract a shared planner.
   - Input: candidate day batches plus skip settings.
   - Output: normalized download plan plus skip accounting.
3. Extract a shared executor.
   - Sequential mode: reuse one FTP session when workers=`1`.
   - Concurrent mode: use bounded day-level workers with one FTP connection per worker batch.
4. Keep public wrappers stable.
   - `download_historical_files(...)` remains as a thin adapter that returns count-style results.
   - `download_realtime_files(...)` remains as a thin adapter that returns file-list results.
5. Fix the integrated pipeline passthrough gap.
   - Historical mode must forward `--download-workers` to `src/data_collectors/himawari_aod.py`.
6. Re-run the targeted downloader tests until green.

## Regression Safety

- Fast inner-loop checks:
  - `./scripts/run_tests.sh -- tests/test_himawari_downloader.py -q`
- Downloader-only acceptance checks:
  - `./scripts/run_behave_tests_compact.sh -- features/contracts/himawari_downloader_contract.feature`
- Existing workflow safety net:
  - Re-run the bounded historical Himawari scenario from `features/contracts/historical_collection_contract.feature`
- Only run the existing full realtime integrated Himawari contract if the shared downloader change appears to affect behavior beyond download planning/execution.

## Success Criteria

- Both historical and realtime download paths use one shared planner/executor implementation.
- Historical mode can use `--download-workers` through the integrated Python path.
- The downloader-specific tests validate behavior without requiring whole-pipeline runs.
- Live downloader acceptance remains bounded to collector-only `--download-only` commands.
- The existing historical integrated Himawari contract still passes after the refactor.

## Evidence to Capture

- RED and GREEN results for `tests/test_himawari_downloader.py`
- RED and GREEN results for `features/contracts/himawari_downloader_contract.feature`
- Before/after timings for:
  - historical downloader-only bounded slice
  - realtime downloader-only bounded slice
  - existing bounded historical integrated Himawari slice
- Notes on whether downloader-only speedup materially reduces the full historical integrated runtime

## Evidence Log

- RED: targeted pytest
  - Command:
    - `./scripts/run_tests.sh -- tests/test_himawari_downloader.py -q`
  - Result:
    - Failed during collection as expected.
    - Core signal:
      - `ImportError: cannot import name 'HIMAWARI_FTP_BASE_DIR' from 'src.data_collectors.himawari_aod'`
- RED: downloader-only Behave
  - Command:
    - `./scripts/run_behave_tests_compact.sh features/contracts/himawari_downloader_contract.feature`
  - Result:
    - Failed as expected with missing downloader-specific steps.
    - Summary:
      - `1 scenario passed, 2 failed`
      - `6 undefined`
      - `Took 2m18.012s`
- GREEN: targeted pytest after shared downloader extraction
  - Command:
    - `./scripts/run_tests.sh -- tests/test_himawari_downloader.py -q`
  - Result:
    - Passed.
    - Summary:
      - `8 passed in 3.50s`
- GREEN: downloader-only Behave after shared downloader + month-range filtering
  - Command:
    - `./scripts/run_behave_tests_compact.sh features/contracts/himawari_downloader_contract.feature`
  - Result:
    - Passed.
    - Summary:
      - `1 feature passed`
      - `3 scenarios passed`
      - `19 steps passed`
      - `Took 1m13.340s`
- Workflow safety: bounded historical Himawari integrated scenario
  - Command:
    - `./scripts/run_behave_tests_compact.sh --tags=@slow features/contracts/historical_collection_contract.feature:50`
  - Result:
    - Passed.
    - Summary:
      - `1 feature passed`
      - `1 scenario passed`
      - `28 steps passed`
      - `Took 29m40.319s`

## Planned Test Coverage

### Targeted Pytest Coverage

- `tests/test_himawari_downloader.py`
  - plan marks a whole day as skipped when interpolated output already exists
  - plan skips only specific files when H3 output already exists for those files
  - plan skips existing raw `.nc` files unless `force_download=True`
  - `force_download=True` does not override the interpolated-output day skip
  - historical adapter preserves count-style return shape
  - realtime adapter preserves file-list return shape
  - concurrent executor opens one FTP connection per worker batch instead of sharing one mutable connection
  - sequential executor resets FTP location correctly between day batches
  - integrated pipeline historical mode includes `--download-workers` when building the collector command

Implementation note:
- If the current code is too monolithic to test directly, first extract small pure helpers such as:
  - `build_download_batches(...)`
  - `build_download_plan(...)`
  - `execute_download_plan(...)`
  - `build_himawari_download_command(...)`

### Narrow Behave Coverage

- `features/contracts/himawari_downloader_contract.feature`
  - Scenario: historical downloader-only run creates fresh raw `.nc` files for a bounded 1-2 day range
  - Scenario: realtime downloader-only run creates fresh raw `.nc` files for a bounded recent-hours slice

Assertions should be limited to downloader responsibilities:
- command succeeds
- command output references a log file
- current run updates raw Himawari `.nc` files under the expected day directories
- at least one updated file is non-empty
- requested mode/date or recent-hours selection produces files in the expected month/day directory structure

This feature should not assert H3, daily aggregation, or interpolation outputs.

## Implementation Slices

1. Extract shared internal downloader helpers without changing public callers.
2. Add targeted pytest coverage against the new helpers and integrated command-building seam.
3. Switch `download_realtime_files(...)` to the shared engine and prove behavior is unchanged.
4. Switch `download_historical_files(...)` to the shared engine and enable worker support.
5. Pass `--download-workers` through historical integrated invocation.
6. Add or update downloader-only Behave coverage.
7. Re-run the existing bounded historical Himawari integrated scenario for final workflow verification.

## Notes and Findings

- From first principles, both current download functions solve the same transport problem:
  - accept candidate remote files
  - skip already-satisfied work
  - download remaining files into the same local tree
  - report what happened
- The real semantic split is upstream of download execution:
  - historical chooses whole days in a date range
  - realtime chooses only the latest required hour files
- The main implementation differences today are:
  - historical uses a sequential day loop on one FTP connection
  - realtime supports day-level threaded downloads with reconnect-per-batch
  - historical returns counts while realtime returns per-file lists
- The safest refactor is shared internals plus stable public wrappers, not an API-level collapse of the current call sites.
- Additional finding during implementation:
  - Historical discovery was still enumerating every month on the FTP server before filtering to the requested range.
  - A new `filter_month_directories_for_range(...)` helper now limits historical month inspection to the requested month window.
- Measured outcome:
  - The narrowed downloader-only Behave feature improved from `3m2.754s` before the month-range filter to `1m13.340s` after it.
  - The full bounded historical integrated Himawari scenario still passed but did not show a stable end-to-end speedup in this run. The latest verification took `29m40.319s`, which is slower than the earlier `17m2.378s` baseline recorded before this slice.
  - Inference:
    - The shared downloader refactor and month filtering reduced downloader-layer overhead, but end-to-end historical runtime remains dominated by variable downstream and network costs, so a separate benchmark pass is still needed before claiming full-pipeline speed gains.

## Handoff

- Delivered:
  - shared downloader planner/executor in `src/data_collectors/himawari_aod.py`
  - historical `--download-workers` passthrough in `src/himawari_integrated_pipeline.py`
  - downloader-only Behave coverage in `features/contracts/himawari_downloader_contract.feature`
  - targeted pytest coverage in `tests/test_himawari_downloader.py`
- Recommended next step:
  - isolate the downstream historical Himawari phases after download, because the downloader layer is now testable and faster in isolation, but the integrated historical runtime is still too noisy to attribute improvement confidently.
