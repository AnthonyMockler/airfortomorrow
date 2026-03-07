# Plan: Realtime Validate-Sensors Guard (BDD Red/Green)

## Feature Goal
Prevent invalid realtime sensor-validation usage by failing fast with a clear error when `--mode realtime` and `--validate-sensors` are combined.

## TDD Approach
1. Red
- Add Behave contract scenario(s) that expect failure and explicit error text for invalid realtime validation flag usage.
- Run targeted Behave command and confirm failure before implementation.

2. Green
- Implement validation guard in prediction CLI path.
- Update wrapper behavior so realtime complete-pipeline execution does not pass validation flags implicitly.
- Run targeted Behave scenarios until green.

3. Regression Safety
- Re-run focused regression scenario that isolates prediction map generation failure behavior.
- Re-run relevant quick contract checks for argument handling.

## Success Criteria
- `./scripts/predict_air_quality.sh --mode realtime ... --validate-sensors` fails immediately.
- Error message clearly states validate-sensors is not valid for realtime mode.
- Behave contract test(s) for this rule pass.
- No slow full-pipeline rerun required for this feature.

## Evidence to Capture
- Behave command used for red run and failing output.
- Behave command used for green run and passing output.
- Commit(s) containing tests and implementation.
