# Feature Goal
Speed up ERA5 realtime collection by removing fixed AWS sleeps and replacing them with adaptive retry/backoff behavior that preserves external contract behavior and output correctness.

## Red
1. Extend `features/contracts/era5_realtime_contract.feature` with a realtime scenario assertion that the referenced run log does not contain fixed inter-request wait messaging (`"Waiting 10s before next request"`).
2. Add corresponding step definitions in `features/steps/era5_steps.py`.
3. Run targeted Behave command for ERA5 contract tags and confirm failure against current implementation.

## Green
1. Refactor AWS retrieval loop in `src/data_collectors/era5_meteorological_idw.py`:
   - Remove unconditional per-date fixed sleep.
   - Route retrieval through a single helper that classifies errors.
   - Retry only transient/rate-limit failures with bounded exponential backoff + jitter.
   - Respect explicit non-retry conditions (404/not available).
2. Keep output generation and file contracts unchanged.
3. Re-run targeted Behave ERA5 contract tests and ensure all pass.

## Regression Safety
- Keep existing CLI contract scenarios unchanged.
- Keep existing parquet schema/value checks unchanged.
- Preserve skip behavior for unavailable dates (404).
- Preserve max retry bounds to avoid unbounded runs.

## Success Criteria
- New no-fixed-wait scenario passes.
- Existing ERA5 contract scenarios pass unchanged.
- Live benchmark run remains functionally correct (fresh parquet + required columns/values).
- Before/after timing evidence shows reduced runtime for equivalent live scenario.

## Evidence to Capture
- RED command + failure signal.
- GREEN command + pass summary.
- Before/after benchmark durations from ERA5 run output/logs.
- Brief attribution of time deltas tied to fixed-wait removal.

## Evidence Captured
- RED:
  - Command: `./scripts/run_behave_tests.sh --inside --tags=@era5 --tags=@contract --tags=@live --tags=@benchmark`
  - Signal: `Failing scenarios: features/contracts/era5_realtime_contract.feature:16`
  - Summary: `0 scenarios passed, 1 failed`
  - Runtime: `Took 1m54.601s`
- GREEN:
  - Command: `./scripts/run_behave_tests.sh --inside --tags=@era5 --tags=@contract --tags=@live --tags=@benchmark`
  - Summary: `1 feature passed, 1 scenario passed, 13 steps passed, 0 failed`
  - Runtime: `Took 0m55.665s`
- Runtime delta:
  - Absolute improvement: `58.936s` faster
  - Relative improvement: `~51.4%` faster
- Log evidence (latest green run):
  - `data/logs/era5_integrated_idw_20260307_041618.log` contains `Total duration: 0:00:51.022635`
  - No occurrences of `Waiting 10s before next request to avoid rate limiting...`
