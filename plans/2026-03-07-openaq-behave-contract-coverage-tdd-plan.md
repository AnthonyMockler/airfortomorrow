# Plan: OpenAQ Behave Contract Coverage (BDD Red/Green)

## Status
Closed on 2026-03-08 by maintainer decision. Scope considered sufficiently complete.

## Feature Goal
Create OpenAQ-focused Behave coverage that locks down current CLI contracts and validates that OpenAQ realtime outputs are usable, correctly formatted inputs for downstream modules.

## Red
1. Add OpenAQ feature scenarios first:
- CLI contract checks for OpenAQ entrypoints and key switches.
- OpenAQ-only realtime invocation via pipeline wrapper.
- Output data contract checks for OpenAQ realtime parquet.
2. Run smallest targeted Docker Behave command for OpenAQ scenarios and confirm expected failure before step implementation.
3. Record failing command and core failure signal.

## Green
1. Implement only required Behave step definitions for OpenAQ:
- Locate OpenAQ parquet files updated by current command.
- Validate required columns and minimum row count.
- Validate non-null key fields and numeric measurement values.
2. Re-run OpenAQ-targeted Docker Behave scenarios until green.

## Regression Safety
1. Keep OpenAQ scenarios bounded with test-mode switches.
2. Avoid modifying shared generic steps unless required.
3. Re-run OpenAQ tag group end-to-end in Docker after step implementation.

## Success Criteria
- OpenAQ CLI contract scenarios pass and detect required option surfaces.
- OpenAQ-only pipeline invocation scenario passes with documented switches.
- OpenAQ realtime parquet assertions pass for schema and basic data quality.
- Tests run through `./scripts/run_behave_tests.sh` (Docker harness), not host Python.

## Evidence to Capture
- Red command and failing signal.
- Green command(s) and passing output.
- Paths of generated OpenAQ parquet validated by scenarios.
- Any residual risk (for example credential-dependent `@live` behavior).

## Execution Evidence (2026-03-07)
### Red
- Command:
  - `./scripts/run_behave_tests.sh -- --tags=@openaq --tags=~@live`
- Core failing signal:
  - 2 undefined steps for OpenAQ feature:
    - `the command output should include CLI options "--days,--timeout,--limit,--test-mode,--help"`
    - `the command output should include CLI options "--days,--locations,--limit,--output,--test-mode,--test-limit"`

### Green
- Command:
  - `./scripts/run_behave_tests.sh -- --tags=@openaq --tags=~@live`
- Result:
  - `1 feature passed, 0 failed, 7 skipped`
  - `2 scenarios passed, 0 failed, 35 skipped`
  - `6 steps passed, 0 failed, 136 skipped, 0 undefined`
- Command:
  - `./scripts/run_behave_tests.sh -- --tags='~@__never__' --tags=@openaq --tags=@live`
- Result:
  - `1 feature passed, 0 failed, 7 skipped`
  - `1 scenario passed, 0 failed, 36 skipped`
  - `12 steps passed, 0 failed, 130 skipped, 0 undefined`
