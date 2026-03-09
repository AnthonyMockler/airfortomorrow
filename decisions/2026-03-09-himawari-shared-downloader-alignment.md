# Decision: Himawari Shared Downloader Alignment

## Date
2026-03-09

## Decision
Refactor Himawari downloads around one shared downloader engine that serves both historical and realtime modes.

Keep the mode-specific discovery logic separate:
- historical: all hourly files for each day in a requested date range
- realtime: only the most recent hourly files needed for the requested lookback

Merge the parts that should behave the same:
- day-batch planning
- skip-rule evaluation
- FTP connection/retry handling
- threaded day-level execution
- download result accounting

Testing should be layered:
- targeted `pytest` for the downloader planner/executor and integrated command-building
- narrow live Behave coverage that exercises `src/data_collectors/himawari_aod.py --download-only`
- existing integrated historical Behave kept as the final workflow safety net, not the routine inner-loop test

## Why
- The current historical and realtime download functions perform the same essential work but duplicate skip logic, FTP path handling, and file transfer behavior.
- The realtime path already has the faster design pattern: day-batch planning plus optional threaded downloads using dedicated FTP connections.
- Historical still uses a sequential loop over day directories, which is the clearest missing reuse from the prior realtime work.
- The current integrated Python path only forwards `--download-workers` in realtime mode, so historical cannot benefit from concurrency even though the shell wrapper exposes the flag.
- Running the full Himawari integrated pipeline is too expensive for routine regression checks when the change is isolated to downloader behavior.

## Change Scope
- `src/data_collectors/himawari_aod.py`
  - Introduce shared day-batch/download-plan abstractions.
  - Share skip filtering and FTP batch execution across modes.
  - Preserve current output layout and mode-specific selection semantics.
- `src/himawari_integrated_pipeline.py`
  - Forward `--download-workers` for historical mode.
  - Extract command-building or equivalent seams so downloader invocation can be tested without a live run.
- Tests
  - Add targeted `pytest` coverage for the shared downloader logic.
  - Add downloader-only Behave contracts for realtime and historical collector entrypoints.

## Non-Goals
- No changes to H3 processing, daily aggregation, or IDW interpolation in this slice.
- No change to raw file layout under `data/raw/himawari/`.
- No change to the current skip precedence unless explicitly documented and tested.
- No requirement to run the whole Himawari integrated pipeline during routine development checks.
