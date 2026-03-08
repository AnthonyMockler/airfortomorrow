# Plan: OpenAQ Live 10%-Sample Benchmark Scenario (BDD Red/Green)

## Status
Closed on 2026-03-08 by maintainer decision. Scope considered sufficiently complete.

## Feature Goal
Create a realistic, repeatable live OpenAQ realtime scenario that samples one tenth of the current live location list so optimization changes can be measured quickly.

## Red
1. Add a new `@openaq @live` scenario that:
- Computes a dynamic sample limit from live OpenAQ location count.
- Runs OpenAQ realtime collection with that computed limit.
- Asserts that reported outputs and parquet data are usable.
2. Run targeted Docker Behave command for only this scenario and confirm failure due to undefined steps.
3. Record command and failure signal.

## Green
1. Implement minimal OpenAQ-specific Behave steps to:
- Discover live baseline location/sensor counts.
- Compute `ceil(total_locations / 10)` sample limit with a safety minimum.
- Execute collection with computed limit.
- Assert runtime and output/parquet contract signals.
2. Re-run targeted Docker Behave command until green.

## Regression Safety
1. Keep scenario `@live` so it remains opt-in and does not affect default fast suite.
2. Use bounded timeout and sampled workload to prevent full-run cost.
3. Re-run existing non-live OpenAQ contract slice to ensure no regression in prior test coverage.

## Success Criteria
- Scenario uses live baseline size and computed one-tenth sample limit.
- OpenAQ run succeeds within scenario timeout.
- OpenAQ parquet output is non-empty and schema-valid.
- Runtime signal is large enough to be optimization-sensitive.

## Evidence to Capture
- Red run command and undefined-step failure signal.
- Green run command and pass summary.
- Baseline location/sensor counts and computed sample limit from the test run.
- Runtime reported by collector output.

## Execution Evidence (2026-03-07)
### Red
- Command:
  - `./scripts/run_behave_tests.sh -- --tags='~@__never__' --tags=@openaq --tags=@benchmark`
- Core failure signal:
  - Benchmark scenario failed with 5 undefined steps for live baseline sizing, computed-limit execution, and benchmark assertions.

### Green
- Command:
  - `./scripts/run_behave_tests.sh -- --tags='~@__never__' --tags=@openaq --tags=@benchmark`
- Result:
  - `1 feature passed, 0 failed, 7 skipped`
  - `1 scenario passed, 0 failed, 37 skipped`
  - `12 steps passed, 0 failed, 142 skipped, 0 undefined`
  - Runtime: `2m30.512s`

### Regression Safety Recheck
- Command:
  - `./scripts/run_behave_tests.sh -- --tags=@openaq --tags=~@live`
- Result:
  - `1 feature passed, 0 failed, 7 skipped`
  - `2 scenarios passed, 0 failed, 36 skipped`
  - `6 steps passed, 0 failed, 148 skipped, 0 undefined`

### Captured Benchmark Metrics
- Source log: `logs/openaq_realtime_20260307_024300.log`
- Baseline live locations: `738`
- Computed one-tenth sample limit: `74`
- Sensors extracted for sampled run: `74`
- Successful sensors with data: `61`
- Collected data points: `1335`
- Reported OpenAQ collection duration: `142.98 seconds`
