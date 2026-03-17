# TESTS KNOWLEDGE BASE

**Generated:** 2026-03-06
**Updated:** 2026-03-16

## OVERVIEW
Repository tests use **Behave BDD** as the preferred style for workflow and contract coverage, executed inside Docker for dependency parity.

## STYLE RULES
- Write tests as Gherkin features under `features/` with clear Given/When/Then intent.
- Keep step definitions in `features/steps/` small and reusable.
- Prefer command-level contract checks and atomic workflow checks over monolithic end-to-end scenarios.
- Tag scenarios consistently:
  - `@tier_a`: local/fast, must not use `@live` or `@slow`
  - `@tier_b`: live non-slow, must include `@live` and must not include `@slow`
  - `@tier_c`: slow, must include `@slow`
  - `@smoke`: fast runtime/environment checks
  - `@contract`: CLI/help/argument behavior
  - `@static_assets`: fast loader-compatibility checks for bootstrap parquet/CSV assets
  - `@quickstart`: README setup/workflow coverage
  - `@slow`: long-running scenarios
  - `@live`: scenarios that require external APIs/network conditions

## EXECUTION RULES
- Run BDD tests through Docker:
  - `./scripts/run_behave_tests_compact.sh --tier a` for routine agent-driven runs
  - `./scripts/run_behave_tests_compact.sh --tier b` for live non-slow runs
  - `./scripts/run_behave_tests_compact.sh --tier c` for slow runs
  - `./scripts/run_behave_tests_compact.sh --tier all` for full ordered suite
  - `./scripts/run_behave_tests.sh` only when full raw output is explicitly needed or when debugging the compact wrapper
- Use `./scripts/validate_static_assets.sh` or `./scripts/run_behave_tests_compact.sh --tier a --scope static_assets` for regular static-asset format checks.
- Avoid host execution unless debugging locally with explicit opt-in.
- Tier runs should not use ad-hoc tag forwarding.
- For performance, soak, load, `@slow`, or other runs expected to exceed 10 minutes, start the command once, record the log path, and avoid polling, tailing, or status updates more often than every 5 to 10 minutes unless the run exits, fails, materially changes state, or the user asked for tighter updates.
- When a Behave run is expected to be long, prefer `./scripts/run_behave_tests_compact.sh --tier c --long-run`. Tier C auto-enables the same guidance.

## AUTHORING GUIDELINES
- Keep scenarios atomic so failures isolate to one workflow responsibility.
- Validate observable outcomes (exit code, output text, file artifacts).
- Reuse shared command-running helpers from `features/environment.py` instead of custom subprocess logic per step file.
- Use scenario outlines for repeated contract checks (for example, script help coverage).

## SESSION LEARNINGS (2026-03-06)
### What Went Wrong
- Live quickstart scenarios could pass on stale files left in `data/` from previous runs.
- Assertions that only checked `command should succeed` were too weak; wrapper scripts can return `0` even when child collectors logged auth failures.
- File-existence checks could be satisfied by baseline files that are intentionally committed to the repo.
- Step definitions that depend on `git` binaries are brittle inside Docker test images (not guaranteed installed).

### Anti-Patterns (Do Not Use)
- `Then the command should succeed` as the only success criterion for `@live` scenarios.
- `directory should contain files` checks in mutable `data/` paths without run isolation.
- Counting artifacts in directories that include tracked baseline fixtures.
- Using `git ls-files` inside Behave steps to decide what to delete/count.

### Correct Pattern
- Before live workflow runs, clean `data/` and preserve only known baseline tracked fixtures:
  - `data/training/silver_dataset.parquet`
  - `data/raw/firms/historical/*`
- For output assertions in mutable paths, require **untracked/new** artifacts, not generic existence.
- Capture logs created by the current command and fail scenario on auth/credential signatures (for example `HTTP 401`, `Invalid credentials`, `Login incorrect`, `NotAuthorized`).
- Keep a focused live scenario for quick failure detection (OpenAQ/Himawari auth checks) and a separate `@slow` full workflow scenario for comprehensive coverage.
