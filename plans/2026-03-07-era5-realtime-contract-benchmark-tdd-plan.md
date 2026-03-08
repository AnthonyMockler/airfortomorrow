> Status: Completed and verified on 2026-03-08. The planned ERA5 benchmark test already exists in `features/contracts/era5_realtime_contract.feature` with supporting steps in `features/steps/era5_steps.py`.

# Plan: ERA5 Realtime Contract + Small Real Benchmark (BDD Red/Green)

## Feature Goal
Create an ERA5-only realtime Behave scenario that is small enough for iterative optimization but still uses live data and validates useful output artifacts for downstream pipeline stages.

## Baseline Context
- User report snapshot shows completed collectors around:
  - FIRMS `~95s`
  - Himawari `~206s`
  - AirGradient `~532s`
  - ERA5 `~680s`
- OpenAQ was in progress during that snapshot; after OpenAQ optimization, ERA5 is the next slowdown target.

## Test Profile (Small but Real)
- Command profile target:
  - `./scripts/run_era5_idw_pipeline.sh --mode realtime --hours 24 --countries THA --params 2t --idw-rings 8 --idw-weight-power 1.5 --force --timeout 2400`
- Rationale:
  - `--countries THA` reduces spatial scope while staying real.
  - `--params 2t` reduces variable breadth while keeping meteorological signal.
  - `--force` ensures fresh artifacts from current run.
  - Explicit IDW parameters keep run bounded and deterministic for benchmark use.

## Red
1. Add ERA5 feature scenarios first in `features/contracts/era5_realtime_contract.feature`:
- ERA5 shell wrapper CLI options contract.
- ERA5 Python entrypoint CLI options contract.
- ERA5-only realtime run with fresh output and data-shape assertions.
2. Run smallest targeted Docker Behave command and confirm expected failure signal before adding step definitions:
- `./scripts/run_behave_tests.sh -- --tags=@era5 --tags=@contract`
3. Record failing command output (undefined step or assertion gap) as RED evidence.

## Green
1. Implement minimal ERA5-specific step definitions in `features/steps/era5_steps.py`:
- Select latest updated ERA5 realtime parquet from current command outputs.
- Assert minimum rows, required columns, non-null key fields, numeric meteorological values, and minimum distinct H3 cells.
2. Re-run the targeted ERA5 command set until green:
- `./scripts/run_behave_tests.sh -- --tags=@era5 --tags=@contract`
3. Keep runtime bounded to ERA5-only scenarios during this cycle.

## Regression Safety
1. Re-run existing OpenAQ contract slice to ensure no collateral BDD breakage:
- `./scripts/run_behave_tests.sh -- --tags=@openaq --tags=~@live`
2. Confirm ERA5 scenario checks fresh files from `updated_data_files`, not pre-existing cached artifacts.
3. Verify log-file reference step still works for ERA5 pipeline wrapper output.

## Success Criteria
- New ERA5 contract scenarios pass in Docker.
- ERA5 realtime scenario produces at least one updated realtime parquet in:
  - `data/processed/era5/daily_aggregated/realtime`
- Generated parquet is non-empty and has expected structural contract:
  - includes `h3_08` and `date`,
  - contains at least one numeric meteorological column with non-null values,
  - has multiple unique H3 cells.
- Test profile is realistic enough to serve as optimization baseline.

## Evidence to Capture
- RED command + failure signal.
- GREEN command + pass summary.
- Path to generated ERA5 realtime parquet(s).
- Extracted row/column/uniqueness checks from scenario assertions.
- Follow-up performance-analysis notes identifying current bottlenecks and proposed fix plan.

## Evidence Log
- RED:
  - Command:
    - `./scripts/run_behave_tests.sh -- --tags=@era5 --tags=@contract`
  - Result:
    - Failed as expected with undefined ERA5 steps.
    - Summary: `0 scenarios passed, 3 failed, 34 skipped`, `9 undefined`, `Took 1m58.816s`.
    - Core signal: missing ERA5-specific output/assertion steps in `features/steps/era5_steps.py`.
- GREEN:
  - Command:
    - `./scripts/run_behave_tests.sh -- --tags=@era5 --tags=@contract`
  - Result:
    - Passed after step implementation.
    - Summary: `3 scenarios passed, 0 failed, 34 skipped`, `18 steps passed, 0 undefined`, `Took 1m55.826s`.
- Live scenario runtime and artifact evidence:
  - ERA5 command step runtime: `~112.849s`.
  - Latest validated output artifact:
    - `data/processed/era5/daily_aggregated/realtime/era5_daily_mean_2026-03-07_THA.parquet`
  - Data checks from generated parquet:
    - rows: `595,995`
    - columns: `h3_08`, `2t`, `date`
    - unique `h3_08`: `595,995`
    - nulls: `h3_08=0`, `date=0`
