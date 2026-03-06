# Full Test Suite Review Log (2026-03-06)

## Scope
- Run the entire Behave suite including `@slow` and `@live`.
- Audit whether tests validate real behavior versus superficial pass conditions.
- Inspect logs and generated artifacts, not just pass/fail counts.
- Propose concrete improvements, implement them, and rerun.

## Start Context
- Branch: `anthony/helpers`
- Starting commits:
  - `90efb4b` docs(tests): capture live quickstart anti-patterns and fixes
  - `0a08ece` test(behave): reset data artifacts and ignore tracked baselines
  - `326e2d6` test(behave): fail quickstart live runs on auth errors
- Known untracked files before run: `plans/`, `pretty.output`, `tests/test_quickstart_baseline_bdd.py`

## Execution Log
### 2026-03-06T00:00 (session local)
- Initialized review log.
- Next: run full Behave suite with Docker harness and wait for completion.
### 2026-03-06T16:xx
- Full suite launched via `./scripts/run_behave_tests.sh`.
- Docker image rebuild triggered automatically by harness.
- Build phase completed dependency verification (GDAL/eccodes/cfgrib).
### 2026-03-06T16:53 (in-progress)
- Contract features (`historical_argument_guards`, `readme_script_commands`) executed before quickstart feature.
- Quickstart `@live` auth-surface scenario started (`skip-firms --skip-era5 --skip-airgradient --skip-silver --skip-prediction`).
- Real-time run log confirms only `himawari` + `openaq` pipelines are active.
### 2026-03-06T16:54 (first full-harness run)
- Result: `4 features passed, 1 failed, 0 skipped`.
- Failure: `features/quickstart/basic_workflow.feature:25` (auth-surface scenario) due expected auth signatures in component logs.
- Observed auth evidence:
  - `openaq_realtime_*.log`: `Invalid credentials`
  - `himawari_aod_realtime_*.log`: `Login incorrect`
- Critical observation: `@slow @live` full workflow scenario in quickstart was skipped in this run.
- Next action: rerun with explicit tags to force inclusion of `@slow` scenarios and confirm true full-suite behavior.
### 2026-03-06T16:55 (tag override attempt)
- Attempted `--tags "@slow or not @slow"` to force all scenarios.
- Behave run skipped all scenarios (`0 scenarios passed, 32 skipped`).
- Conclusion: this expression was not interpreted as intended in current harness invocation.
- Next action: run default suite + explicit `--tags=@slow` execution to guarantee slow coverage.
### 2026-03-06T16:54 (explicit @slow run)
- Started explicit `--tags=@slow` run to force slow coverage.
- Full quickstart realtime scenario is executing end-to-end (`himawari`, `firms`, `era5`, `openaq`, `airgradient`).
- Early signal: OpenAQ marked successful quickly; long-running pipelines remain active.
### 2026-03-06T16:55 (during @slow)
- Current run logs already show auth failures in source-specific logs:
  - `openaq_realtime_20260306_165437.log`: HTTP 401 / Invalid credentials
  - `integrated_realtime_pipeline_20260306_165438.log`: FTP 530 Login incorrect
- Top-level orchestrator still marks OpenAQ/Himawari as successful, confirming the exact masking behavior under test.
### 2026-03-06T17:02 (still running)
- In explicit `@slow` run, `airgradient` remains active for an extended duration after other collectors complete.
- Orchestrator reports repeated `Still running: airgradient` with no incremental collector log detail.
- This behavior suggests a reliability gap for long-running live tests (potentially unbounded wait masked by a high timeout).
### 2026-03-06T17:06 (explicit @slow result)
- `@slow` run completed in ~12 minutes with 1 failing scenario (`features/quickstart/basic_workflow.feature:34`).
- Failure was at auth-log assertion, so downstream artifact assertions in that scenario did not execute (`None` in Behave output).
- Despite scenario failure, command itself completed full phases and wrote fresh artifacts:
  - `data/silver/realtime/silver_realtime_LAO_THA_20260306.parquet` (~104 MB)
  - `data/predictions/data/realtime/aq_predictions_20260306_LAO_THA.parquet` (~5.9 MB)
  - `data/predictions/map/realtime/aqi_map_20260306_LAO_THA.png` (~1.6 MB)
- Critical log finding: prediction phase logs a traceback/`ERROR` (`'NoneType' object has no attribute 'empty'`) while still reporting overall success.
- Interpretation: current test shape can short-circuit, and pipeline success semantics can mask real errors unless explicitly asserted.
